from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.modules.reservations.application.ports import ReservationStore
from app.modules.reservations.domain.appointment import Appointment


@dataclass(frozen=True, slots=True)
class CreatePendingAppointment:
    store: ReservationStore

    async def execute(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        service_id: str,
        availability_id: str,
        starts_at: datetime,
        ends_at: datetime,
        customer_name: str,
        customer_phone: str,
    ) -> Appointment:
        appointment = Appointment(
            id=appointment_id,
            tenant_id=tenant_id,
            customer_id=str(uuid4()),
            service_id=service_id,
            availability_id=availability_id,
            starts_at=starts_at,
            ends_at=ends_at,
        )
        return await self.store.create_customer_and_reserve(
            appointment,
            customer_name=customer_name,
            customer_phone=customer_phone,
        )
