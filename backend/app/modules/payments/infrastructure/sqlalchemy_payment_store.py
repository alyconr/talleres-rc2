from uuid import uuid4
from typing import cast

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.modules.payments.domain.payment import PaymentCheckout, PaymentStatus, ProviderPayment
from app.modules.payments.infrastructure.models import PaymentCheckoutRecord, PaymentRecord


class SqlAlchemyPaymentStore:
    def __init__(self, sessions: async_sessionmaker[AsyncSession]) -> None:
        self._sessions = sessions

    async def get_checkout(self, appointment_id: str) -> PaymentCheckout | None:
        async with self._sessions() as session:
            record = await session.scalar(
                select(PaymentCheckoutRecord).where(
                    PaymentCheckoutRecord.appointment_id == appointment_id
                )
            )
            return self._checkout(record) if record else None

    async def save_checkout_if_absent(
        self, checkout: PaymentCheckout
    ) -> PaymentCheckout:
        try:
            async with self._sessions() as session, session.begin():
                record = await session.scalar(
                    select(PaymentCheckoutRecord)
                    .where(PaymentCheckoutRecord.appointment_id == checkout.appointment_id)
                    .with_for_update()
                )
                if record is not None:
                    return self._existing_checkout(record, checkout)
                session.add(
                    PaymentCheckoutRecord(
                        id=str(uuid4()),
                        tenant_id=checkout.tenant_id,
                        appointment_id=checkout.appointment_id,
                        preference_id=checkout.preference_id,
                        checkout_url=checkout.checkout_url,
                        amount=checkout.amount,
                        currency=checkout.currency,
                    )
                )
                await session.flush()
                return checkout
        except IntegrityError:
            existing = await self.get_checkout(checkout.appointment_id)
            if existing is None:
                raise
            return self._existing_checkout_values(existing, checkout)

    async def record_approved_payment_if_new(
        self,
        payment: ProviderPayment,
        *,
        tenant_id: str,
        appointment_id: str,
        transaction: object,
    ) -> None:
        session = cast(AsyncSession, transaction)
        checkout = await session.scalar(
            select(PaymentCheckoutRecord)
            .where(
                PaymentCheckoutRecord.appointment_id == appointment_id,
                PaymentCheckoutRecord.tenant_id == tenant_id,
            )
            .with_for_update()
        )
        if checkout is None:
            raise LookupError("Payment checkout not found")
        if payment.amount != checkout.amount or payment.currency != checkout.currency:
            raise ValueError("Payment does not match checkout")

        inserted_id = await session.scalar(
            insert(PaymentRecord)
            .values(
                id=str(uuid4()),
                tenant_id=tenant_id,
                appointment_id=appointment_id,
                provider="mercado_pago",
                provider_payment_id=payment.payment_id,
                amount=payment.amount,
                currency=payment.currency,
                status=PaymentStatus.APPROVED.value,
            )
            .on_conflict_do_nothing(index_elements=["provider_payment_id"])
            .returning(PaymentRecord.id)
        )
        if inserted_id is None:
            existing = await session.scalar(
                select(PaymentRecord).where(
                    PaymentRecord.provider_payment_id == payment.payment_id
                )
            )
            if existing is None:
                raise RuntimeError("Could not record provider payment")
            self._ensure_same_payment(existing, payment, tenant_id, appointment_id)

    @staticmethod
    def _checkout(record: PaymentCheckoutRecord) -> PaymentCheckout:
        return PaymentCheckout(
            appointment_id=record.appointment_id,
            tenant_id=record.tenant_id,
            preference_id=record.preference_id,
            checkout_url=record.checkout_url,
            amount=record.amount,
            currency=record.currency,
        )

    @staticmethod
    def _existing_checkout(
        record: PaymentCheckoutRecord, checkout: PaymentCheckout
    ) -> PaymentCheckout:
        return SqlAlchemyPaymentStore._existing_checkout_values(
            SqlAlchemyPaymentStore._checkout(record), checkout
        )

    @staticmethod
    def _existing_checkout_values(
        existing: PaymentCheckout, checkout: PaymentCheckout
    ) -> PaymentCheckout:
        if (
            existing.tenant_id != checkout.tenant_id
            or existing.amount != checkout.amount
            or existing.currency != checkout.currency
        ):
            raise ValueError("A checkout already exists with different tenant or deposit")
        return existing

    @staticmethod
    def _ensure_same_payment(
        existing: PaymentRecord,
        payment: ProviderPayment,
        tenant_id: str,
        appointment_id: str,
    ) -> None:
        if (
            existing.tenant_id != tenant_id
            or existing.appointment_id != appointment_id
            or existing.amount != payment.amount
            or existing.currency != payment.currency
            or existing.status != PaymentStatus.APPROVED.value
        ):
            raise ValueError("Provider payment identifier was reused with different data")
