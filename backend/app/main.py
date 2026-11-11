import os
import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from contextlib import suppress

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.modules.catalog.public import build_catalog_reader
from app.modules.conversations.public import (
    DeliverAppointmentConfirmation,
    WhatsAppSender,
    build_confirmation_outbox,
    build_confirmation_queue,
)
from app.modules.payments.public import (
    CreateCheckout,
    ProcessPaymentWebhook,
    build_payment_provider,
    build_payment_store,
    build_webhook_verifier,
    router as payment_router,
)
from app.modules.reservations.public import (
    BookingService,
    CreatePendingAppointment,
    build_reservation_store,
    router as reservation_router,
)
from app.shared.database import (
    SqlAlchemyTransactionManager,
    create_database_engine,
    create_session_factory,
)
from app.shared.settings import Settings


def create_app(
    settings: Settings | None = None,
    *,
    booking_service: BookingService | None = None,
    payment_webhook_service: ProcessPaymentWebhook | None = None,
    whatsapp_sender: WhatsAppSender | None = None,
) -> FastAPI:
    origins = (
        settings.frontend_origins
        if settings is not None
        else tuple(
            origin.strip()
            for origin in os.environ.get("FRONTEND_ORIGINS", "").split(",")
            if origin.strip()
        )
    )

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncIterator[None]:
        if booking_service is not None or payment_webhook_service is not None:
            application.state.booking_service = booking_service
            application.state.payment_webhook_service = payment_webhook_service
            yield
            return
        try:
            config = settings or Settings.from_environment()
        except RuntimeError:
            application.state.booking_service = None
            application.state.payment_webhook_service = None
            yield
            return

        engine = create_database_engine(config.database_url)
        sessions = create_session_factory(engine)
        confirmation_worker_task: asyncio.Task[None] | None = None
        try:
            async with engine.connect() as connection:
                await connection.execute(text("SELECT 1"))

            catalog = build_catalog_reader(sessions)
            reservations = build_reservation_store(sessions, catalog)
            payments = build_payment_store(sessions)
            provider = build_payment_provider(config.mercado_pago_access_token)
            confirmation_queue = build_confirmation_queue(config.rabbitmq_url)
            confirmation_outbox = build_confirmation_outbox(sessions)
            checkout = CreateCheckout(provider=provider, store=payments)
            application.state.booking_service = BookingService(
                catalog=catalog,
                reservations=reservations,
                create_checkout=checkout,
                create_pending_appointment=CreatePendingAppointment(reservations),
            )
            application.state.payment_webhook_service = ProcessPaymentWebhook(
                provider=provider,
                store=payments,
                appointment_confirmer=reservations,
                confirmation_outbox=confirmation_outbox,
                confirmation_publisher=confirmation_queue,
                signature_verifier=build_webhook_verifier(
                    config.mercado_pago_webhook_secret
                ),
                transaction_manager=SqlAlchemyTransactionManager(sessions),
            )
            if whatsapp_sender is not None:
                confirmation_worker = DeliverAppointmentConfirmation(
                    outbox=confirmation_outbox,
                    sender=whatsapp_sender,
                )
                confirmation_worker_task = asyncio.create_task(
                    confirmation_queue.consume_forever(confirmation_worker)
                )
            application.state.database_engine = engine
            yield
        finally:
            if confirmation_worker_task is not None:
                confirmation_worker_task.cancel()
                with suppress(asyncio.CancelledError):
                    await confirmation_worker_task
            await engine.dispose()

    app = FastAPI(title="Talleres API", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(origins),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["content-type", "x-request-id", "x-signature"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        return response

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(reservation_router)
    app.include_router(payment_router)
    return app


app = create_app()
