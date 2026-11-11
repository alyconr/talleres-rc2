from dataclasses import dataclass
from decimal import Decimal

from app.modules.payments.domain.payment import PaymentCheckout
from app.modules.payments.application.ports import PaymentProvider, PaymentStore


@dataclass(frozen=True, slots=True)
class CreateCheckout:
    provider: PaymentProvider
    store: PaymentStore

    async def execute(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        appointment_status: str,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> PaymentCheckout:
        if appointment_status != "pending_payment":
            raise ValueError("Only appointments awaiting payment can start checkout")
        if not title.strip() or not amount.is_finite() or amount <= 0:
            raise ValueError("A valid service title and deposit amount are required")
        if len(currency) != 3 or not currency.isalpha() or currency != currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")

        existing = await self.store.get_checkout(appointment_id)
        if existing is not None:
            if existing.amount != amount or existing.currency != currency:
                raise ValueError("A checkout already exists with a different deposit")
            return existing

        preference_id, checkout_url = await self.provider.create_checkout(
            appointment_id=appointment_id,
            tenant_id=tenant_id,
            title=title,
            amount=amount,
            currency=currency,
        )
        checkout = PaymentCheckout(
            appointment_id=appointment_id,
            tenant_id=tenant_id,
            preference_id=preference_id,
            checkout_url=checkout_url,
            amount=amount,
            currency=currency,
        )
        return await self.store.save_checkout_if_absent(checkout)
