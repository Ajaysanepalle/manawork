# ManaWorks

A Telugu-first career platform foundation for students, freshers, and early-career professionals in India.

## What works now

- Responsive public career homepage with job keyword, location, work-mode, and salary sorting controls.
- Public job detail pages and sign-in gates for save/apply actions.
- Clearly labeled preview listings while the API is unavailable.
- FastAPI `/api/v1/health`, `/api/v1/ready`, and published-job search endpoints.
- Email/password accounts with email verification, password recovery, Argon2 hashes, HttpOnly access/refresh cookies, CSRF validation, Redis rate limits, session rotation, and logout revocation.
- Google OIDC and Twilio Verify adapters gated on provider credentials.
- Qdrant vector-store adapter, local Qdrant service, Ollama embedding adapter, and optional semantic jobs endpoint.
- PostgreSQL SQLAlchemy model and initial Alembic migration for jobs.
- Separate local, UAT, and production Compose configurations; UAT/production require separate database, Redis, and Qdrant services.
- Redis/Celery worker shell and configurable Ollama settings.

This is still a foundation, not the complete product in the master brief. Admin RBAC/workflows, phone OTP until Twilio is configured, Google until OAuth credentials are configured, resume processing, embedding/indexing jobs, AI career workflows, notifications, and real job seeding/providers remain incomplete. Semantic search requires an available Ollama embedding model and published jobs indexed in Qdrant.

## Run the frontend

Requirements: Node.js 22+ and npm.

```powershell
npm install
npm run dev
```

Open `http://localhost:5173`. Without a running API, the interface shows six labeled preview roles and supports local filtering. The frontend production build is `npm run build`.

## Run with Docker

Requirements: Docker Desktop running in Linux-container mode.

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://postgres:<your-password>@host.docker.internal:5432/manaworks'
docker compose up --build
```

Open the frontend at `http://localhost:3000`; API docs are at `http://localhost:8000/docs`. Verification emails are captured at the local-only [Mailpit inbox](http://localhost:8025). Qdrant is available at `http://localhost:6333/dashboard`. Local Compose connects to the host PostgreSQL database through `host.docker.internal`; it does not start a second PostgreSQL server. Set `DATABASE_URL` in the shell before starting Compose, using the dedicated `manaworks` database. Do not commit credentials. Ollama is opt-in so core services do not require large model downloads:

```powershell
docker compose --profile ai up --build
```

The host PostgreSQL instance lacks pgvector, but ManaWorks vector retrieval uses Qdrant instead. The isolated `manaworks` database is migrated and currently contains no job listings. Local setup currently uses the PostgreSQL administrator account; create a restricted application role before any shared or deployed use. Google and phone OTP return unavailable until their credentials are configured.

For local Google OAuth, set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in the shell running Compose and register callback `http://localhost:8000/api/v1/auth/google/callback` in Google Cloud. Phone OTP requires Twilio Verify values. Store all secrets in an untracked local environment file or a secret manager, never in source control or chat.

## Backend without Docker

Requirements: Python 3.11+ and PostgreSQL. From the repository root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
$env:DATABASE_URL = 'postgresql+psycopg://postgres:<your-password>@localhost:5432/manaworks'
$env:PYTHONPATH = 'backend'
alembic -c backend\alembic.ini upgrade head
uvicorn app.main:app --app-dir backend --reload
```

Set database and Redis URLs via environment variables. `/api/v1/health` does not depend on PostgreSQL; `/api/v1/ready` checks database connectivity. API docs are available at `/docs`. The current database is dedicated but does not have pgvector installed; install the PostgreSQL 18-compatible pgvector extension before implementing embeddings/vector search.

## Checks

```powershell
npm run lint
npm run build
python -m pip install -r backend\requirements.txt
$env:PYTHONPATH = 'backend'
pytest backend\tests
```

See [local setup](docs/local-setup.md), [architecture](docs/architecture.md), [UAT](docs/uat.md), [production](docs/production.md), [backup and restore](docs/backup-restore.md), and [security](docs/security.md).
