from decimal import Decimal, InvalidOperation

import httpx

from app.modules.payments.domain.payment import PaymentStatus, ProviderPayment


class PaymentProviderError(RuntimeError):
    pass


class MercadoPagoGateway:
    _API_URL = "https://api.mercadopago.com"

    def __init__(self, access_token: str) -> None:
        if not access_token:
            raise ValueError("Mercado Pago access token is required")
        self._access_token = access_token

    async def create_checkout(
        self,
        *,
        appointment_id: str,
        tenant_id: str,
        title: str,
        amount: Decimal,
        currency: str,
    ) -> tuple[str, str]:
        payload = {
            "items": [
                {
                    "id": appointment_id,
                    "title": title,
                    "quantity": 1,
                    "currency_id": currency,
                    "unit_price": float(amount),
                }
            ],
            "external_reference": appointment_id,
            "metadata": {"tenant_id": tenant_id},
        }
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                response = await client.post(
                    f"{self._API_URL}/checkout/preferences",
                    headers={"Authorization": f"Bearer {self._access_token}"},
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                preference_id = result["id"]
                checkout_url = result["init_point"]
                if not isinstance(preference_id, str) or not isinstance(checkout_url, str):
                    raise ValueError
                return preference_id, checkout_url
        except (httpx.HTTPError, KeyError, TypeError, ValueError) as exc:
            raise PaymentProviderError("Could not create Mercado Pago checkout") from exc

    async def get_payment(self, payment_id: str) -> ProviderPayment:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
                response = await client.get(
                    f"{self._API_URL}/v1/payments/{payment_id}",
                    headers={"Authorization": f"Bearer {self._access_token}"},
                )
                response.raise_for_status()
                result = response.json()
                status = {
                    "approved": PaymentStatus.APPROVED,
                    "rejected": PaymentStatus.REJECTED,
                    "refunded": PaymentStatus.REFUNDED,
                    "pending": PaymentStatus.PENDING,
                }.get(result["status"], PaymentStatus.PENDING)
                return ProviderPayment(
                    payment_id=str(result["id"]),
                    external_reference=result["external_reference"],
                    status=status,
                    amount=Decimal(str(result["transaction_amount"])),
                    currency=result["currency_id"],
                )
        except (httpx.HTTPError, KeyError, TypeError, ValueError, InvalidOperation) as exc:
            raise PaymentProviderError("Could not retrieve Mercado Pago payment") from exc
