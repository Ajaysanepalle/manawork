"""Store usernames and login tracking fields for users."""

from alembic import op
import sqlalchemy as sa

revision = "0003_user_tracking"
down_revision = "0002_auth"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=80), nullable=True))
    op.add_column("users", sa.Column("picture_url", sa.String(length=500), nullable=True))
    op.add_column("users", sa.Column("signup_method", sa.String(length=24), nullable=False, server_default="password"))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("last_login_method", sa.String(length=24), nullable=True))
    op.add_column("users", sa.Column("last_login_ip", sa.String(length=64), nullable=True))
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.alter_column("users", "signup_method", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "last_login_method")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "signup_method")
    op.drop_column("users", "picture_url")
    op.drop_column("users", "username")
