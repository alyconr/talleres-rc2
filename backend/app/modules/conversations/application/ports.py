from typing import Protocol

from app.modules.conversations.domain.appointment_confirmation import (
    AppointmentConfirmation,
    ConfirmationDelivery,
)


class ConfirmationOutbox(Protocol):
    async def enqueue_if_absent(
        self,
        confirmation: AppointmentConfirmation,
        *,
        transaction: object,
    ) -> bool: ...

    async def claim_for_delivery(
        self, *, tenant_id: str, appointment_id: str
    ) -> ConfirmationDelivery | None: ...

    async def delivery_status(self, *, tenant_id: str, appointment_id: str) -> str | None: ...

    async def mark_sent(
        self,
        *,
        tenant_id: str,
        appointment_id: str,
        provider_message_id: str,
    ) -> None: ...

    async def record_failure(
        self, *, tenant_id: str, appointment_id: str, max_attempts: int
    ) -> bool: ...


class WhatsAppSender(Protocol):
    async def send_confirmation(
        self,
        *,
        recipient_phone: str,
        message: str,
        idempotency_key: str,
    ) -> str: ...


class ConfirmationPublisher(Protocol):
    async def publish_confirmation(
        self, *, tenant_id: str, appointment_id: str
    ) -> None: ...
