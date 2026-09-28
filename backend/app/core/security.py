from datetime import UTC, datetime, timedelta
from hashlib import sha256
from secrets import token_urlsafe
from uuid import UUID

import jwt
from pwdlib import PasswordHash

from app.core.config import get_settings

password_hash = PasswordHash.recommended()
_DUMMY_HASH = password_hash.hash("ManaWorks dummy password value")


def hash_password(value: str) -> str:
    return password_hash.hash(value)


def verify_password(value: str, stored_hash: str | None) -> bool:
    return password_hash.verify(value, stored_hash or _DUMMY_HASH)


def new_secret() -> str:
    return token_urlsafe(48)


def hash_secret(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def create_access_token(user_id: UUID, session_id: UUID) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    return jwt.encode(
        {
            "sub": str(user_id),
            "sid": str(session_id),
            "typ": "access",
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
            "iss": "manaworks",
        },
        settings.jwt_secret,
        algorithm="HS256",
    )


def decode_access_token(value: str) -> tuple[UUID, UUID]:
    payload = jwt.decode(value, get_settings().jwt_secret, algorithms=["HS256"], issuer="manaworks")
    if payload.get("typ") != "access":
        raise jwt.InvalidTokenError("Not an access token")
    return UUID(payload["sub"]), UUID(payload["sid"])