from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class ServiceResponse(StrictSchema):
    id: str
    name: str
    duration_minutes: int = Field(gt=0)
    deposit_amount: Decimal = Field(gt=0)
    currency: str = Field(pattern=r"^[A-Z]{3}$")


class AvailabilityResponse(StrictSchema):
    starts_at: datetime
    ends_at: datetime


class CreateBookingRequest(StrictSchema):
    service_id: str = Field(min_length=1, max_length=36)
    starts_at: datetime = Field(strict=False)
    customer_name: str = Field(min_length=1, max_length=120)
    customer_phone: str = Field(min_length=8, max_length=16, pattern=r"^\+[1-9][0-9]{6,14}$")

    @field_validator("starts_at")
    @classmethod
    def starts_at_must_be_timezone_aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("starts_at must include a timezone")
        return value

    @field_validator("customer_name")
    @classmethod
    def customer_name_must_be_safe(cls, value: str) -> str:
        if not value.strip() or any(ord(character) < 32 or ord(character) == 127 for character in value):
            raise ValueError("customer_name must be nonempty and contain no control characters")
        return value.strip()


class CreateBookingResponse(StrictSchema):
    appointment_id: str
    status: str
    checkout_url: str
