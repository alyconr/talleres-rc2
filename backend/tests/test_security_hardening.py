import asyncio
import hashlib
import hmac
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.dialects import postgresql

from app.modules.catalog.infrastructure.sqlalchemy_catalog_reader import (
    SqlAlchemyCatalogReader,
)
from app.modules.payments.infrastructure.webhook_signature import verify_webhook_signature
from app.modules.reservations.api.schemas import CreateBookingRequest
from app.modules.reservations.domain.appointment import Appointment
from app.modules.reservations.infrastructure.sqlalchemy_reservation_store import (
    SlotUnavailable,
    SqlAlchemyReservationStore,
)


@pytest.mark.parametrize("digest", [chr(233) * 64, "x" * 63, "g" * 64])
def test_webhook_signature_rejects_malformed_digest(digest: str) -> None:
    assert not verify_webhook_signature(
        signature_header=f"ts=1800000000,v1={digest}",
        request_id="request-1",
        data_id="payment-1",
        secret="test-secret",
        now=1_800_000_000,
    )


def test_booking_schema_rejects_timezone_naive_datetime() -> None:
    with pytest.raises(ValueError):
        CreateBookingRequest.model_validate(
            {
                "service_id": "service-1",
                "starts_at": "2026-11-11T15:00:00",
                "customer_name": "Ana",
                "customer_phone": "+573001112233",
            }
        )


def test_booking_schema_rejects_invalid_phone_format() -> None:
    with pytest.raises(ValueError):
        CreateBookingRequest.model_validate(
            {
                "service_id": "service-1",
                "starts_at": "2026-11-11T15:00:00Z",
                "customer_name": "Ana",
                "customer_phone": "not-a-phone",
            }
        )


@pytest.mark.parametrize("customer_name", ["   ", "Ana\nBolaños"])
def test_booking_schema_rejects_blank_or_controlled_customer_name(
    customer_name: str,
) -> None:
    with pytest.raises(ValueError):
        CreateBookingRequest.model_validate(
            {
                "service_id": "service-1",
                "starts_at": "2026-11-11T15:00:00Z",
                "customer_name": customer_name,
                "customer_phone": "+573001112233",
            }
        )


def test_reservation_slot_occupancy_query_is_tenant_scoped() -> None:
    class SessionCapture:
        statement = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        def begin(self):
            return self

        async def scalar(self, statement):
            self.statement = statement
            return "occupied-appointment"

    session = SessionCapture()
    store = SqlAlchemyReservationStore(
        lambda: session,  # type: ignore[arg-type]
        catalog=None,  # type: ignore[arg-type]
    )
    starts_at = datetime(2026, 11, 11, 15, tzinfo=timezone.utc)
    appointment = Appointment(
        id="appointment-1",
        tenant_id="workshop-1",
        customer_id="customer-1",
        service_id="service-1",
        availability_id="slot-1",
        starts_at=starts_at,
        ends_at=starts_at + timedelta(hours=1),
    )

    with pytest.raises(SlotUnavailable):
        asyncio.run(
            store.create_customer_and_reserve(
                appointment,
                customer_name="Ana",
                customer_phone="+573001112233",
            )
        )

    assert session.statement is not None
    sql = str(session.statement.compile(dialect=postgresql.dialect()))
    assert "appointments.tenant_id" in sql


def test_availability_query_caps_result_count() -> None:
    class SessionCapture:
        statement = None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_: object) -> None:
            return None

        async def scalars(self, statement):
            self.statement = statement
            return []

    session = SessionCapture()
    reader = SqlAlchemyCatalogReader(lambda: session)  # type: ignore[arg-type]
    starts_after = datetime(2026, 11, 11, tzinfo=timezone.utc)
    asyncio.run(
        reader.list_slots(
            "workshop-1", "service-1", starts_after, starts_after + timedelta(days=90)
        )
    )

    assert session.statement is not None
    assert session.statement._limit_clause is not None
