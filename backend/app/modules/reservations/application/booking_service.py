from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.modules.catalog.public import AvailabilitySlot, BookableService, CatalogReader
from app.modules.payments.public import CreateCheckout
from app.modules.reservations.application.create_pending_appointment import (
    CreatePendingAppointment,
)
from app.modules.reservations.application.ports import ReservationStore
from app.modules.reservations.application.public_types import BookingResult


@dataclass(frozen=True, slots=True)
class BookingService:
    catalog: CatalogReader
    reservations: ReservationStore
    create_checkout: CreateCheckout
    create_pending_appointment: CreatePendingAppointment

    async def list_services(self, *, tenant_id: str) -> list[BookableService]:
        return await self.catalog.list_bookable_services(tenant_id)

    async def list_availability(
        self,
        *,
        tenant_id: str,
        service_id: str,
        starts_after: datetime,
        ends_before: datetime,
    ) -> list[AvailabilitySlot]:
        service = await self.catalog.get_bookable_service(tenant_id, service_id)
        if service is None:
            raise LookupError("Service not found")
        slots = await self.catalog.list_slots(
            tenant_id,
            service_id,
            starts_after,
            ends_before,
        )
        reserved = await self.reservations.reserved_slot_ids(
            tenant_id, [slot.id for slot in slots]
        )
        return [slot for slot in slots if slot.id not in reserved]

    async def create_booking(
        self,
        *,
        tenant_id: str,
        service_id: str,
        starts_at: datetime,
        customer_name: str,
        customer_phone: str,
    ) -> BookingResult:
        service = await self.catalog.get_bookable_service(tenant_id, service_id)
        if service is None:
            raise LookupError("Service not found")
        slot = await self.catalog.get_slot(tenant_id, service_id, starts_at)
        if slot is None:
            raise LookupError("Availability not found")

        appointment_id = str(uuid4())
        appointment = await self.create_pending_appointment.execute(
            appointment_id=appointment_id,
            tenant_id=tenant_id,
            service_id=service_id,
            availability_id=slot.id,
            starts_at=slot.starts_at,
            ends_at=slot.ends_at,
            customer_name=customer_name,
            customer_phone=customer_phone,
        )
        try:
            checkout = await self.create_checkout.execute(
                appointment_id=appointment.id,
                tenant_id=appointment.tenant_id,
                appointment_status=appointment.status.value,
                title=service.name,
                amount=service.deposit_amount,
                currency=service.currency,
            )
        except Exception:
            await self.reservations.release_pending(
                tenant_id=tenant_id,
                appointment_id=appointment.id,
            )
            raise
        return BookingResult(
            appointment_id=appointment.id,
            status=appointment.status.value,
            checkout_url=checkout.checkout_url,
        )
