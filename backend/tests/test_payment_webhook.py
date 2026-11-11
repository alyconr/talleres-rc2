import asyncio
import hashlib
import hmac
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from decimal import Decimal
from datetime import datetime, timedelta, timezone

import pytest

from app.modules.payments.application.process_payment_webhook import ProcessPaymentWebhook
from app.modules.conversations.public import AppointmentConfirmation
from app.modules.payments.application.create_checkout import CreateCheckout
from app.modules.payments.domain.payment import (
    PaymentCheckout,
    PaymentStatus,
    ProviderPayment,
)
from app.modules.payments.infrastructure.webhook_signature import verify_webhook_signature


def signed_header(*, secret: str, request_id: str, data_id: str, timestamp: int) -> str:
    manifest = f"id:{data_id};request-id:{request_id};ts:{timestamp};"
    signature = hmac.new(secret.encode(), manifest.encode(), hashlib.sha256).hexdigest()
    return f"ts={timestamp},v1={signature}"


def test_webhook_signature_is_verified_and_replay_window_is_enforced() -> None:
    now = 1_800_000_000
    header = signed_header(
        secret="test-secret",
        request_id="request-1",
        data_id="payment-1",
        timestamp=now,
    )

    assert verify_webhook_signature(
        signature_header=header,
        request_id="request-1",
        data_id="payment-1",
        secret="test-secret",
        now=now,
    )
    assert not verify_webhook_signature(
        signature_header=header,
        request_id="request-1",
        data_id="payment-2",
        secret="test-secret",
        now=now,
    )
    assert not verify_webhook_signature(
        signature_header=header,
        request_id="request-1",
        data_id="payment-1",
        secret="test-secret",
        now=now + 301,
    )


class AlwaysValidSignature:
    def verify(self, **_: str | None) -> bool:
        return True


class InvalidSignature:
    def verify(self, **_: str | None) -> bool:
        return False


class FakeProvider:
    def __init__(self, payment: ProviderPayment) -> None:
        self.payment = payment

    async def get_payment(self, payment_id: str) -> ProviderPayment:
        assert payment_id == self.payment.payment_id
        return self.payment


class FakeTransactionManager:
    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[object]:
        yield object()


class RecordingCheckoutProvider:
    def __init__(self) -> None:
        self.called = False

    async def create_checkout(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> tuple[str, str]:
        self.called = True
        return "preference-1", "https://www.mercadopago.com.co/checkout/redirect"


class EmptyCheckoutStore:
    async def get_checkout(self, appointment_id: str) -> None:
        return None


class FakeStore:
    def __init__(self) -> None:
        self.checkout = PaymentCheckout(
            appointment_id="appointment-1",
            tenant_id="workshop-1",
            preference_id="preference-1",
            checkout_url="https://www.mercadopago.com.co/checkout/redirect",
            amount=Decimal("25000.00"),
            currency="COP",
        )
        self.recorded_payment_ids: set[str] = set()

    async def get_checkout(self, appointment_id: str) -> PaymentCheckout | None:
        return self.checkout if appointment_id == self.checkout.appointment_id else None

    async def record_approved_payment_if_new(
        self,
        payment: ProviderPayment,
        *,
        tenant_id: str,
        appointment_id: str,
        transaction: object,
    ) -> None:
        assert tenant_id == self.checkout.tenant_id
        assert appointment_id == self.checkout.appointment_id
        self.recorded_payment_ids.add(payment.payment_id)


class FakeConfirmer:
    def __init__(self) -> None:
        self.confirmed: list[tuple[str, str]] = []

    async def confirm_after_approved_payment(
        self, *, tenant_id: str, appointment_id: str, transaction: object
    ) -> AppointmentConfirmation:
        self.confirmed.append((tenant_id, appointment_id))
        return AppointmentConfirmation(
            idempotency_key=f"appointment-confirmation:{tenant_id}:{appointment_id}",
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            recipient_phone="+573001234567",
            customer_name="Ana",
            service_name="Cambio de aceite",
            starts_at=datetime(2026, 11, 12, 14, 30, tzinfo=timezone(timedelta(hours=-5))),
        )


class FakeConfirmationOutbox:
    def __init__(self) -> None:
        self.keys: set[str] = set()
        self.enqueue_attempts = 0

    async def enqueue_if_absent(
        self,
        confirmation: AppointmentConfirmation,
        *,
        transaction: object,
    ) -> bool:
        self.enqueue_attempts += 1
        if confirmation.idempotency_key in self.keys:
            return False
        self.keys.add(confirmation.idempotency_key)
        return True


class FakeConfirmationPublisher:
    def __init__(self) -> None:
        self.published: list[tuple[str, str]] = []

    async def publish_confirmation(self, *, tenant_id: str, appointment_id: str) -> None:
        self.published.append((tenant_id, appointment_id))


def test_repeated_approved_notification_records_payment_once_and_retries_confirmation() -> None:
    payment = ProviderPayment(
        payment_id="payment-1",
        external_reference="appointment-1",
        status=PaymentStatus.APPROVED,
        amount=Decimal("25000.00"),
        currency="COP",
    )
    store = FakeStore()
    confirmer = FakeConfirmer()
    outbox = FakeConfirmationOutbox()
    publisher = FakeConfirmationPublisher()
    use_case = ProcessPaymentWebhook(
        provider=FakeProvider(payment),
        store=store,
        appointment_confirmer=confirmer,
        confirmation_outbox=outbox,
        confirmation_publisher=publisher,
        signature_verifier=AlwaysValidSignature(),
        transaction_manager=FakeTransactionManager(),
    )

    async def process_twice() -> tuple[bool, bool]:
        first = await use_case.execute(
            signature_header="signed", request_id="request-1", payment_id="payment-1"
        )
        second = await use_case.execute(
            signature_header="signed", request_id="request-1", payment_id="payment-1"
        )
        return first, second

    assert asyncio.run(process_twice()) == (True, True)
    assert store.recorded_payment_ids == {"payment-1"}
    assert confirmer.confirmed == [
        ("workshop-1", "appointment-1"),
        ("workshop-1", "appointment-1"),
    ]
    assert outbox.keys == {"appointment-confirmation:workshop-1:appointment-1"}
    assert outbox.enqueue_attempts == 2
    assert publisher.published == [
        ("workshop-1", "appointment-1"),
        ("workshop-1", "appointment-1"),
    ]


def test_rejected_payment_does_not_confirm_appointment() -> None:
    payment = ProviderPayment(
        payment_id="payment-1",
        external_reference="appointment-1",
        status=PaymentStatus.REJECTED,
        amount=Decimal("25000.00"),
        currency="COP",
    )
    confirmer = FakeConfirmer()
    outbox = FakeConfirmationOutbox()
    publisher = FakeConfirmationPublisher()
    use_case = ProcessPaymentWebhook(
        provider=FakeProvider(payment),
        store=FakeStore(),
        appointment_confirmer=confirmer,
        confirmation_outbox=outbox,
        confirmation_publisher=publisher,
        signature_verifier=AlwaysValidSignature(),
        transaction_manager=FakeTransactionManager(),
    )

    async def process() -> bool:
        return await use_case.execute(
            signature_header="signed", request_id="request-1", payment_id="payment-1"
        )

    assert asyncio.run(process()) is False
    assert confirmer.confirmed == []
    assert outbox.keys == set()
    assert outbox.enqueue_attempts == 0
    assert publisher.published == []


def test_invalid_signature_does_not_enqueue_confirmation() -> None:
    payment = ProviderPayment(
        payment_id="payment-1",
        external_reference="appointment-1",
        status=PaymentStatus.APPROVED,
        amount=Decimal("25000.00"),
        currency="COP",
    )
    outbox = FakeConfirmationOutbox()
    publisher = FakeConfirmationPublisher()
    use_case = ProcessPaymentWebhook(
        provider=FakeProvider(payment),
        store=FakeStore(),
        appointment_confirmer=FakeConfirmer(),
        confirmation_outbox=outbox,
        confirmation_publisher=publisher,
        signature_verifier=InvalidSignature(),
        transaction_manager=FakeTransactionManager(),
    )

    async def process() -> None:
        await use_case.execute(
            signature_header="invalid", request_id="request-1", payment_id="payment-1"
        )

    with pytest.raises(ValueError, match="Invalid payment notification"):
        asyncio.run(process())
    assert outbox.keys == set()
    assert outbox.enqueue_attempts == 0
    assert publisher.published == []


@pytest.mark.parametrize(
    ("amount", "currency"),
    [(Decimal("100.00"), "COP"), (Decimal("25000.00"), "USD")],
)
def test_approved_payment_amount_and_currency_must_match_checkout(
    amount: Decimal, currency: str
) -> None:
    payment = ProviderPayment(
        payment_id="payment-1",
        external_reference="appointment-1",
        status=PaymentStatus.APPROVED,
        amount=amount,
        currency=currency,
    )
    use_case = ProcessPaymentWebhook(
        provider=FakeProvider(payment),
        store=FakeStore(),
        appointment_confirmer=FakeConfirmer(),
        confirmation_outbox=FakeConfirmationOutbox(),
        confirmation_publisher=FakeConfirmationPublisher(),
        signature_verifier=AlwaysValidSignature(),
        transaction_manager=FakeTransactionManager(),
    )

    async def process() -> bool:
        return await use_case.execute(
            signature_header="signed", request_id="request-1", payment_id="payment-1"
        )

    with pytest.raises(ValueError, match="does not match"):
        asyncio.run(process())


def test_payment_reference_must_identify_a_saved_checkout() -> None:
    payment = ProviderPayment(
        payment_id="payment-1",
        external_reference="another-appointment",
        status=PaymentStatus.APPROVED,
        amount=Decimal("25000.00"),
        currency="COP",
    )
    store = FakeStore()
    confirmer = FakeConfirmer()
    use_case = ProcessPaymentWebhook(
        provider=FakeProvider(payment),
        store=store,
        appointment_confirmer=confirmer,
        confirmation_outbox=FakeConfirmationOutbox(),
        confirmation_publisher=FakeConfirmationPublisher(),
        signature_verifier=AlwaysValidSignature(),
        transaction_manager=FakeTransactionManager(),
    )

    async def process() -> bool:
        return await use_case.execute(
            signature_header="signed", request_id="request-1", payment_id="payment-1"
        )

    assert asyncio.run(process()) is False
    assert store.recorded_payment_ids == set()
    assert confirmer.confirmed == []


@pytest.mark.parametrize(
    ("amount", "currency"),
    [(Decimal("0"), "COP"), (Decimal("25000.00"), "cop")],
)
def test_checkout_rejects_missing_or_invalid_service_deposit(
    amount: Decimal, currency: str
) -> None:
    provider = RecordingCheckoutProvider()
    use_case = CreateCheckout(
        provider=provider,
        store=EmptyCheckoutStore(),  # type: ignore[arg-type]
    )

    async def create() -> None:
        await use_case.execute(
            appointment_id="appointment-1",
            tenant_id="workshop-1",
            appointment_status="pending_payment",
            title="Cambio de aceite",
            amount=amount,
            currency=currency,
        )

    with pytest.raises(ValueError):
        asyncio.run(create())
    assert provider.called is False
