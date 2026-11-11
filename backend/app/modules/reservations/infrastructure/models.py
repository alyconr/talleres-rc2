from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKeyConstraint, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database import Base


class CustomerRecord(Base):
    __tablename__ = "customers"
    __table_args__ = (
        UniqueConstraint("id", "tenant_id", name="uq_customers_id_tenant"),
        UniqueConstraint("tenant_id", "phone", name="uq_customers_tenant_phone"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), nullable=False)


class AppointmentRecord(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["customers.id", "customers.tenant_id"],
            name="fk_appointments_customer_tenant",
        ),
        ForeignKeyConstraint(
            ["service_id", "tenant_id"],
            ["services.id", "services.tenant_id"],
            name="fk_appointments_service_tenant",
        ),
        ForeignKeyConstraint(
            ["availability_id", "tenant_id", "service_id"],
            ["availability_slots.id", "availability_slots.tenant_id", "availability_slots.service_id"],
            name="fk_appointments_availability_tenant_service",
        ),
        UniqueConstraint("id", "tenant_id", name="uq_appointments_id_tenant"),
        UniqueConstraint("availability_id", name="uq_appointments_availability"),
        CheckConstraint(
            "status IN ('pending_payment', 'confirmed', 'completed', 'cancelled')",
            name="ck_appointments_status",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), nullable=False)
    service_id: Mapped[str] = mapped_column(String(36), nullable=False)
    availability_id: Mapped[str] = mapped_column(String(36), nullable=False)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending_payment")
