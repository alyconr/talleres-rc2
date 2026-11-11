from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import StrEnum


class AppointmentStatus(StrEnum):
    PENDING_PAYMENT = "pending_payment"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class Appointment:
    id: str
    tenant_id: str
    customer_id: str
    service_id: str
    availability_id: str
    starts_at: datetime
    ends_at: datetime
    status: AppointmentStatus = AppointmentStatus.PENDING_PAYMENT

    def __post_init__(self) -> None:
        if not all((self.id, self.tenant_id, self.customer_id, self.service_id, self.availability_id)):
            raise ValueError("Appointment identifiers must not be empty")
        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Appointment times must include a timezone")
        if self.ends_at <= self.starts_at:
            raise ValueError("Appointment end must be after its start")

    def confirm(self, *, payment_approved: bool) -> Appointment:
        if not payment_approved:
            raise ValueError("Appointment requires an approved deposit")
        if self.status is not AppointmentStatus.PENDING_PAYMENT:
            raise ValueError("Only appointments awaiting payment can be confirmed")
        return replace(self, status=AppointmentStatus.CONFIRMED)
