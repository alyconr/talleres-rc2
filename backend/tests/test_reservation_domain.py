from datetime import datetime, timedelta, timezone

import pytest

from app.modules.reservations.domain.appointment import Appointment, AppointmentStatus
from app.modules.reservations.domain.availability import slots_overlap


def appointment(**overrides: object) -> Appointment:
    starts_at = datetime(2026, 11, 10, 15, tzinfo=timezone.utc)
    values: dict[str, object] = {
        "id": "appointment-1",
        "tenant_id": "workshop-1",
        "customer_id": "customer-1",
        "service_id": "service-1",
        "availability_id": "slot-1",
        "starts_at": starts_at,
        "ends_at": starts_at + timedelta(hours=1),
    }
    values.update(overrides)
    return Appointment(**values)  # type: ignore[arg-type]


def test_new_appointment_waits_for_payment_and_requires_approval_to_confirm() -> None:
    pending = appointment()

    assert pending.status is AppointmentStatus.PENDING_PAYMENT
    with pytest.raises(ValueError, match="approved deposit"):
        pending.confirm(payment_approved=False)

    assert pending.confirm(payment_approved=True).status is AppointmentStatus.CONFIRMED


def test_appointment_requires_timezone_and_positive_duration() -> None:
    starts_at = datetime(2026, 11, 10, 15)
    with pytest.raises(ValueError, match="timezone"):
        appointment(starts_at=starts_at)
    with pytest.raises(ValueError, match="after its start"):
        appointment(ends_at=datetime(2026, 11, 10, 15, tzinfo=timezone.utc))


def test_adjacent_slots_do_not_overlap_but_intersecting_slots_do() -> None:
    start = datetime(2026, 11, 10, 15, tzinfo=timezone.utc)
    middle = start + timedelta(hours=1)
    end = middle + timedelta(hours=1)

    assert not slots_overlap(start, middle, middle, end)
    assert slots_overlap(start, end, middle, end)
