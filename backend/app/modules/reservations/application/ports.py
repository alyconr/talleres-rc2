from typing import Protocol

from app.modules.conversations.public import AppointmentConfirmation
from app.modules.reservations.domain.appointment import Appointment


class ReservationStore(Protocol):
    async def create_customer_and_reserve(
        self,
        appointment: Appointment,
        *,
        customer_name: str,
        customer_phone: str,
    ) -> Appointment: ...

    async def reserved_slot_ids(self, tenant_id: str, slot_ids: list[str]) -> set[str]: ...

    async def release_pending(self, *, tenant_id: str, appointment_id: str) -> None: ...

    async def confirm_after_approved_payment(
        self, *, tenant_id: str, appointment_id: str, transaction: object
    ) -> AppointmentConfirmation: ...
