from typing import Annotated, cast

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.modules.payments.application.process_payment_webhook import ProcessPaymentWebhook

router = APIRouter(prefix="/api/v1/payments/mercado-pago", tags=["payments"])


def get_payment_webhook_service(request: Request) -> ProcessPaymentWebhook:
    service = getattr(request.app.state, "payment_webhook_service", None)
    if service is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is unavailable",
        )
    return cast(ProcessPaymentWebhook, service)


@router.post("/webhook", status_code=status.HTTP_200_OK)
async def payment_webhook(
    request: Request,
    payment_service: Annotated[ProcessPaymentWebhook, Depends(get_payment_webhook_service)],
) -> dict[str, str]:
    payment_id = request.query_params.get("data.id")
    try:
        await payment_service.execute(
            signature_header=request.headers.get("x-signature"),
            request_id=request.headers.get("x-request-id"),
            payment_id=payment_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid notification") from exc
    return {"status": "received"}
