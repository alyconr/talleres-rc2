from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base


class PaymentCheckoutRecord(Base):
    __tablename__ = "payment_checkouts"
    __table_args__ = (
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            name="fk_payment_checkouts_appointment_tenant",
        ),
        UniqueConstraint("appointment_id", name="uq_payment_checkouts_appointment"),
        UniqueConstraint("preference_id", name="uq_payment_checkouts_preference"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    appointment_id: Mapped[str] = mapped_column(String(36), nullable=False)
    preference_id: Mapped[str] = mapped_column(String(128), nullable=False)
    checkout_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PaymentRecord(Base):
    __tablename__ = "payments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            name="fk_payments_appointment_tenant",
        ),
        UniqueConstraint("provider_payment_id", name="uq_payments_provider_payment_id"),
        CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'refunded')",
            name="ck_payments_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    appointment_id: Mapped[str] = mapped_column(String(36), nullable=False)
    provider: Mapped[str] = mapped_column(String(32), nullable=False, default="mercado_pago")
    provider_payment_id: Mapped[str] = mapped_column(String(128), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
