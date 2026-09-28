from datetime import UTC, datetime
from secrets import token_urlsafe
from time import time

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.dependencies import enforce_rate_limit, get_current_user, require_csrf
from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, hash_secret, new_secret, verify_password
from app.db.session import get_db
from app.models.user import AuthSession, User
from app.schemas.auth import AdminLogin, PasswordLogin, PasswordSignup

router = APIRouter()
settings = get_settings()
oauth = OAuth()
google_configured = bool(settings.google_client_id and settings.google_client_secret)
if google_configured:
    oauth.register(
        name="google",
        client_id=settings.google_client_id,
        client_secret=settings.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )


def _user_payload(user: User) -> dict[str, str | bool | None]:
    return {
        "id": str(user.id),
        "email": user.email,
        "username": user.username,
        "phone": user.phone,
        "full_name": user.full_name,
        "picture_url": user.picture_url,
        "role": user.role,
        "signup_method": user.signup_method,
        "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
        "last_login_method": user.last_login_method,
    }


def _set_auth_cookies(response: Response, user: User, session: AuthSession, refresh_token: str) -> None:
    access_token = create_access_token(user.id, session.id)
    common = {"secure": settings.secure_cookies, "httponly": True, "samesite": "lax", "path": "/"}
    if settings.auth_cookie_domain:
        common["domain"] = settings.auth_cookie_domain
    response.set_cookie("mw_access", access_token, max_age=settings.access_token_minutes * 60, **common)
    response.set_cookie("mw_refresh", refresh_token, max_age=settings.refresh_token_days * 86400, **common)


def _clear_auth_cookies(response: Response) -> None:
    for name in ("mw_access", "mw_refresh"):
        response.delete_cookie(name, path="/", domain=settings.auth_cookie_domain, secure=settings.secure_cookies, samesite="lax")
    response.delete_cookie("mw_csrf", path="/api/v1/auth", domain=settings.auth_cookie_domain, secure=settings.secure_cookies, samesite="strict")


def _create_session(db: Session, user: User, request: Request, response: Response) -> None:
    refresh_token = new_secret()
    session = AuthSession(
        user_id=user.id,
        refresh_token_hash=hash_secret(refresh_token),
        expires_at=int(time()) + settings.refresh_token_days * 86400,
        user_agent=request.headers.get("user-agent", "")[:512] or None,
    )
    db.add(session)
    db.flush()
    _set_auth_cookies(response, user, session, refresh_token)


def _mark_login(user: User, request: Request, method: str) -> None:
    user.last_login_at = datetime.now(UTC)
    user.last_login_method = method
    user.last_login_ip = request.client.host if request.client else None


def _auth_error(status_code: int, message: str, code: str) -> HTTPException:
    return HTTPException(status_code=status_code, detail={"success": False, "message": message, "error_code": code})


def _complete_login(db: Session, user: User, request: Request, response: Response, method: str) -> dict[str, object]:
    if not user.is_active:
        raise _auth_error(403, "This account is unavailable", "ACCOUNT_DISABLED")
    _mark_login(user, request, method)
    _create_session(db, user, request, response)
    db.commit()
    return {"success": True, "data": {"user": _user_payload(user)}}


@router.get("/csrf")
def csrf_token(response: Response) -> dict[str, object]:
    value = token_urlsafe(32)
    response.set_cookie(
        "mw_csrf",
        value,
        max_age=7200,
        httponly=False,
        secure=settings.secure_cookies,
        samesite="strict",
        path="/api/v1/auth",
        domain=settings.auth_cookie_domain,
    )
    return {"success": True, "data": {"csrf_token": value}}


@router.get("/google/status")
def google_status() -> dict[str, object]:
    return {"success": True, "data": {"configured": google_configured}}


@router.post("/signup", dependencies=[Depends(require_csrf)])
def signup(payload: PasswordSignup, request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, object]:
    enforce_rate_limit(request, "signup", identity=payload.email, limit=8, window_seconds=900)
    existing = db.scalar(select(User).where(User.email == payload.email))
    if existing:
        raise _auth_error(409, "An account with this email already exists. Sign in instead.", "EMAIL_IN_USE")
    user = User(
        email=payload.email,
        full_name=payload.full_name.strip()[:120],
        password_hash=hash_password(payload.password),
        role="USER",
        email_verified=False,
        signup_method="password",
    )
    db.add(user)
    db.flush()
    return _complete_login(db, user, request, response, "password")


@router.post("/login", dependencies=[Depends(require_csrf)])
def login(payload: PasswordLogin, request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, object]:
    identifier = payload.identifier.strip().lower()
    enforce_rate_limit(request, "login", identity=identifier, limit=10, window_seconds=900)
    user = db.scalar(select(User).where(or_(User.email == identifier, User.username == identifier)))
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise _auth_error(401, "Check your email or username and password, then try again.", "INVALID_CREDENTIALS")
    if user.role == "ADMIN":
        raise _auth_error(403, "Use the admin sign-in page for this account.", "ADMIN_LOGIN_REQUIRED")
    return _complete_login(db, user, request, response, "password")


@router.post("/admin/login", dependencies=[Depends(require_csrf)])
def admin_login(payload: AdminLogin, request: Request, response: Response, db: Session = Depends(get_db)) -> dict[str, object]:
    username = payload.username.strip().lower()
    enforce_rate_limit(request, "admin-login", identity=username, limit=8, window_seconds=900)
    user = db.scalar(select(User).where(User.username == username, User.role == "ADMIN"))
    if not user or not user.password_hash or not verify_password(payload.password, user.password_hash):
        raise _auth_error(401, "Admin username or password is incorrect.", "INVALID_CREDENTIALS")
    return _complete_login(db, user, request, response, "password")


@router.post("/refresh", dependencies=[Depends(require_csrf)])
def refresh(
    request: Request,
    response: Response,
    refresh_cookie: str | None = Cookie(default=None, alias="mw_refresh"),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    enforce_rate_limit(request, "refresh", limit=20, window_seconds=900)
    session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_secret(refresh_cookie or "")))
    if not session or session.revoked_at is not None or session.expires_at <= int(time()):
        _clear_auth_cookies(response)
        raise _auth_error(401, "Your session has expired. Please sign in again.", "SESSION_EXPIRED")
    user = db.get(User, session.user_id)
    if not user or not user.is_active:
        session.revoked_at = int(time())
        db.commit()
        _clear_auth_cookies(response)
        raise _auth_error(401, "Sign in to continue", "UNAUTHENTICATED")
    rotated_token = new_secret()
    session.refresh_token_hash = hash_secret(rotated_token)
    _set_auth_cookies(response, user, session, rotated_token)
    db.commit()
    return {"success": True, "data": {"user": _user_payload(user)}}


@router.post("/logout", dependencies=[Depends(require_csrf)])
def logout(
    response: Response,
    refresh_cookie: str | None = Cookie(default=None, alias="mw_refresh"),
    db: Session = Depends(get_db),
) -> dict[str, object]:
    if refresh_cookie:
        session = db.scalar(select(AuthSession).where(AuthSession.refresh_token_hash == hash_secret(refresh_cookie)))
        if session and session.revoked_at is None:
            session.revoked_at = int(time())
            db.commit()
    _clear_auth_cookies(response)
    return {"success": True, "message": "Signed out", "data": {}}


@router.get("/me")
def current_user(user: User = Depends(get_current_user)) -> dict[str, object]:
    return {"success": True, "data": {"user": _user_payload(user)}}


@router.get("/google/start")
async def google_start(request: Request):
    if not google_configured:
        raise _auth_error(503, "Google sign-in is not configured yet", "GOOGLE_UNAVAILABLE")
    enforce_rate_limit(request, "google-start", limit=10, window_seconds=900)
    return await oauth.google.authorize_redirect(request, settings.google_callback_url)


@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    if not google_configured:
        raise _auth_error(503, "Google sign-in is not configured yet", "GOOGLE_UNAVAILABLE")
    try:
        token = await oauth.google.authorize_access_token(request)
        claims = token.get("userinfo") or await oauth.google.userinfo(token=token)
    except Exception:
        raise _auth_error(401, "Google sign-in could not be verified", "GOOGLE_AUTH_FAILED") from None
    email = str(claims.get("email", "")).lower()
    google_sub = str(claims.get("sub", ""))
    if not email or not google_sub:
        raise _auth_error(401, "Google did not provide an email address", "GOOGLE_EMAIL_MISSING")
    if claims.get("email_verified") is not True:
        raise _auth_error(401, "Verify your email address with Google before signing in", "GOOGLE_EMAIL_UNVERIFIED")
    user = db.scalar(select(User).where(User.google_sub == google_sub))
    if not user:
        user = db.scalar(select(User).where(User.email == email))
        if user:
            if user.role == "ADMIN":
                raise _auth_error(403, "Admin accounts cannot sign in with Google.", "ADMIN_GOOGLE_BLOCKED")
            user.google_sub = google_sub
            user.email_verified = True
            user.picture_url = str(claims.get("picture", "") or user.picture_url or "")[:500] or user.picture_url
            user.full_name = user.full_name or str(claims.get("name", ""))[:120] or None
        else:
            user = User(
                email=email,
                full_name=str(claims.get("name", ""))[:120] or None,
                google_sub=google_sub,
                picture_url=str(claims.get("picture", "") or "")[:500] or None,
                email_verified=True,
                role="USER",
                signup_method="google",
            )
            db.add(user)
            db.flush()
    if user.role == "ADMIN":
        raise _auth_error(403, "Admin accounts cannot sign in with Google.", "ADMIN_GOOGLE_BLOCKED")
    if not user.is_active:
        raise _auth_error(403, "This account is unavailable", "ACCOUNT_DISABLED")
    response = RedirectResponse(url=settings.frontend_url.rstrip("/") + "/", status_code=303)
    _mark_login(user, request, "google")
    _create_session(db, user, request, response)
    db.commit()
    return response
