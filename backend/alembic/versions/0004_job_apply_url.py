"""Add external application URLs to jobs."""

from alembic import op
import sqlalchemy as sa

revision = "0004_job_apply_url"
down_revision = "0003_user_tracking"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("apply_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "apply_url")