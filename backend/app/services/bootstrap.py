from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.user import User


def seed_admin() -> None:
    settings = get_settings()
    username = settings.admin_username.strip().lower()
    if not username or not settings.admin_password:
        return
    with SessionLocal() as db:
        admin = db.scalar(select(User).where(User.username == username))
        if admin:
            admin.password_hash = hash_password(settings.admin_password)
            admin.role = "ADMIN"
            admin.is_active = True
            admin.full_name = admin.full_name or username.title()
        else:
            db.add(
                User(
                    username=username,
                    email=f"{username}@manaworks.local",
                    full_name=username.title(),
                    password_hash=hash_password(settings.admin_password),
                    role="ADMIN",
                    email_verified=True,
                    signup_method="admin_seed",
                )
            )
        db.commit()
