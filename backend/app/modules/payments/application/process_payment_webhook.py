from dataclasses import dataclass

from app.modules.conversations.public import ConfirmationOutbox, ConfirmationPublisher
from app.modules.payments.application.ports import (
    AppointmentConfirmer,
    PaymentProvider,
    PaymentStore,
    PaymentTransactionManager,
    WebhookSignatureVerifier,
)
from app.modules.payments.domain.payment import PaymentStatus


@dataclass(frozen=True, slots=True)
class ProcessPaymentWebhook:
    provider: PaymentProvider
    store: PaymentStore
    appointment_confirmer: AppointmentConfirmer
    confirmation_outbox: ConfirmationOutbox
    confirmation_publisher: ConfirmationPublisher
    signature_verifier: WebhookSignatureVerifier
    transaction_manager: PaymentTransactionManager

    async def execute(
        self,
        *,
        signature_header: str | None,
        request_id: str | None,
        payment_id: str | None,
    ) -> bool:
        if not self.signature_verifier.verify(
            signature_header=signature_header,
            request_id=request_id,
            data_id=payment_id,
        ):
            raise ValueError("Invalid payment notification")

        if payment_id is None:
            raise ValueError("Invalid payment notification")
        payment = await self.provider.get_payment(payment_id)
        if payment.payment_id != payment_id or payment.status is not PaymentStatus.APPROVED:
            return False

        checkout = await self.store.get_checkout(payment.external_reference)
        if checkout is None:
            return False
        if payment.amount != checkout.amount or payment.currency != checkout.currency:
            raise ValueError("Approved payment does not match the checkout")

        async with self.transaction_manager.transaction() as transaction:
            await self.store.record_approved_payment_if_new(
                payment,
                tenant_id=checkout.tenant_id,
                appointment_id=checkout.appointment_id,
                transaction=transaction,
            )
            confirmation = await self.appointment_confirmer.confirm_after_approved_payment(
                tenant_id=checkout.tenant_id,
                appointment_id=checkout.appointment_id,
                transaction=transaction,
            )
            if confirmation is not None:
                await self.confirmation_outbox.enqueue_if_absent(
                    confirmation,
                    transaction=transaction,
                )
        if confirmation is not None:
            await self.confirmation_publisher.publish_confirmation(
                tenant_id=checkout.tenant_id,
                appointment_id=checkout.appointment_id,
            )
        return True
