"""Create tenant-scoped catalog, reservation and payment tables."""

from alembic import op
import sqlalchemy as sa

revision = "20261109_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "services",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("duration_minutes", sa.Integer(), nullable=False),
        sa.Column("deposit_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("currency", sa.String(3), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("id", "tenant_id", name="uq_services_id_tenant"),
    )
    op.create_index("ix_services_tenant_id", "services", ["tenant_id"])
    op.create_table(
        "availability_slots",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("service_id", sa.String(36), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(
            ["service_id", "tenant_id"],
            ["services.id", "services.tenant_id"],
            name="fk_availability_service_tenant",
        ),
        sa.UniqueConstraint("id", "tenant_id", "service_id", name="uq_availability_id_tenant_service"),
    )
    op.create_index("ix_availability_slots_tenant_id", "availability_slots", ["tenant_id"])
    op.create_table(
        "customers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("phone", sa.String(32), nullable=False),
        sa.UniqueConstraint("id", "tenant_id", name="uq_customers_id_tenant"),
        sa.UniqueConstraint("tenant_id", "phone", name="uq_customers_tenant_phone"),
    )
    op.create_index("ix_customers_tenant_id", "customers", ["tenant_id"])
    op.create_table(
        "appointments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("customer_id", sa.String(36), nullable=False),
        sa.Column("service_id", sa.String(36), nullable=False),
        sa.Column("availability_id", sa.String(36), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="pending_payment"),
        sa.ForeignKeyConstraint(
            ["customer_id", "tenant_id"],
            ["customers.id", "customers.tenant_id"],
            name="fk_appointments_customer_tenant",
        ),
        sa.ForeignKeyConstraint(
            ["service_id", "tenant_id"],
            ["services.id", "services.tenant_id"],
            name="fk_appointments_service_tenant",
        ),
        sa.ForeignKeyConstraint(
            ["availability_id", "tenant_id", "service_id"],
            ["availability_slots.id", "availability_slots.tenant_id", "availability_slots.service_id"],
            name="fk_appointments_availability_tenant_service",
        ),
        sa.UniqueConstraint("id", "tenant_id", name="uq_appointments_id_tenant"),
        sa.UniqueConstraint("availability_id", name="uq_appointments_availability"),
        sa.CheckConstraint(
            "status IN ('pending_payment', 'confirmed', 'completed', 'cancelled')",
            name="ck_appointments_status",
        ),
    )
    op.create_index("ix_appointments_tenant_id", "appointments", ["tenant_id"])
    op.create_table(
        "payment_checkouts",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("appointment_id", sa.String(36), nullable=False),
        sa.Column("preference_id", sa.String(128), nullable=False),
        sa.Column("checkout_url", sa.String(2048), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            name="fk_payment_checkouts_appointment_tenant",
        ),
        sa.UniqueConstraint("appointment_id", name="uq_payment_checkouts_appointment"),
        sa.UniqueConstraint("preference_id", name="uq_payment_checkouts_preference"),
    )
    op.create_index("ix_payment_checkouts_tenant_id", "payment_checkouts", ["tenant_id"])
    op.create_table(
        "payments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("appointment_id", sa.String(36), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False, server_default="mercado_pago"),
        sa.Column("provider_payment_id", sa.String(128), nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False),
        sa.Column("status", sa.String(32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            name="fk_payments_appointment_tenant",
        ),
        sa.UniqueConstraint("provider_payment_id", name="uq_payments_provider_payment_id"),
        sa.CheckConstraint(
            "status IN ('pending', 'approved', 'rejected', 'refunded')",
            name="ck_payments_status",
        ),
    )
    op.create_index("ix_payments_tenant_id", "payments", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("ix_payments_tenant_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_payment_checkouts_tenant_id", table_name="payment_checkouts")
    op.drop_table("payment_checkouts")
    op.drop_index("ix_appointments_tenant_id", table_name="appointments")
    op.drop_table("appointments")
    op.drop_index("ix_customers_tenant_id", table_name="customers")
    op.drop_table("customers")
    op.drop_index("ix_availability_slots_tenant_id", table_name="availability_slots")
    op.drop_table("availability_slots")
    op.drop_index("ix_services_tenant_id", table_name="services")
    op.drop_table("services")
