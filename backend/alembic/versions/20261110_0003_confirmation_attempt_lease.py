"""Track confirmation worker leases for safe message retries."""

from alembic import op
import sqlalchemy as sa

revision = "20261110_0003"
down_revision = "20261110_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "appointment_confirmation_outbox",
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("appointment_confirmation_outbox", "attempted_at")
