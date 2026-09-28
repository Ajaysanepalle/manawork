from secrets import compare_digest
from uuid import UUID

import jwt
from fastapi import Cookie, Depends, Header, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token, hash_secret
from app.db.session import get_db
from app.models.user import AuthSession, User


def require_csrf(
    request: Request,
    csrf_header: str | None = Header(default=None, alias="X-CSRF-Token"),
    csrf_cookie: str | None = Cookie(default=None, alias="mw_csrf"),
) -> None:
    settings = get_settings()
    origin = request.headers.get("origin")
    if origin not in settings.allowed_origins:
        raise HTTPException(status_code=403, detail={"success": False, "message": "Request origin is not allowed", "error_code": "INVALID_ORIGIN"})
    if not csrf_header or not csrf_cookie or not compare_digest(csrf_header, csrf_cookie):
        raise HTTPException(status_code=403, detail={"success": False, "message": "Refresh the page and try again", "error_code": "CSRF_VALIDATION_FAILED"})


def get_current_user(
    access_cookie: str | None = Cookie(default=None, alias="mw_access"),
    db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail={"success": False, "message": "Sign in to continue", "error_code": "UNAUTHENTICATED"})
    if not access_cookie:
        raise unauthorized
    try:
        user_id, session_id = decode_access_token(access_cookie)
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise unauthorized from None
    session = db.get(AuthSession, session_id)
    user = db.get(User, user_id)
    import time

    if not session or session.user_id != user_id or session.revoked_at is not None or session.expires_at <= int(time.time()) or not user or not user.is_active:
        raise unauthorized
    return user


def get_active_session(
    access_cookie: str | None = Cookie(default=None, alias="mw_access"),
    db: Session = Depends(get_db),
) -> AuthSession:
    if not access_cookie:
        raise HTTPException(status_code=401, detail={"success": False, "message": "Sign in to continue", "error_code": "UNAUTHENTICATED"})
    try:
        _, session_id = decode_access_token(access_cookie)
    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise HTTPException(status_code=401, detail={"success": False, "message": "Sign in to continue", "error_code": "UNAUTHENTICATED"}) from None
    session = db.get(AuthSession, session_id)
    import time

    if not session or session.revoked_at is not None or session.expires_at <= int(time.time()):
        raise HTTPException(status_code=401, detail={"success": False, "message": "Sign in to continue", "error_code": "UNAUTHENTICATED"})
    return session


def require_admin(user: User = Depends(get_current_user)) -> User:
    if user.role != "ADMIN":
        raise HTTPException(status_code=403, detail={"success": False, "message": "Admin access is required", "error_code": "FORBIDDEN"})
    return user


def enforce_rate_limit(request: Request, action: str, identity: str = "", limit: int = 5, window_seconds: int = 900) -> None:
    import redis

    settings = get_settings()
    client_host = request.client.host if request.client else "unknown"
    key = f"auth-rate:{action}:{hash_secret(client_host + ':' + identity)}"
    try:
        client = redis.Redis.from_url(settings.redis_url, socket_connect_timeout=1, socket_timeout=1, decode_responses=True)
        try:
            count = client.incr(key)
            if count == 1:
                client.expire(key, window_seconds)
        finally:
            client.close()
    except redis.RedisError:
        raise HTTPException(status_code=503, detail={"success": False, "message": "Sign-in is temporarily unavailable", "error_code": "RATE_LIMITER_UNAVAILABLE"}) from None
    if count > limit:
        raise HTTPException(status_code=429, detail={"success": False, "message": "Too many attempts. Please try again later.", "error_code": "RATE_LIMITED"})