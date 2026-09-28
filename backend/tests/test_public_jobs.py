from collections.abc import Generator
from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.api.v1.endpoints import jobs as jobs_endpoint
from app.core.security import create_access_token, hash_password, hash_secret, new_secret
from app.models.job import Job, JobStatus
from app.models.user import AuthSession, User
from time import time


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
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
    with test_session() as session:
        session.add_all(
            [
                Job(
                    title="Backend Engineer",
                    company="Example Labs",
                    location="Hyderabad",
                    experience="Fresher",
                    description="Build APIs",
                    tags=["FastAPI", "Python"],
                    responsibilities=[],
                    requirements=[],
                    status=JobStatus.PUBLISHED,
                ),
                Job(
                    title="Private draft",
                    company="Example Labs",
                    location="Hyderabad",
                    experience="Fresher",
                    description="Draft listing",
                    tags=["Python"],
                    responsibilities=[],
                    requirements=[],
                    status=JobStatus.DRAFT,
                ),
            ]
        )
        session.commit()

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()


def test_public_search_matches_skills_and_excludes_drafts(client: TestClient) -> None:
    response = client.get("/api/v1/jobs", params={"q": "FastAPI", "location": "Hyderabad"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["total"] == 1
    assert payload["data"]["items"][0]["title"] == "Backend Engineer"


def test_semantic_search_filters_unpublished_qdrant_points(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    published_id = str(uuid4())

    class FakeVectorStore:
        def search_jobs(self, vector: list[float], limit: int) -> list[SimpleNamespace]:
            return [
                SimpleNamespace(id=published_id, score=0.94, payload={"status": "PUBLISHED", "title": "Backend Engineer"}),
                SimpleNamespace(id=str(uuid4()), score=0.91, payload={"status": "DRAFT", "title": "Private draft"}),
            ]

    monkeypatch.setattr(jobs_endpoint, "embed_text", lambda query: [1.0, 0.0, 0.0])
    monkeypatch.setattr(jobs_endpoint, "QdrantVectorStore", FakeVectorStore)

    response = client.get("/api/v1/jobs/semantic-search", params={"q": "Python backend fresher"})

    assert response.status_code == 200
    assert response.json()["data"]["total"] == 1
    assert response.json()["data"]["items"][0]["id"] == published_id


def test_admin_can_publish_job_visible_to_users(client: TestClient) -> None:
    from app.db.session import get_db

    db_gen = app.dependency_overrides[get_db]()
    session = next(db_gen)
    admin = User(username="ajay", email="ajay@manaworks.local", password_hash=hash_password("ajay123"), role="ADMIN", signup_method="admin_seed")
    session.add(admin)
    session.flush()
    refresh_token = new_secret()
    auth_session = AuthSession(user_id=admin.id, refresh_token_hash=hash_secret(refresh_token), expires_at=int(time()) + 3600)
    session.add(auth_session)
    session.commit()
    client.cookies.set("mw_access", create_access_token(admin.id, auth_session.id))
    client.cookies.set("mw_refresh", refresh_token)
    db_gen.close()

    created = client.post(
        "/api/v1/admin/jobs",
        json={
            "title": "Campus Recruiter",
            "company": "ManaWorks",
            "location": "Hyderabad",
            "mode": "hybrid",
            "employment_type": "Full-time",
            "experience": "0-2 years",
            "salary": "₹8-12 LPA",
            "apply_url": "https://careers.example.com/jobs/campus-recruiter",
            "tags": ["Hiring", "People"],
            "description": "Help students find work that moves them forward with care.",
            "responsibilities": ["Post roles", "Talk to candidates"],
            "requirements": ["Clear writing", "Empathy"],
        },
    )
    assert created.status_code == 200
    job_id = created.json()["data"]["job"]["id"]
    listed = client.get("/api/v1/jobs", params={"q": "Campus Recruiter"})
    assert listed.status_code == 200
    assert listed.json()["data"]["total"] >= 1
    detail = client.get(f"/api/v1/jobs/{job_id}")
    assert detail.status_code == 200
    assert detail.json()["data"]["job"]["title"] == "Campus Recruiter"
    assert detail.json()["data"]["job"]["applyUrl"] == "https://careers.example.com/jobs/campus-recruiter"

    updated = client.put(
        f"/api/v1/admin/jobs/{job_id}",
        json={
            "title": "Senior Campus Recruiter",
            "company": "ManaWorks",
            "location": "Hyderabad",
            "mode": "hybrid",
            "employment_type": "Full-time",
            "experience": "2-4 years",
            "salary": "₹10-14 LPA",
            "apply_url": "https://careers.example.com/jobs/senior-campus-recruiter",
            "tags": ["Hiring", "People"],
            "description": "Help students find work that moves them forward with care.",
            "responsibilities": ["Post roles", "Talk to candidates"],
            "requirements": ["Clear writing", "Empathy"],
        },
    )
    assert updated.status_code == 200
    assert updated.json()["data"]["job"]["title"] == "Senior Campus Recruiter"
    assert client.get(f"/api/v1/jobs/{job_id}").json()["data"]["job"]["applyUrl"] == "https://careers.example.com/jobs/senior-campus-recruiter"

    deleted = client.delete(f"/api/v1/admin/jobs/{job_id}")
    assert deleted.status_code == 200
    assert client.get(f"/api/v1/jobs/{job_id}").status_code == 404

    users = client.get("/api/v1/admin/users")
    assert users.status_code == 200