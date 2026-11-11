from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


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
    service_id: str = Field(min_length=1, max_length=100)
    starts_at: datetime = Field(strict=False)
    customer_name: str = Field(min_length=1, max_length=120)
    customer_phone: str = Field(min_length=6, max_length=32)


class CreateBookingResponse(StrictSchema):
    appointment_id: str
    status: str
    checkout_url: str
