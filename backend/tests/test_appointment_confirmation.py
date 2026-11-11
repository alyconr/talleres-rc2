from datetime import datetime, timedelta, timezone

import pytest

from app.modules.conversations.public import AppointmentConfirmation


def test_appointment_confirmation_builds_spanish_message() -> None:
    confirmation = AppointmentConfirmation(
        idempotency_key="appointment-confirmation:workshop-1:appointment-1",
        tenant_id="workshop-1",
        appointment_id="appointment-1",
        recipient_phone="+573001234567",
        customer_name="Ana",
        service_name="Cambio de aceite",
        starts_at=datetime(2026, 11, 12, 14, 30, tzinfo=timezone(timedelta(hours=-5))),
    )

    assert confirmation.message == (
        "Hola Ana, tu cita de Cambio de aceite quedó confirmada para el "
        "12/11/2026 a las 14:30."
    )


def test_appointment_confirmation_requires_identifiers_and_contact_data() -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        AppointmentConfirmation(
            idempotency_key=" ",
            tenant_id="workshop-1",
            appointment_id="appointment-1",
            recipient_phone="+573001234567",
            customer_name="Ana",
            service_name="Cambio de aceite",
            starts_at=datetime(2026, 11, 12, 14, 30, tzinfo=timezone(timedelta(hours=-5))),
        )


def test_appointment_confirmation_requires_timezone_aware_start() -> None:
    with pytest.raises(ValueError, match="timezone"):
        AppointmentConfirmation(
            idempotency_key="appointment-confirmation:workshop-1:appointment-1",
            tenant_id="workshop-1",
            appointment_id="appointment-1",
            recipient_phone="+573001234567",
            customer_name="Ana",
            service_name="Cambio de aceite",
            starts_at=datetime(2026, 11, 12, 14, 30),
        )
