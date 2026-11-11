import asyncio

from app.modules.conversations.domain.appointment_confirmation import (
    ConfirmationDelivery,
    DeliveryResult,
)
from app.modules.conversations.application.deliver_confirmation import (
    DeliverAppointmentConfirmation,
)


class FakeOutbox:
    def __init__(self, *, status: str = "queued") -> None:
        self.status = status
        self.failures: list[int] = []
        self.sent: list[str] = []

    async def enqueue_if_absent(self, *_args, **_kwargs) -> bool:
        raise AssertionError("delivery must not enqueue")

    async def claim_for_delivery(
        self, *, tenant_id: str, appointment_id: str
    ) -> ConfirmationDelivery | None:
        assert tenant_id == "tenant-1"
        assert appointment_id == "appointment-1"
        if self.status != "queued":
            return None
        self.status = "sending"
        return ConfirmationDelivery(
            idempotency_key="appointment-confirmation:tenant-1:appointment-1",
            recipient_phone="+573001234567",
            message="Tu cita fue confirmada.",
            attempt_count=1,
        )

    async def delivery_status(self, *, tenant_id: str, appointment_id: str) -> str:
        return self.status

    async def mark_sent(self, *, tenant_id: str, appointment_id: str, provider_message_id: str) -> None:
        self.sent.append(provider_message_id)
        self.status = "sent"

    async def record_failure(self, *, tenant_id: str, appointment_id: str, max_attempts: int) -> bool:
        self.failures.append(max_attempts)
        self.status = "queued"
        return True


class FakeSender:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.requests: list[tuple[str, str, str]] = []

    async def send_confirmation(
        self,
        *,
        recipient_phone: str,
        message: str,
        idempotency_key: str,
    ) -> str:
        self.requests.append((recipient_phone, message, idempotency_key))
        if self.fail:
            raise RuntimeError("WhatsApp transport unavailable")
        return "provider-message-1"


def test_confirmation_delivery_sends_with_stable_idempotency_key() -> None:
    outbox = FakeOutbox()
    sender = FakeSender()
    worker = DeliverAppointmentConfirmation(outbox=outbox, sender=sender)

    result = asyncio.run(
        worker.execute(tenant_id="tenant-1", appointment_id="appointment-1")
    )

    assert result is DeliveryResult.SENT
    assert sender.requests == [
        (
            "+573001234567",
            "Tu cita fue confirmada.",
            "appointment-confirmation:tenant-1:appointment-1",
        )
    ]
    assert outbox.sent == ["provider-message-1"]


def test_transient_confirmation_delivery_failure_requeues_without_logging_payload() -> None:
    outbox = FakeOutbox()
    worker = DeliverAppointmentConfirmation(outbox=outbox, sender=FakeSender(fail=True))

    result = asyncio.run(
        worker.execute(tenant_id="tenant-1", appointment_id="appointment-1")
    )

    assert result is DeliveryResult.RETRY
    assert outbox.failures == [5]
    assert outbox.status == "queued"


def test_duplicate_confirmation_delivery_does_not_send_again() -> None:
    outbox = FakeOutbox(status="sent")
    sender = FakeSender()
    worker = DeliverAppointmentConfirmation(outbox=outbox, sender=sender)

    result = asyncio.run(
        worker.execute(tenant_id="tenant-1", appointment_id="appointment-1")
    )

    assert result is DeliveryResult.DUPLICATE
    assert sender.requests == []
