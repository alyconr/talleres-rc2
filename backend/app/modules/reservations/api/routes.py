from datetime import datetime
from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from app.modules.reservations.application.booking_service import (
    BookingService,
    InvalidDepositError,
)
from app.modules.reservations.api.schemas import (
    AvailabilityResponse,
    CreateBookingRequest,
    CreateBookingResponse,
    ServiceResponse,
)

router = APIRouter(prefix="/api/v1/workshops/{tenant_id}", tags=["booking"])


def get_booking_service(request: Request) -> BookingService:
    service = getattr(request.app.state, "booking_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Booking service is unavailable",
        )
    return cast(BookingService, service)


@router.get("/services", response_model=list[ServiceResponse])
async def list_services(
    tenant_id: str,
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> list[ServiceResponse]:
    try:
        return await service.list_services(tenant_id=tenant_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Workshop not found") from exc


@router.get("/availability", response_model=list[AvailabilityResponse])
async def list_availability(
    tenant_id: str,
    service: Annotated[BookingService, Depends(get_booking_service)],
    service_id: str = Query(min_length=1, max_length=100),
    starts_after: datetime = Query(...),
    ends_before: datetime = Query(...),
) -> list[AvailabilityResponse]:
    if starts_after.tzinfo is None or ends_before.tzinfo is None:
        raise HTTPException(status_code=422, detail="Date range must include a timezone")
    if ends_before <= starts_after:
        raise HTTPException(status_code=422, detail="Invalid date range")
    try:
        return await service.list_availability(
            tenant_id=tenant_id,
            service_id=service_id,
            starts_after=starts_after,
            ends_before=ends_before,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Workshop or service not found") from exc


@router.post("/appointments", response_model=CreateBookingResponse, status_code=201)
async def create_booking(
    tenant_id: str,
    payload: CreateBookingRequest,
    service: Annotated[BookingService, Depends(get_booking_service)],
) -> CreateBookingResponse:
    try:
        return await service.create_booking(
            tenant_id=tenant_id,
            service_id=payload.service_id,
            starts_at=payload.starts_at,
            customer_name=payload.customer_name,
            customer_phone=payload.customer_phone,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Service or availability not found") from exc
    except InvalidDepositError as exc:
        raise HTTPException(
            status_code=422, detail="Service deposit must be greater than zero"
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail="Selected time is unavailable") from exc
