# UAT

UAT uses `docker-compose.uat.yml` and requires `UAT_DATABASE_URL`, `UAT_REDIS_URL`, and `UAT_CORS_ORIGINS` for dedicated non-production services. Do not point these at production. The configuration fails fast when those values are absent. Only synthetic data belongs in UAT; no seed command is provided yet.

Run after Docker is available and UAT services have been provisioned:

```powershell
docker compose -f docker-compose.uat.yml up --build -d
```

| Area | Check | Status |
|---|---|---|
| Public site | Homepage loads at mobile and desktop sizes | BLOCKED: Docker engine unavailable |
| Jobs | Published jobs are returned and drafts are hidden | BLOCKED: no UAT DB or seed |
| Search | Keyword, skills, location, mode, sorting, pagination | BLOCKED: no UAT DB or seed |
| Details | Listing detail renders and missing listing has an empty state | BLOCKED: browser run pending |
| Account | Signup, login, Google, OTP, logout, password reset | BLOCKED: not implemented |
| Candidate | Profile, resume, saved jobs, applications, account deletion | BLOCKED: not implemented |
| AI | ATS, matching, skill gap, Telugu assistant, AI failure mode | BLOCKED: not implemented |
| Admin | RBAC, job create/edit/publish/archive, analytics, audit log | BLOCKED: not implemented |
| Notifications | Email, job alerts, notification center | BLOCKED: not implemented |
| Operations | Migrations, readiness, logs, backup and restore drill | BLOCKED: UAT services unavailable |

UAT cannot be considered passed until each blocked critical workflow is implemented, exercised with synthetic data, and recorded by an operator.