from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class BookableService:
    id: str
    tenant_id: str
    name: str
    duration_minutes: int
    deposit_amount: Decimal
    currency: str


@dataclass(frozen=True, slots=True)
class AvailabilitySlot:
    id: str
    tenant_id: str
    service_id: str
    starts_at: datetime
    ends_at: datetime
