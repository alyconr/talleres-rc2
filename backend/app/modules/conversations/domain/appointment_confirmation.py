from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum


class DeliveryResult(StrEnum):
    SENT = "sent"
    RETRY = "retry"
    FAILED = "failed"
    DUPLICATE = "duplicate"


@dataclass(frozen=True, slots=True)
class ConfirmationDelivery:
    idempotency_key: str
    recipient_phone: str
    message: str
    attempt_count: int

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.idempotency_key, self.recipient_phone, self.message)
        ):
            raise ValueError("Confirmation delivery fields must not be empty")
        if self.attempt_count < 1:
            raise ValueError("Confirmation delivery attempt count must be positive")


@dataclass(frozen=True, slots=True)
class AppointmentConfirmation:
    idempotency_key: str
    tenant_id: str
    appointment_id: str
    recipient_phone: str
    customer_name: str
    service_name: str
    starts_at: datetime

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (
                self.idempotency_key,
                self.tenant_id,
                self.appointment_id,
                self.recipient_phone,
                self.customer_name,
                self.service_name,
            )
        ):
            raise ValueError("Appointment confirmation fields must not be empty")
        if self.starts_at.tzinfo is None:
            raise ValueError("Appointment confirmation time must include a timezone")

    @property
    def message(self) -> str:
        date = self.starts_at.strftime("%d/%m/%Y a las %H:%M")
        return (
            f"Hola {self.customer_name}, tu cita de {self.service_name} quedó "
            f"confirmada para el {date}."
        )
