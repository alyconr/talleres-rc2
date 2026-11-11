from typing import cast
from uuid import uuid4

from sqlalchemy import and_, case, func, or_, select, text, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.conversations.domain.appointment_confirmation import (
    AppointmentConfirmation,
    ConfirmationDelivery,
)
from app.modules.conversations.infrastructure.models import AppointmentConfirmationRecord


class SqlAlchemyConfirmationOutbox:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def enqueue_if_absent(
        self,
        confirmation: AppointmentConfirmation,
        *,
        transaction: object,
    ) -> bool:
        session = cast(AsyncSession, transaction)
        inserted_id = await session.scalar(
            insert(AppointmentConfirmationRecord)
            .values(
                id=str(uuid4()),
                tenant_id=confirmation.tenant_id,
                appointment_id=confirmation.appointment_id,
                idempotency_key=confirmation.idempotency_key,
                recipient_phone=confirmation.recipient_phone,
                message=confirmation.message,
                status="queued",
                attempt_count=0,
            )
            .on_conflict_do_nothing(
                index_elements=["tenant_id", "appointment_id"]
            )
            .returning(AppointmentConfirmationRecord.id)
        )
        if inserted_id is None:
            return False
        return True

    async def claim_for_delivery(
        self, *, tenant_id: str, appointment_id: str
    ) -> ConfirmationDelivery | None:
        stale_claim = AppointmentConfirmationRecord.attempted_at < (
            func.now() - text("INTERVAL '1 minute'")
        )
        async with self._sessions() as session, session.begin():
            result = await session.execute(
                update(AppointmentConfirmationRecord)
                .where(
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                    AppointmentConfirmationRecord.appointment_id == appointment_id,
                    or_(
                        AppointmentConfirmationRecord.status == "queued",
                        and_(
                            AppointmentConfirmationRecord.status == "sending",
                            stale_claim,
                        ),
                    ),
                )
                .values(
                    status="sending",
                    attempt_count=AppointmentConfirmationRecord.attempt_count + 1,
                    attempted_at=func.now(),
                )
                .returning(
                    AppointmentConfirmationRecord.idempotency_key,
                    AppointmentConfirmationRecord.recipient_phone,
                    AppointmentConfirmationRecord.message,
                    AppointmentConfirmationRecord.attempt_count,
                )
            )
            record = result.one_or_none()
            if record is None:
                return None
            return ConfirmationDelivery(
                idempotency_key=record.idempotency_key,
                recipient_phone=record.recipient_phone,
                message=record.message,
                attempt_count=record.attempt_count,
            )

    async def delivery_status(self, *, tenant_id: str, appointment_id: str) -> str | None:
        async with self._sessions() as session:
            return await session.scalar(
                select(AppointmentConfirmationRecord.status).where(
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                    AppointmentConfirmationRecord.appointment_id == appointment_id,
                )
            )

    async def mark_sent(
        self,
        *,
        tenant_id: str,
        appointment_id: str,
        provider_message_id: str,
    ) -> None:
        async with self._sessions() as session, session.begin():
            result = await session.execute(
                update(AppointmentConfirmationRecord)
                .where(
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                    AppointmentConfirmationRecord.appointment_id == appointment_id,
                    AppointmentConfirmationRecord.status == "sending",
                )
                .values(
                    status="sent",
                    provider_message_id=provider_message_id,
                    sent_at=func.now(),
                )
            )
            if result.rowcount != 1:
                raise LookupError("Confirmation delivery claim was lost")

    async def record_failure(
        self, *, tenant_id: str, appointment_id: str, max_attempts: int
    ) -> bool:
        async with self._sessions() as session, session.begin():
            result = await session.execute(
                update(AppointmentConfirmationRecord)
                .where(
                    AppointmentConfirmationRecord.tenant_id == tenant_id,
                    AppointmentConfirmationRecord.appointment_id == appointment_id,
                    AppointmentConfirmationRecord.status == "sending",
                )
                .values(
                    status=case(
                        (
                            AppointmentConfirmationRecord.attempt_count >= max_attempts,
                            "failed",
                        ),
                        else_="queued",
                    )
                )
                .returning(AppointmentConfirmationRecord.status)
            )
            status = result.scalar_one_or_none()
            if status is None:
                raise LookupError("Confirmation delivery claim was lost")
            return status == "queued"


def build_confirmation_outbox(
    sessions: async_sessionmaker[AsyncSession],
) -> SqlAlchemyConfirmationOutbox:
    return SqlAlchemyConfirmationOutbox(sessions)
