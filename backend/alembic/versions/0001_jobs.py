"""Create the initial public jobs table."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_jobs"
down_revision = None
branch_labels = None
depends_on = None

job_status = postgresql.ENUM("DRAFT", "PUBLISHED", "CLOSED", "ARCHIVED", name="job_status", create_type=False)


def upgrade() -> None:
    bind = op.get_bind()
    job_status.create(bind, checkfirst=True)
    op.create_table(
        "jobs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("company", sa.String(length=180), nullable=False),
        sa.Column("company_mark", sa.String(length=8), nullable=False),
        sa.Column("company_tone", sa.String(length=32), nullable=False),
        sa.Column("location", sa.String(length=180), nullable=False),
        sa.Column("mode", sa.String(length=16), nullable=False),
        sa.Column("employment_type", sa.String(length=32), nullable=False),
        sa.Column("experience", sa.String(length=80), nullable=False),
        sa.Column("salary", sa.String(length=80), nullable=True),
        sa.Column("salary_value", sa.Integer(), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("responsibilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("requirements", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", job_status, nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_jobs_status_created_at", "jobs", ["status", "created_at"])
    op.create_index("ix_jobs_location", "jobs", ["location"])


def downgrade() -> None:
    op.drop_index("ix_jobs_location", table_name="jobs")
    op.drop_index("ix_jobs_status_created_at", table_name="jobs")
    op.drop_table("jobs")
    job_status.drop(op.get_bind(), checkfirst=True)