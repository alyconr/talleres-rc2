import asyncio
import json
import logging
from dataclasses import dataclass
from typing import Any

import aio_pika

from app.modules.conversations.application.deliver_confirmation import (
    DeliverAppointmentConfirmation,
)
from app.modules.conversations.domain.appointment_confirmation import DeliveryResult

logger = logging.getLogger(__name__)
QUEUE_NAME = "whatsapp.appointment-confirmations"


@dataclass(frozen=True, slots=True)
class RabbitMqConfirmationQueue:
    url: str

    async def publish_confirmation(
        self, *, tenant_id: str, appointment_id: str
    ) -> None:
        connection = await aio_pika.connect_robust(self.url, timeout=5)
        try:
            channel = await connection.channel(publisher_confirms=True, on_return_raises=True)
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(
                        {"tenant_id": tenant_id, "appointment_id": appointment_id},
                        separators=(",", ":"),
                    ).encode(),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    message_id=f"appointment-confirmation:{tenant_id}:{appointment_id}",
                ),
                routing_key=queue.name,
                mandatory=True,
            )
        finally:
            await connection.close()

    async def consume_forever(self, worker: DeliverAppointmentConfirmation) -> None:
        connection = await aio_pika.connect_robust(self.url, timeout=5)
        try:
            channel = await connection.channel()
            await channel.set_qos(prefetch_count=1)
            queue = await channel.declare_queue(QUEUE_NAME, durable=True)
            async with queue.iterator() as messages:
                async for message in messages:
                    await self.deliver_message(message, worker)
        finally:
            await connection.close()

    @staticmethod
    async def deliver_message(message: Any, worker: DeliverAppointmentConfirmation) -> None:
        try:
            payload = json.loads(message.body)
            tenant_id = payload.get("tenant_id") if isinstance(payload, dict) else None
            appointment_id = payload.get("appointment_id") if isinstance(payload, dict) else None
            if not (
                isinstance(tenant_id, str)
                and tenant_id
                and isinstance(appointment_id, str)
                and appointment_id
            ):
                await message.reject(requeue=False)
                return
        except (UnicodeDecodeError, json.JSONDecodeError, TypeError):
            await message.reject(requeue=False)
            return

        try:
            result = await worker.execute(
                tenant_id=tenant_id,
                appointment_id=appointment_id,
            )
        except Exception:
            logger.warning("WhatsApp confirmation processing failed")
            await message.nack(requeue=True)
            await asyncio.sleep(2)
            return

        if result is DeliveryResult.RETRY:
            await message.nack(requeue=True)
            await asyncio.sleep(2)
            return
        await message.ack()


def build_confirmation_queue(url: str) -> RabbitMqConfirmationQueue:
    return RabbitMqConfirmationQueue(url)
