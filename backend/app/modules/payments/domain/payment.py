from dataclasses import dataclass
from decimal import Decimal
from enum import StrEnum
from urllib.parse import urlsplit


class PaymentStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REFUNDED = "refunded"


@dataclass(frozen=True, slots=True)
class PaymentCheckout:
    appointment_id: str
    tenant_id: str
    preference_id: str
    checkout_url: str
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not all((self.appointment_id, self.tenant_id, self.preference_id, self.checkout_url)):
            raise ValueError("Payment checkout identifiers and URL must not be empty")
        if not self.amount.is_finite() or self.amount <= 0:
            raise ValueError("Payment amount must be positive and finite")
        if len(self.currency) != 3 or not self.currency.isalpha() or self.currency != self.currency.upper():
            raise ValueError("Currency must be a three-letter uppercase code")
        parsed_url = urlsplit(self.checkout_url)
        hostname = parsed_url.hostname or ""
        if parsed_url.scheme != "https" or not (
            hostname == "mercadopago.com.co"
            or hostname.endswith(".mercadopago.com.co")
            or hostname == "mercadopago.com"
            or hostname.endswith(".mercadopago.com")
        ):
            raise ValueError("Checkout URL must point to Mercado Pago over HTTPS")


@dataclass(frozen=True, slots=True)
class ProviderPayment:
    payment_id: str
    external_reference: str
    status: PaymentStatus
    amount: Decimal
    currency: str

    def __post_init__(self) -> None:
        if not self.payment_id or not self.external_reference:
            raise ValueError("Provider payment identifiers must not be empty")
        if not self.amount.is_finite() or self.amount < 0:
            raise ValueError("Provider payment amount must be non-negative and finite")
