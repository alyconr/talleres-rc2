import os
from datetime import datetime, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.modules.catalog.public import AvailabilitySlot, BookableService
from app.modules.reservations.application.public_types import BookingResult
from app.shared.settings import Settings


class FakeBookingService:
    def __init__(self) -> None:
        self.created: dict[str, object] | None = None
        self.requested_tenant: str | None = None

    async def list_services(self, *, tenant_id: str) -> list[BookableService]:
        self.requested_tenant = tenant_id
        return [
            BookableService(
                id="service-1",
                tenant_id=tenant_id,
                name="Cambio de aceite",
                duration_minutes=60,
                deposit_amount=Decimal("25000.00"),
                currency="COP",
            )
        ]

    async def list_availability(
        self,
        *,
        tenant_id: str,
        service_id: str,
        starts_after: datetime,
        ends_before: datetime,
    ) -> list[AvailabilitySlot]:
        slot = AvailabilitySlot(
            id="slot-1",
            tenant_id=tenant_id,
            service_id=service_id,
            starts_at=datetime(2026, 11, 11, 15, tzinfo=timezone.utc),
            ends_at=datetime(2026, 11, 11, 16, tzinfo=timezone.utc),
        )
        return [slot] if starts_after < slot.starts_at < ends_before else []

    async def create_booking(self, **values: object) -> BookingResult:
        self.created = values
        return BookingResult(
            appointment_id="appointment-1",
            status="pending_payment",
            checkout_url="https://www.mercadopago.com.co/checkout/redirect",
        )


class FakeWebhookService:
    def __init__(self) -> None:
        self.notification: dict[str, object] | None = None

    async def execute(self, **values: object) -> bool:
        self.notification = values
        if values.get("signature_header") == "invalid":
            raise ValueError("Invalid notification")
        return True


def configured_app() -> tuple[TestClient, FakeBookingService, FakeWebhookService]:
    booking = FakeBookingService()
    webhook = FakeWebhookService()
    settings = Settings(
        database_url="postgresql+asyncpg://app:app@localhost/app",
        mercado_pago_access_token="test-access-token",
        mercado_pago_webhook_secret="test-webhook-secret",
            rabbitmq_url="amqp://app:app@localhost:5672/",
        frontend_origins=("https://booking.example",),
    )
    return (
        TestClient(
            create_app(
                settings,
                booking_service=booking,  # type: ignore[arg-type]
                payment_webhook_service=webhook,  # type: ignore[arg-type]
            )
        ),
        booking,
        webhook,
    )


def test_booking_routes_use_tenant_scoped_application_service() -> None:
    client, booking, _ = configured_app()
    with client:
        response = client.get("/api/v1/workshops/workshop-7/services")
        assert response.status_code == 200
        assert response.json()[0]["id"] == "service-1"
        assert booking.requested_tenant == "workshop-7"

        availability = client.get(
            "/api/v1/workshops/workshop-7/availability",
            params={
                "service_id": "service-1",
                "starts_after": "2026-11-10T00:00:00Z",
                "ends_before": "2026-11-12T00:00:00Z",
            },
        )
        assert availability.status_code == 200
        assert availability.json()[0]["starts_at"].startswith("2026-11-11T15:00:00")

        created = client.post(
            "/api/v1/workshops/workshop-7/appointments",
            json={
                "service_id": "service-1",
                "starts_at": "2026-11-11T15:00:00Z",
                "customer_name": "Ana",
                "customer_phone": "+573001112233",
            },
        )
        assert created.status_code == 201, created.text
        assert created.json()["status"] == "pending_payment"
        assert booking.created is not None
        assert booking.created["tenant_id"] == "workshop-7"


def test_booking_request_cannot_set_deposit_amount() -> None:
    client, _, _ = configured_app()
    with client:
        response = client.post(
            "/api/v1/workshops/workshop-7/appointments",
            json={
                "service_id": "service-1",
                "starts_at": "2026-11-11T15:00:00Z",
                "customer_name": "Ana",
                "customer_phone": "+573001112233",
                "amount": 1,
            },
        )
    assert response.status_code == 422


def test_webhook_route_passes_raw_signature_headers_and_query_id() -> None:
    client, _, webhook = configured_app()
    with client:
        response = client.post(
            "/api/v1/payments/mercado-pago/webhook?data.id=payment-41",
            headers={"x-signature": "signed-value", "x-request-id": "request-1"},
        )
    assert response.status_code == 200
    assert webhook.notification == {
        "signature_header": "signed-value",
        "request_id": "request-1",
        "payment_id": "payment-41",
    }


def test_unconfigured_app_fails_closed_and_sets_security_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "DATABASE_URL",
        "MERCADO_PAGO_ACCESS_TOKEN",
        "MERCADO_PAGO_WEBHOOK_SECRET",
        "FRONTEND_ORIGINS",
    ):
        monkeypatch.delenv(name, raising=False)

    with TestClient(create_app()) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.headers["x-content-type-options"] == "nosniff"
        unavailable = client.get("/api/v1/workshops/workshop-1/services")
        webhook = client.post("/api/v1/payments/mercado-pago/webhook?data.id=1")

    assert unavailable.status_code == 503
    assert webhook.status_code == 503


def test_configured_origin_is_allowlisted_without_credentials() -> None:
    client, _, _ = configured_app()
    with client:
        response = client.options(
            "/api/v1/workshops/workshop-7/services",
            headers={
                "Origin": "https://booking.example",
                "Access-Control-Request-Method": "GET",
            },
        )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "https://booking.example"
    assert "access-control-allow-credentials" not in response.headers


def test_real_composition_routes_do_not_return_503_with_database(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    database_url = os.environ.get("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("Set TEST_DATABASE_URL to verify the real application composition")

    monkeypatch.setenv("DATABASE_URL", database_url)
    monkeypatch.setenv("MERCADO_PAGO_ACCESS_TOKEN", "test-access-token")
    monkeypatch.setenv("MERCADO_PAGO_WEBHOOK_SECRET", "test-webhook-secret")
    monkeypatch.setenv("AMQP_URL", "amqp://app:app@127.0.0.1:5672/")
    monkeypatch.setenv("FRONTEND_ORIGINS", "https://booking.example")

    with TestClient(create_app()) as client:
        services = client.get("/api/v1/workshops/workshop-live/services")
        availability = client.get(
            "/api/v1/workshops/workshop-live/availability",
            params={
                "service_id": "missing-service",
                "starts_after": "2026-11-10T00:00:00Z",
                "ends_before": "2026-11-12T00:00:00Z",
            },
        )
        reservation = client.post(
            "/api/v1/workshops/workshop-live/appointments",
            json={
                "service_id": "missing-service",
                "starts_at": "2026-11-11T15:00:00Z",
                "customer_name": "Ana",
                "customer_phone": "+573001112233",
            },
        )
        webhook = client.post(
            "/api/v1/payments/mercado-pago/webhook?data.id=payment-live",
            headers={"x-signature": "ts=1,v1=invalid", "x-request-id": "request-live"},
        )

    assert services.status_code == 200, services.text
    assert availability.status_code == 404, availability.text
    assert reservation.status_code == 404, reservation.text
    assert webhook.status_code == 401, webhook.text
