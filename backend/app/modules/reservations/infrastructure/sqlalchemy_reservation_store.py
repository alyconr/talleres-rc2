from uuid import uuid4
from typing import cast

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.catalog.public import CatalogReader
from app.modules.conversations.public import AppointmentConfirmation
from app.modules.reservations.domain.appointment import Appointment, AppointmentStatus
from app.modules.reservations.infrastructure.models import AppointmentRecord, CustomerRecord


class SlotUnavailable(ValueError):
    pass


class SqlAlchemyReservationStore:
    def __init__(
        self,
        sessions: async_sessionmaker[AsyncSession],
        catalog: CatalogReader,
    ) -> None:
        self._sessions = sessions
        self._catalog = catalog

    async def create_customer_and_reserve(
        self,
        appointment: Appointment,
        *,
        customer_name: str,
        customer_phone: str,
    ) -> Appointment:
        try:
            async with self._sessions() as session, session.begin():
                occupied = await session.scalar(
                    select(AppointmentRecord.id).where(
                        AppointmentRecord.availability_id == appointment.availability_id,
                        AppointmentRecord.status != AppointmentStatus.CANCELLED.value,
                    )
                )
                if occupied is not None:
                    raise SlotUnavailable("Selected time is unavailable")

                await session.execute(
                    insert(CustomerRecord)
                    .values(
                        id=str(uuid4()),
                        tenant_id=appointment.tenant_id,
                        name=customer_name,
                        phone=customer_phone,
                    )
                    .on_conflict_do_nothing(index_elements=["tenant_id", "phone"])
                )
                customer = await session.scalar(
                    select(CustomerRecord).where(
                        CustomerRecord.tenant_id == appointment.tenant_id,
                        CustomerRecord.phone == customer_phone,
                    )
                )
                if customer is None:
                    raise RuntimeError("Could not save customer")

                session.add(
                    AppointmentRecord(
                        id=appointment.id,
                        tenant_id=appointment.tenant_id,
                        customer_id=customer.id,
                        service_id=appointment.service_id,
                        availability_id=appointment.availability_id,
                        starts_at=appointment.starts_at,
                        ends_at=appointment.ends_at,
                        status=AppointmentStatus.PENDING_PAYMENT.value,
                    )
                )
                await session.flush()
                return Appointment(
                    id=appointment.id,
                    tenant_id=appointment.tenant_id,
                    customer_id=customer.id,
                    service_id=appointment.service_id,
                    availability_id=appointment.availability_id,
                    starts_at=appointment.starts_at,
                    ends_at=appointment.ends_at,
                )
        except IntegrityError as exc:
            raise SlotUnavailable("Selected time is unavailable") from exc

    async def reserved_slot_ids(self, tenant_id: str, slot_ids: list[str]) -> set[str]:
        if not slot_ids:
            return set()
        async with self._sessions() as session:
            result = await session.scalars(
                select(AppointmentRecord.availability_id).where(
                    AppointmentRecord.tenant_id == tenant_id,
                    AppointmentRecord.availability_id.in_(slot_ids),
                    AppointmentRecord.status != AppointmentStatus.CANCELLED.value,
                )
            )
            return set(result)

    async def release_pending(self, *, tenant_id: str, appointment_id: str) -> None:
        async with self._sessions() as session, session.begin():
            await session.execute(
                update(AppointmentRecord)
                .where(
                    AppointmentRecord.id == appointment_id,
                    AppointmentRecord.tenant_id == tenant_id,
                    AppointmentRecord.status == AppointmentStatus.PENDING_PAYMENT.value,
                )
                .values(status=AppointmentStatus.CANCELLED.value)
            )

    async def confirm_after_approved_payment(
        self, *, tenant_id: str, appointment_id: str, transaction: object
    ) -> AppointmentConfirmation:
        session = cast(AsyncSession, transaction)
        appointment = await session.scalar(
            select(AppointmentRecord)
            .where(
                AppointmentRecord.id == appointment_id,
                AppointmentRecord.tenant_id == tenant_id,
            )
            .with_for_update()
        )
        if appointment is None:
            raise LookupError("Appointment not found")
        if appointment.status == AppointmentStatus.PENDING_PAYMENT.value:
            appointment.status = AppointmentStatus.CONFIRMED.value
        elif appointment.status not in {
            AppointmentStatus.CONFIRMED.value,
            AppointmentStatus.COMPLETED.value,
        }:
            raise ValueError("Appointment cannot be confirmed in its current state")

        details = await session.execute(
            select(AppointmentRecord, CustomerRecord)
            .join(
                CustomerRecord,
                (CustomerRecord.id == AppointmentRecord.customer_id)
                & (CustomerRecord.tenant_id == AppointmentRecord.tenant_id),
            )
            .where(
                AppointmentRecord.id == appointment_id,
                AppointmentRecord.tenant_id == tenant_id,
            )
        )
        row = details.one_or_none()
        if row is None:
            raise LookupError("Appointment confirmation details not found")
        appointment, customer = row
        service_name = await self._catalog.get_service_name(tenant_id, appointment.service_id)
        if service_name is None:
            raise LookupError("Appointment service not found")
        return AppointmentConfirmation(
            idempotency_key=f"appointment-confirmation:{tenant_id}:{appointment_id}",
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            recipient_phone=customer.phone,
            customer_name=customer.name,
            service_name=service_name,
            starts_at=appointment.starts_at,
        )
