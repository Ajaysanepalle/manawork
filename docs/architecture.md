# Architecture

## Current foundation

The browser app is React 19, TypeScript, and Vite. React Router owns public routes; TanStack Query caches API requests. Public job search calls `/api/v1/jobs`; if the API is unreachable, the browser uses clearly labeled, non-production sample listings. The Vite development server proxies `/api` to FastAPI.

The API is FastAPI with Pydantic v2 settings and SQLAlchemy 2. Public search only returns `PUBLISHED` records, applies filters in SQL, and paginates. PostgreSQL owns relational and private account/session data. Alembic migrations create the jobs, users, auth sessions, and one-time auth-token tables. Qdrant owns vector collections for jobs, resumes, and career content; the adapter supports typed upsert/search/delete, and the semantic search endpoint embeds a query with a configured local Ollama model. Job publish/indexing and resume indexing workflows are not wired yet. Redis backs rate limits and Celery is included for future background tasks.

## Boundaries

```text
Browser -> React auth/job services -> FastAPI -> SQLAlchemy -> PostgreSQL
                                               -> Redis rate limits -> Celery worker
                                               -> Ollama embeddings -> Qdrant semantic retrieval
                                               -> SMTP / Mailpit, Twilio Verify, Google OIDC
```

Public and authenticated data must remain separate. Published listings are public; profile, application, resume, and conversation APIs must require server-side authorization when introduced. Never trust UI role checks.

## Planned modules

Add authentication, profiles, companies, saved jobs, applications, and RBAC in discrete API modules. Add an AI provider interface before implementing Ollama inference; keep deterministic scores and matching in application code, and keep model output advisory. Add pgvector through Alembic only when an embedding workflow is ready. Background delivery and resume processing belong in Celery tasks, not request handlers.

## Current limitations

Phone OTP and Google OAuth are credential-gated; no Google or Twilio credentials are configured. There is no admin write API/RBAC, sample-job database seed, company relation, audit log, notifications, upload storage, job embedding/indexing task, resume AI workflow, or telemetry. Semantic search is unavailable until Ollama has the configured embedding model and jobs are indexed. Per-job SEO/schema.org output is not available because this is a client-rendered first slice.