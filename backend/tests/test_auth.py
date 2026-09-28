from collections.abc import Generator
from http.cookies import SimpleCookie
from time import time
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.endpoints import auth as auth_endpoints
from app.core.security import create_access_token, hash_password, hash_secret, new_secret
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.user import AuthSession, User


@pytest.fixture
def auth_client(monkeypatch: pytest.MonkeyPatch) -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    test_session = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def override_get_db() -> Generator[Session, None, None]:
        with test_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    monkeypatch.setattr(auth_endpoints, "enforce_rate_limit", lambda *args, **kwargs: None)
    with TestClient(app) as client:
        yield client, test_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


def _csrf(client: TestClient) -> dict[str, str]:
    response = client.get("/api/v1/auth/csrf")
    assert response.status_code == 200
    return {"Origin": "http://localhost:5173", "X-CSRF-Token": response.json()["data"]["csrf_token"]}


def test_google_user_session_refresh_rotation_and_logout(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, test_session = auth_client
    with test_session() as session_db:
        user = User(email="google-user@example.com", full_name="Google User", google_sub="google-sub-123", email_verified=True, signup_method="google")
        session_db.add(user)
        session_db.flush()
        refresh_token = new_secret()
        auth_session = AuthSession(user_id=user.id, refresh_token_hash=hash_secret(refresh_token), expires_at=int(time()) + 3600)
        session_db.add(auth_session)
        session_db.flush()
        client.cookies.set("mw_access", create_access_token(user.id, auth_session.id))
        client.cookies.set("mw_refresh", refresh_token)
        session_db.commit()

    assert client.get("/api/v1/auth/me").status_code == 200
    headers = _csrf(client)
    refreshed = client.post("/api/v1/auth/refresh", headers=headers)
    assert refreshed.status_code == 200
    refreshed_cookies = SimpleCookie()
    for header in refreshed.headers.get_list("set-cookie"):
        refreshed_cookies.load(header)
    assert refreshed_cookies["mw_refresh"].value != refresh_token

    logout = client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert client.get("/api/v1/auth/me").status_code == 401


def test_password_signup_login_and_admin_are_stored(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, test_session = auth_client
    headers = _csrf(client)
    signup = client.post(
        "/api/v1/auth/signup",
        headers=headers,
        json={"full_name": "Ravi Kumar", "email": "ravi@example.com", "password": "secret12"},
    )
    assert signup.status_code == 200
    assert signup.json()["data"]["user"]["email"] == "ravi@example.com"
    assert signup.json()["data"]["user"]["role"] == "USER"

    with test_session() as session_db:
        stored = session_db.scalar(select(User).where(User.email == "ravi@example.com"))
        assert stored is not None
        assert stored.signup_method == "password"
        assert stored.last_login_method == "password"
        session_db.add(User(username="ajay", email="ajay@manaworks.local", full_name="Ajay", password_hash=hash_password("ajay123"), role="ADMIN", signup_method="admin_seed"))
        session_db.commit()

    client.post("/api/v1/auth/logout", headers=_csrf(client))
    login = client.post("/api/v1/auth/login", headers=_csrf(client), json={"identifier": "ravi@example.com", "password": "secret12"})
    assert login.status_code == 200

    admin_on_user_page = client.post("/api/v1/auth/login", headers=_csrf(client), json={"identifier": "ajay", "password": "ajay123"})
    assert admin_on_user_page.status_code == 403

    admin = client.post("/api/v1/auth/admin/login", headers=_csrf(client), json={"username": "ajay", "password": "ajay123"})
    assert admin.status_code == 200
    assert admin.json()["data"]["user"]["role"] == "ADMIN"


def test_google_status_and_removed_verification_routes(auth_client: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, _ = auth_client
    status = client.get("/api/v1/auth/google/status")
    assert status.status_code == 200
    assert "configured" in status.json()["data"]
    assert client.post("/api/v1/auth/verify-email").status_code == 404
    assert client.post("/api/v1/auth/phone/send-otp").status_code == 404
    assert client.post("/api/v1/auth/password/forgot").status_code == 404


def test_google_callback_requires_verified_email_and_creates_user(
    auth_client: tuple[TestClient, sessionmaker[Session]], monkeypatch: pytest.MonkeyPatch
) -> None:
    client, test_session = auth_client
    claims = {
        "email": "google-user@example.com",
        "sub": "google-sub-123",
        "name": "Google User",
        "email_verified": False,
    }

    class GoogleClient:
        async def authorize_access_token(self, request):
            return {"userinfo": claims}

    monkeypatch.setattr(auth_endpoints, "google_configured", True)
    monkeypatch.setattr(auth_endpoints, "oauth", SimpleNamespace(google=GoogleClient()))

    unverified = client.get("/api/v1/auth/google/callback?code=unverified", follow_redirects=False)
    assert unverified.status_code == 401
    assert unverified.json()["detail"]["error_code"] == "GOOGLE_EMAIL_UNVERIFIED"

    with test_session() as session_db:
        assert session_db.scalar(select(User).where(User.email == "google-user@example.com")) is None

    claims["email_verified"] = True
    verified = client.get("/api/v1/auth/google/callback?code=verified", follow_redirects=False)
    assert verified.status_code == 303

    with test_session() as session_db:
        user = session_db.scalar(select(User).where(User.email == "google-user@example.com"))
        assert user is not None
        assert user.google_sub == "google-sub-123"
        assert user.email_verified is True
        assert user.signup_method == "google"
