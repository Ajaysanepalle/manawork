# Local Setup

## Frontend only

Install Node.js 22 or newer, then run `npm install` and `npm run dev` from the repository root. Vite prints the local URL (normally `http://localhost:5173`). Frontend development works without Docker; jobs are visibly marked as preview data when the API cannot be reached.

## Full local stack

Start Docker Desktop in Linux-container mode. ManaWorks uses the host PostgreSQL service and its dedicated `manaworks` database. Set the URL in the current PowerShell session (do not save it in Git):

```powershell
$env:DATABASE_URL = 'postgresql+psycopg://postgres:<your-password>@host.docker.internal:5432/manaworks'
docker compose up --build
```

Frontend: `http://localhost:3000`. FastAPI: `http://localhost:8000`; OpenAPI docs: `http://localhost:8000/docs`. The API container runs Alembic before Uvicorn. Redis is provided by Compose on port 6379. Docker Desktop maps `host.docker.internal` to the Windows host where PostgreSQL listens. The verified host is PostgreSQL 18.3; the isolated database has migrations through `0002_auth` applied and is intentionally empty until approved job data is supplied.

The auth migration adds `users`, `auth_sessions`, and `auth_tokens`. SMTP is captured locally by Mailpit at `http://localhost:8025`; no email leaves the machine. Qdrant runs locally at `http://localhost:6333` and its data persists in a dedicated Compose volume. Google OAuth and phone verification respond as unavailable until Google client credentials and Twilio Verify credentials are configured. Semantic search additionally requires Ollama with the configured embedding model pulled and jobs indexed.

The current local connection uses the PostgreSQL administrator credentials supplied for setup. Do not reuse that account for production; create a dedicated least-privilege application role before any shared or deployed environment.

To enable Google locally, create a Google OAuth Web client and set `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and `GOOGLE_CALLBACK_URL=http://localhost:8000/api/v1/auth/google/callback` in the launching environment. Register that exact callback with Google. To enable phone OTP, set `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, and `TWILIO_VERIFY_SERVICE_SID`; values belong in a local untracked `.env` or secret manager, never in source control or chat. For production, also provide the frontend URL, exact production API callback, allowed frontend origin, verified SMTP sender, separate JWT/session secrets, and isolated Qdrant URL/API key. UAT and production Compose require their own independent database, Redis, and Qdrant endpoints.

Ollama is optional: `docker compose --profile ai up --build`. Pulling a model is intentionally a separate, bandwidth- and disk-intensive choice; semantic search returns an unavailable response until the embedding model is installed. The platform uses Qdrant for vectors; the host PostgreSQL installation does not need pgvector.

## Backend tests

Create and activate a virtual environment, install `backend/requirements.txt`, set `PYTHONPATH=backend`, and run `pytest backend/tests`. A local PostgreSQL instance is needed for migrations and readiness; the health endpoint test itself does not require PostgreSQL.

## Troubleshooting

- If `docker compose` cannot connect to the engine, start Docker Desktop and confirm Linux containers are enabled.
- If ports conflict, override `FRONTEND_PORT`, `API_PORT`, or `REDIS_PORT` in `.env`.
- If the database schema changes, create and review an Alembic migration before applying it; do not change a deployed schema manually.
- Never use local volumes or secrets for UAT or production.