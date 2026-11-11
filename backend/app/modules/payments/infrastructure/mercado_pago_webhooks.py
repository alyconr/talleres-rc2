from dataclasses import dataclass

from app.modules.payments.infrastructure.webhook_signature import verify_webhook_signature


@dataclass(frozen=True, slots=True)
class MercadoPagoWebhookSignatureVerifier:
    secret: str

    def verify(
        self,
        *,
        signature_header: str | None,
        request_id: str | None,
        data_id: str | None,
    ) -> bool:
        return verify_webhook_signature(
            signature_header=signature_header,
            request_id=request_id,
            data_id=data_id,
            secret=self.secret,
        )
