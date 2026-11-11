from decimal import Decimal
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from app.modules.conversations.public import AppointmentConfirmation
from app.modules.payments.domain.payment import ProviderPayment
from app.modules.payments.domain.payment import PaymentCheckout


class PaymentProvider(Protocol):
    async def create_checkout(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> tuple[str, str]: ...

    async def get_payment(self, payment_id: str) -> ProviderPayment: ...


class PaymentStore(Protocol):
    async def get_checkout(self, appointment_id: str) -> PaymentCheckout | None: ...

    async def save_checkout_if_absent(
        self, checkout: PaymentCheckout
    ) -> PaymentCheckout: ...

    async def record_approved_payment_if_new(
        self,
        payment: ProviderPayment,
        *,
        tenant_id: str,
        appointment_id: str,
        transaction: object,
    ) -> None: ...


class AppointmentConfirmer(Protocol):
    async def confirm_after_approved_payment(
        self, *, tenant_id: str, appointment_id: str, transaction: object
    ) -> AppointmentConfirmation | None: ...


class PaymentTransactionManager(Protocol):
    def transaction(self) -> AbstractAsyncContextManager[object]: ...


class WebhookSignatureVerifier(Protocol):
    def verify(
        self,
        *,
        signature_header: str | None,
        request_id: str | None,
        data_id: str | None,
    ) -> bool: ...
