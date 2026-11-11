import asyncio
import json
import os
from dataclasses import dataclass, replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4

import pytest
import aio_pika
from fastapi.testclient import TestClient
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.modules.catalog.infrastructure.models import AvailabilitySlotRecord, ServiceRecord
from app.modules.catalog.public import build_catalog_reader
from app.modules.conversations.public import (
    DeliverAppointmentConfirmation,
    build_confirmation_outbox,
    build_confirmation_queue,
)
from app.modules.conversations.infrastructure.models import AppointmentConfirmationRecord
from app.modules.conversations.infrastructure.rabbitmq_confirmation_queue import QUEUE_NAME
from app.main import create_app
from app.modules.payments.application.create_checkout import CreateCheckout
from app.modules.payments.application.process_payment_webhook import ProcessPaymentWebhook
from app.modules.payments.domain.payment import PaymentCheckout, PaymentStatus, ProviderPayment
from app.modules.payments.infrastructure.models import PaymentCheckoutRecord, PaymentRecord
from app.modules.payments.infrastructure.sqlalchemy_payment_store import SqlAlchemyPaymentStore
from app.modules.reservations.domain.appointment import Appointment, AppointmentStatus
from app.modules.reservations.application.booking_service import BookingService
from app.modules.reservations.application.create_pending_appointment import CreatePendingAppointment
from app.modules.reservations.infrastructure.models import AppointmentRecord, CustomerRecord
from app.modules.reservations.infrastructure.sqlalchemy_reservation_store import (
    SlotUnavailable,
    SqlAlchemyReservationStore,
)
from app.shared.database import Base, SqlAlchemyTransactionManager, create_session_factory


@dataclass(frozen=True, slots=True)
class PostgresDatabase:
    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]


class FakeCheckoutProvider:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.request: dict[str, object] | None = None

    async def create_checkout(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> tuple[str, str]:
        self.request = {
            "appointment_id": appointment_id,
            "tenant_id": tenant_id,
            "title": title,
            "amount": amount,
            "currency": currency,
        }
        if self.fail:
            raise RuntimeError("Provider unavailable")
        return "preference-created", "https://www.mercadopago.com.co/checkout/redirect"


class ApprovedPaymentProvider:
    def __init__(self, payment: ProviderPayment) -> None:
        self.payment = payment

    async def get_payment(self, payment_id: str) -> ProviderPayment:
        assert payment_id == self.payment.payment_id
        return self.payment


class ValidSignature:
    def verify(self, **_: str | None) -> bool:
        return True


class RecordingConfirmationPublisher:
    def __init__(self) -> None:
        self.published: list[tuple[str, str]] = []

    async def publish_confirmation(self, *, tenant_id: str, appointment_id: str) -> None:
        self.published.append((tenant_id, appointment_id))


@pytest.fixture
def postgres_database() -> PostgresDatabase:
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to run PostgreSQL integration tests")

    schema = f"h001_test_{uuid4().hex}"
    admin_engine = create_async_engine(database_url, poolclass=NullPool)

    async def create_schema() -> AsyncEngine:
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'CREATE SCHEMA "{schema}"'))
        engine = create_async_engine(
            database_url,
            poolclass=NullPool,
            connect_args={"server_settings": {"search_path": schema}},
        )
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        return engine

    engine = asyncio.run(create_schema())
    sessions = create_session_factory(engine)
    yield PostgresDatabase(engine=engine, sessions=sessions)

    async def drop_schema() -> None:
        await engine.dispose()
        async with admin_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))
        await admin_engine.dispose()

    asyncio.run(drop_schema())


def seed_slot(sessions: async_sessionmaker[AsyncSession]) -> tuple[str, str, str]:
    tenant_id = "tenant-1"
    service_id = str(uuid4())
    slot_id = str(uuid4())
    starts_at = datetime.now(timezone.utc) + timedelta(days=1)

    async def seed() -> None:
        async with sessions() as session, session.begin():
            session.add(
                ServiceRecord(
                    id=service_id,
                    tenant_id=tenant_id,
                    name="Cambio de aceite",
                    duration_minutes=60,
                    deposit_amount=Decimal("25000.00"),
                    currency="COP",
                    active=True,
                )
            )
            await session.flush()
            session.add(
                AvailabilitySlotRecord(
                    id=slot_id,
                    tenant_id=tenant_id,
                    service_id=service_id,
                    starts_at=starts_at,
                    ends_at=starts_at + timedelta(hours=1),
                    active=True,
                )
            )

    asyncio.run(seed())
    return tenant_id, service_id, slot_id


def appointment_for(
    sessions: async_sessionmaker[AsyncSession],
    tenant_id: str,
    service_id: str,
    slot_id: str,
) -> Appointment:
    async def get_slot_times() -> tuple[datetime, datetime]:
        async with sessions() as session:
            slot = await session.scalar(
                select(AvailabilitySlotRecord).where(AvailabilitySlotRecord.id == slot_id)
            )
            assert slot is not None
            return slot.starts_at, slot.ends_at

    starts_at, ends_at = asyncio.run(get_slot_times())
    return Appointment(
        id=str(uuid4()),
        tenant_id=tenant_id,
        customer_id=str(uuid4()),
        service_id=service_id,
        availability_id=slot_id,
        starts_at=starts_at,
        ends_at=ends_at,
    )


def test_postgres_reservation_is_atomic_and_rejects_cross_tenant_slot(
    postgres_database: PostgresDatabase,
) -> None:
    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    store = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    appointment = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )

    async def reserve_twice() -> list[str]:
        async def reserve(name: str) -> str:
            candidate = replace(
                appointment,
                id=str(uuid4()),
                customer_id=str(uuid4()),
            )
            try:
                await store.create_customer_and_reserve(
                    candidate,
                    customer_name=name,
                    customer_phone=f"+57300{uuid4().int % 10**7:07d}",
                )
                return "reserved"
            except SlotUnavailable:
                return "unavailable"

        return await asyncio.gather(reserve("Ana"), reserve("Luis"))

    outcomes = asyncio.run(reserve_twice())
    assert sorted(outcomes) == ["reserved", "unavailable"]

    _, owner_service_id, owner_slot_id = seed_slot(postgres_database.sessions)
    wrong_tenant = replace(
        appointment_for(
            postgres_database.sessions, "tenant-evil", owner_service_id, owner_slot_id
        ),
        id=str(uuid4()),
    )

    async def reserve_other_tenant() -> None:
        await store.create_customer_and_reserve(
            wrong_tenant,
            customer_name="Eve",
            customer_phone="+573009999999",
        )

    with pytest.raises(SlotUnavailable):
        asyncio.run(reserve_other_tenant())

    async def counts() -> tuple[int, int]:
        async with postgres_database.sessions() as session:
            appointments = await session.scalar(select(func.count()).select_from(AppointmentRecord))
            evil_customers = await session.scalar(
                select(func.count()).select_from(CustomerRecord).where(
                    CustomerRecord.tenant_id == "tenant-evil"
                )
            )
            return appointments or 0, evil_customers or 0

    assert asyncio.run(counts()) == (1, 0)


def test_postgres_duplicate_approved_webhook_records_once_and_confirms(
    postgres_database: PostgresDatabase,
) -> None:
    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    reservations = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    publisher = RecordingConfirmationPublisher()
    payments = SqlAlchemyPaymentStore(postgres_database.sessions)
    appointment = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )

    async def setup() -> None:
        await reservations.create_customer_and_reserve(
            appointment,
            customer_name="Ana",
            customer_phone="+573001112233",
        )
        await payments.save_checkout_if_absent(
            PaymentCheckout(
                appointment_id=appointment.id,
                tenant_id=tenant_id,
                preference_id="preference-1",
                checkout_url="https://www.mercadopago.com.co/checkout/redirect",
                amount=Decimal("25000.00"),
                currency="COP",
            )
        )
        payment = ProviderPayment(
            payment_id="payment-1",
            external_reference=appointment.id,
            status=PaymentStatus.APPROVED,
            amount=Decimal("25000.00"),
            currency="COP",
        )
        webhook = ProcessPaymentWebhook(
            provider=ApprovedPaymentProvider(payment),
            store=payments,
            appointment_confirmer=reservations,
            confirmation_outbox=build_confirmation_outbox(postgres_database.sessions),
            confirmation_publisher=publisher,
            signature_verifier=ValidSignature(),
            transaction_manager=SqlAlchemyTransactionManager(
                postgres_database.sessions
            ),
        )

        async def process() -> bool:
            return await webhook.execute(
                signature_header="signed",
                request_id="request-1",
                payment_id=payment.payment_id,
            )

        assert await asyncio.gather(process(), process()) == [True, True]

    asyncio.run(setup())

    async def persisted_state() -> tuple[int, int, int, str, tuple[str, str, str] | None]:
        async with postgres_database.sessions() as session:
            payment_count = await session.scalar(select(func.count()).select_from(PaymentRecord))
            appointment_count = await session.scalar(
                select(func.count()).select_from(AppointmentRecord)
            )
            confirmation_count = await session.scalar(
                select(func.count()).select_from(AppointmentConfirmationRecord)
            )
            appointment_status = await session.scalar(
                select(AppointmentRecord.status).where(AppointmentRecord.id == appointment.id)
            )
            confirmation = await session.scalar(
                select(AppointmentConfirmationRecord).where(
                    AppointmentConfirmationRecord.appointment_id == appointment.id,
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                )
            )
            return (
                payment_count or 0,
                appointment_count or 0,
                confirmation_count or 0,
                appointment_status or "",
                (
                    confirmation.recipient_phone,
                    confirmation.message,
                    confirmation.status,
                )
                if confirmation
                else None,
            )

    assert asyncio.run(persisted_state()) == (
        1,
        1,
        1,
        AppointmentStatus.CONFIRMED.value,
        (
            "+573001112233",
            "Hola Ana, tu cita de Cambio de aceite quedó confirmada para el "
            f"{appointment.starts_at.strftime('%d/%m/%Y a las %H:%M')}.",
            "queued",
        ),
    )
    assert publisher.published == [
        (tenant_id, appointment.id),
        (tenant_id, appointment.id),
    ]


def test_webhook_failure_rolls_back_payment_and_appointment_together(
    postgres_database: PostgresDatabase,
) -> None:
    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    reservations = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    payments = SqlAlchemyPaymentStore(postgres_database.sessions)
    appointment = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )

    async def setup() -> None:
        await reservations.create_customer_and_reserve(
            appointment,
            customer_name="Ana",
            customer_phone="+573001112233",
        )
        await payments.save_checkout_if_absent(
            PaymentCheckout(
                appointment_id=appointment.id,
                tenant_id=tenant_id,
                preference_id="preference-rollback",
                checkout_url="https://www.mercadopago.com.co/checkout/redirect",
                amount=Decimal("25000.00"),
                currency="COP",
            )
        )

    asyncio.run(setup())
    payment = ProviderPayment(
        payment_id="payment-rollback",
        external_reference=appointment.id,
        status=PaymentStatus.APPROVED,
        amount=Decimal("25000.00"),
        currency="COP",
    )

    class FailingConfirmer:
        async def confirm_after_approved_payment(
            self, *, tenant_id: str, appointment_id: str, transaction: object
        ) -> None:
            raise RuntimeError("Appointment update failed")

    webhook = ProcessPaymentWebhook(
        provider=ApprovedPaymentProvider(payment),
        store=payments,
        appointment_confirmer=FailingConfirmer(),  # type: ignore[arg-type]
        confirmation_outbox=build_confirmation_outbox(postgres_database.sessions),
        confirmation_publisher=RecordingConfirmationPublisher(),
        signature_verifier=ValidSignature(),
        transaction_manager=SqlAlchemyTransactionManager(postgres_database.sessions),
    )

    async def process() -> bool:
        return await webhook.execute(
            signature_header="signed",
            request_id="request-rollback",
            payment_id=payment.payment_id,
        )

    with pytest.raises(RuntimeError, match="Appointment update failed"):
        asyncio.run(process())

    async def persisted_state() -> tuple[int, int, str]:
        async with postgres_database.sessions() as session:
            payment_count = await session.scalar(
                select(func.count()).select_from(PaymentRecord)
            )
            confirmation_count = await session.scalar(
                select(func.count()).select_from(AppointmentConfirmationRecord)
            )
            status = await session.scalar(
                select(AppointmentRecord.status).where(
                    AppointmentRecord.id == appointment.id
                )
            )
            return payment_count or 0, confirmation_count or 0, status or ""

    assert asyncio.run(persisted_state()) == (
        0,
        0,
        AppointmentStatus.PENDING_PAYMENT.value,
    )


def test_postgres_and_rabbitmq_deliver_one_confirmation_for_duplicate_webhooks(
    postgres_database: PostgresDatabase,
) -> None:
    amqp_url = os.environ.get("AMQP_URL")
    if not amqp_url:
        pytest.skip("Set AMQP_URL to run RabbitMQ integration tests")

    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    reservations = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    payments = SqlAlchemyPaymentStore(postgres_database.sessions)
    appointment = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )
    payment = ProviderPayment(
        payment_id="payment-rabbit-integration",
        external_reference=appointment.id,
        status=PaymentStatus.APPROVED,
        amount=Decimal("25000.00"),
        currency="COP",
    )
    queue = build_confirmation_queue(amqp_url)

    class RecordingWhatsAppSender:
        def __init__(self) -> None:
            self.requests: list[tuple[str, str, str]] = []

        async def send_confirmation(
            self,
            *,
            recipient_phone: str,
            message: str,
            idempotency_key: str,
        ) -> str:
            self.requests.append((recipient_phone, message, idempotency_key))
            return "whatsapp-message-integration"

    sender = RecordingWhatsAppSender()
    worker = DeliverAppointmentConfirmation(
        outbox=build_confirmation_outbox(postgres_database.sessions),
        sender=sender,
    )
    webhook = ProcessPaymentWebhook(
        provider=ApprovedPaymentProvider(payment),
        store=payments,
        appointment_confirmer=reservations,
        confirmation_outbox=build_confirmation_outbox(postgres_database.sessions),
        confirmation_publisher=queue,
        signature_verifier=ValidSignature(),
        transaction_manager=SqlAlchemyTransactionManager(postgres_database.sessions),
    )

    async def execute_integration() -> None:
        await reservations.create_customer_and_reserve(
            appointment,
            customer_name="Ana",
            customer_phone="+573001112233",
        )
        await payments.save_checkout_if_absent(
            PaymentCheckout(
                appointment_id=appointment.id,
                tenant_id=tenant_id,
                preference_id="preference-rabbit-integration",
                checkout_url="https://www.mercadopago.com.co/checkout/redirect",
                amount=Decimal("25000.00"),
                currency="COP",
            )
        )
        for request_id in ("rabbit-request-1", "rabbit-request-2"):
            assert await webhook.execute(
                signature_header="signed",
                request_id=request_id,
                payment_id=payment.payment_id,
            )

        connection = await aio_pika.connect_robust(amqp_url, timeout=5)
        try:
            channel = await connection.channel()
            broker_queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            handled = 0
            while handled < 2:
                message = await broker_queue.get(timeout=5, fail=False)
                assert message is not None, "confirmation message did not reach RabbitMQ"
                payload = json.loads(message.body)
                if payload.get("tenant_id") == tenant_id and payload.get("appointment_id") == appointment.id:
                    await queue.deliver_message(message, worker)
                    handled += 1
                else:
                    await message.ack()
        finally:
            await connection.close()

    asyncio.run(execute_integration())

    async def persisted() -> tuple[str, int, str | None]:
        async with postgres_database.sessions() as session:
            record = await session.scalar(
                select(AppointmentConfirmationRecord).where(
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                    AppointmentConfirmationRecord.appointment_id == appointment.id,
                )
            )
            assert record is not None
            return record.status, record.attempt_count, record.provider_message_id

    assert asyncio.run(persisted()) == ("sent", 1, "whatsapp-message-integration")
    assert len(sender.requests) == 1
    assert sender.requests[0][0] == "+573001112233"
    assert sender.requests[0][1].startswith("Hola Ana, tu cita de Cambio de aceite")


def test_postgres_booking_api_persists_checkout_from_service_configuration(
    postgres_database: PostgresDatabase,
) -> None:
    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    reservations = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    payments = SqlAlchemyPaymentStore(postgres_database.sessions)
    provider = FakeCheckoutProvider()
    booking = BookingService(
        catalog=build_catalog_reader(postgres_database.sessions),
        reservations=reservations,
        create_checkout=CreateCheckout(provider=provider, store=payments),
        create_pending_appointment=CreatePendingAppointment(reservations),
    )
    slot = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )

    with TestClient(create_app(booking_service=booking)) as client:
        response = client.post(
            f"/api/v1/workshops/{tenant_id}/appointments",
            json={
                "service_id": service_id,
                "starts_at": slot.starts_at.isoformat(),
                "customer_name": "Ana",
                "customer_phone": "+573001112233",
            },
        )

    assert response.status_code == 201, response.text
    response_data = response.json()
    assert response_data["status"] == AppointmentStatus.PENDING_PAYMENT.value
    assert response_data["checkout_url"] == (
        "https://www.mercadopago.com.co/checkout/redirect"
    )
    assert provider.request is not None
    assert provider.request["amount"] == Decimal("25000.00")
    assert provider.request["currency"] == "COP"

    async def persisted() -> tuple[PaymentCheckout | None, str | None]:
        checkout = await payments.get_checkout(response_data["appointment_id"])
        async with postgres_database.sessions() as session:
            appointment_status = await session.scalar(
                select(AppointmentRecord.status).where(
                    AppointmentRecord.id == response_data["appointment_id"]
                )
            )
        return checkout, appointment_status

    checkout, status = asyncio.run(persisted())
    assert checkout is not None
    assert checkout.amount == Decimal("25000.00")
    assert checkout.currency == "COP"
    assert status == AppointmentStatus.PENDING_PAYMENT.value


def test_checkout_provider_failure_releases_pending_slot(
    postgres_database: PostgresDatabase,
) -> None:
    tenant_id, service_id, slot_id = seed_slot(postgres_database.sessions)
    reservations = SqlAlchemyReservationStore(
        postgres_database.sessions, build_catalog_reader(postgres_database.sessions)
    )
    provider = FakeCheckoutProvider(fail=True)
    booking = BookingService(
        catalog=build_catalog_reader(postgres_database.sessions),
        reservations=reservations,
        create_checkout=CreateCheckout(
            provider=provider,
            store=SqlAlchemyPaymentStore(postgres_database.sessions),
        ),
        create_pending_appointment=CreatePendingAppointment(reservations),
    )
    slot = appointment_for(
        postgres_database.sessions, tenant_id, service_id, slot_id
    )

    with TestClient(
        create_app(booking_service=booking), raise_server_exceptions=False
    ) as client:
        response = client.post(
            f"/api/v1/workshops/{tenant_id}/appointments",
            json={
                "service_id": service_id,
                "starts_at": slot.starts_at.isoformat(),
                "customer_name": "Luis",
                "customer_phone": "+573009998877",
            },
        )

    assert response.status_code == 500
    assert provider.request is not None
    appointment_id = str(provider.request["appointment_id"])

    async def persisted() -> str | None:
        async with postgres_database.sessions() as session:
            return await session.scalar(
                select(AppointmentRecord.status).where(
                    AppointmentRecord.id == appointment_id
                )
            )

    assert asyncio.run(persisted()) == AppointmentStatus.CANCELLED.value
    assert asyncio.run(reservations.reserved_slot_ids(tenant_id, [slot_id])) == set()
