from dataclasses import dataclass

from app.modules.conversations.application.ports import ConfirmationOutbox, WhatsAppSender
from app.modules.conversations.domain.appointment_confirmation import DeliveryResult


@dataclass(frozen=True, slots=True)
class DeliverAppointmentConfirmation:
    outbox: ConfirmationOutbox
    sender: WhatsAppSender
    max_attempts: int = 5

    async def execute(self, *, tenant_id: str, appointment_id: str) -> DeliveryResult:
        delivery = await self.outbox.claim_for_delivery(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
        )
        if delivery is None:
            status = await self.outbox.delivery_status(
                tenant_id=tenant_id,
                appointment_id=appointment_id,
            )
            return (
                DeliveryResult.RETRY
                if status in {"queued", "sending"}
                else DeliveryResult.DUPLICATE
            )

        try:
            provider_message_id = await self.sender.send_confirmation(
                recipient_phone=delivery.recipient_phone,
                message=delivery.message,
                idempotency_key=delivery.idempotency_key,
            )
            if not provider_message_id.strip():
                raise ValueError("WhatsApp sender returned an empty message identifier")
        except Exception:
            retry = await self.outbox.record_failure(
                tenant_id=tenant_id,
                appointment_id=appointment_id,
                max_attempts=self.max_attempts,
            )
            return DeliveryResult.RETRY if retry else DeliveryResult.FAILED

        await self.outbox.mark_sent(
            tenant_id=tenant_id,
            appointment_id=appointment_id,
            provider_message_id=provider_message_id,
        )
        return DeliveryResult.SENT
