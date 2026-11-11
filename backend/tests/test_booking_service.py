import asyncio
from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.modules.catalog.domain.catalog_items import AvailabilitySlot, BookableService
from app.modules.reservations.application.booking_service import BookingService
from app.modules.reservations.domain.appointment import Appointment


class FakeCatalog:
    def __init__(self, deposit_amount: Decimal = Decimal("0")) -> None:
        self.deposit_amount = deposit_amount

    async def get_bookable_service(
        self, tenant_id: str, service_id: str
    ) -> BookableService:
        return BookableService(
            id=service_id,
            tenant_id=tenant_id,
            name="Cambio de aceite",
            duration_minutes=60,
            deposit_amount=self.deposit_amount,
            currency="COP",
        )

    async def get_slot(
        self, tenant_id: str, service_id: str, starts_at: datetime
    ) -> AvailabilitySlot:
        return AvailabilitySlot(
            id="slot-1",
            tenant_id=tenant_id,
            service_id=service_id,
            starts_at=starts_at,
            ends_at=datetime(2026, 11, 11, 16, tzinfo=timezone.utc),
        )


class FakeReservationStore:
    def __init__(self) -> None:
        self.created: list[Appointment] = []

    async def create_customer_and_reserve(
        self, appointment: Appointment, *, customer_name: str, customer_phone: str
    ) -> Appointment:
        self.created.append(appointment)
        return appointment

    async def reserved_slot_ids(self, tenant_id: str, slot_ids: list[str]) -> set[str]:
        return set()

    async def release_pending(self, *, tenant_id: str, appointment_id: str) -> None:
        return None


class FakeCreatePendingAppointment:
    def __init__(self, store: FakeReservationStore) -> None:
        self.store = store

    async def execute(self, **values: object) -> Appointment:
        appointment = Appointment(
            id=str(values["appointment_id"]),
            tenant_id=str(values["tenant_id"]),
            customer_id="customer-1",
            service_id=str(values["service_id"]),
            availability_id=str(values["availability_id"]),
            starts_at=values["starts_at"],  # type: ignore[arg-type]
            ends_at=values["ends_at"],  # type: ignore[arg-type]
        )
        return await self.store.create_customer_and_reserve(
            appointment,
            customer_name=str(values["customer_name"]),
            customer_phone=str(values["customer_phone"]),
        )


class FakeCheckout:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    async def execute(self, **values: object) -> object:
        self.calls.append(values)
        return type("Checkout", (), {"checkout_url": "https://example.test"})()


def test_zero_deposit_is_rejected_before_reserving_or_starting_checkout() -> None:
    reservations = FakeReservationStore()
    checkout = FakeCheckout()
    service = BookingService(
        catalog=FakeCatalog(),  # type: ignore[arg-type]
        reservations=reservations,  # type: ignore[arg-type]
        create_checkout=checkout,  # type: ignore[arg-type]
        create_pending_appointment=FakeCreatePendingAppointment(reservations),  # type: ignore[arg-type]
    )

    with pytest.raises(ValueError, match="deposit"):
        asyncio.run(
            service.create_booking(
                tenant_id="workshop-1",
                service_id="service-1",
                starts_at=datetime(2026, 11, 11, 15, tzinfo=timezone.utc),
                customer_name="Ana",
                customer_phone="+573001112233",
            )
        )

    assert reservations.created == []
    assert checkout.calls == []


def test_positive_deposit_still_creates_reservation_and_checkout() -> None:
    reservations = FakeReservationStore()
    checkout = FakeCheckout()
    service = BookingService(
        catalog=FakeCatalog(Decimal("25000")),  # type: ignore[arg-type]
        reservations=reservations,  # type: ignore[arg-type]
        create_checkout=checkout,  # type: ignore[arg-type]
        create_pending_appointment=FakeCreatePendingAppointment(reservations),  # type: ignore[arg-type]
    )

    result = asyncio.run(
        service.create_booking(
            tenant_id="workshop-1",
            service_id="service-1",
            starts_at=datetime(2026, 11, 11, 15, tzinfo=timezone.utc),
            customer_name="Ana",
            customer_phone="+573001112233",
        )
    )

    assert result.checkout_url == "https://example.test"
    assert len(reservations.created) == 1
    assert len(checkout.calls) == 1
    assert checkout.calls[0]["amount"] == Decimal("25000")
