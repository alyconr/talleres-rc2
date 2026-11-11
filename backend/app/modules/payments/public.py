from app.modules.payments.application.create_checkout import CreateCheckout
from app.modules.payments.application.ports import (
    AppointmentConfirmer,
    PaymentProvider,
    PaymentStore,
    WebhookSignatureVerifier,
)
from app.modules.payments.application.process_payment_webhook import ProcessPaymentWebhook
from app.modules.payments.domain.payment import PaymentCheckout, PaymentStatus, ProviderPayment
from app.modules.payments.infrastructure.mercado_pago import MercadoPagoGateway
from app.modules.payments.infrastructure.mercado_pago_webhooks import (
    MercadoPagoWebhookSignatureVerifier,
)
from app.modules.payments.infrastructure.sqlalchemy_payment_store import SqlAlchemyPaymentStore
from app.modules.payments.api.routes import router


def build_payment_provider(access_token: str) -> PaymentProvider:
    return MercadoPagoGateway(access_token)


def build_payment_store(sessions) -> PaymentStore:
    return SqlAlchemyPaymentStore(sessions)


def build_webhook_verifier(secret: str) -> WebhookSignatureVerifier:
    return MercadoPagoWebhookSignatureVerifier(secret)

__all__ = [
    "CreateCheckout",
    "ProcessPaymentWebhook",
    "AppointmentConfirmer",
    "PaymentCheckout",
    "PaymentProvider",
    "PaymentStore",
    "WebhookSignatureVerifier",
    "build_payment_provider",
    "build_payment_store",
    "build_webhook_verifier",
    "router",
    "PaymentStatus",
    "ProviderPayment",
]
