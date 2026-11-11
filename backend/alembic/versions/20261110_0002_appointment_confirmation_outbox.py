"""Persist idempotent WhatsApp appointment confirmations."""

from alembic import op
import sqlalchemy as sa

revision = "20261110_0002"
down_revision = "20261109_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "appointment_confirmation_outbox",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("appointment_id", sa.String(36), nullable=False),
        sa.Column("idempotency_key", sa.String(200), nullable=False),
        sa.Column("recipient_phone", sa.String(32), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="queued"),
        sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("provider_message_id", sa.String(128), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["appointment_id", "tenant_id"],
            ["appointments.id", "appointments.tenant_id"],
            name="fk_confirmation_outbox_appointment_tenant",
        ),
        sa.UniqueConstraint(
            "tenant_id", "appointment_id", name="uq_confirmation_outbox_appointment"
        ),
        sa.UniqueConstraint("idempotency_key", name="uq_confirmation_outbox_idempotency"),
        sa.CheckConstraint(
            "status IN ('queued', 'sending', 'sent', 'failed')",
            name="ck_confirmation_outbox_status",
        ),
    )
    op.create_index(
        "ix_appointment_confirmation_outbox_tenant_id",
        "appointment_confirmation_outbox",
        ["tenant_id"],
    )
    op.create_index(
        "ix_appointment_confirmation_outbox_status",
        "appointment_confirmation_outbox",
        ["status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_appointment_confirmation_outbox_status",
        table_name="appointment_confirmation_outbox",
    )
    op.drop_index(
        "ix_appointment_confirmation_outbox_tenant_id",
        table_name="appointment_confirmation_outbox",
    )
    op.drop_table("appointment_confirmation_outbox")
