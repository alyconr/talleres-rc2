from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BookingResult:
    appointment_id: str
    status: str
    checkout_url: str
