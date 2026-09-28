# Security Notes

## Implemented

- Argon2 password hashing; email verification and password-reset tokens are single-use, expire, and are stored hashed.
- Access and rotating refresh cookies are HttpOnly; refresh-session hashes are persisted for revocation and logout invalidates the session.
- Origin-checked double-submit CSRF tokens protect state-changing auth endpoints.
- Redis-backed limits protect login, signup, verification, recovery, and OTP endpoints; auth mutations fail closed if Redis is unavailable.
- Google OIDC validates the provider token/userinfo server-side and requires a verified email; Twilio Verify owns phone codes and verification.
- Public API search restricts results to published jobs and validates filter lengths, sort values, mode values, page ranges, and page size.
- Database access uses SQLAlchemy parameterized expressions.
- Readiness reports database failure without making general liveness depend on PostgreSQL.
- CORS origins are configuration-driven.
- UAT and production Compose require separate database, Redis, and origin settings.
- Example configuration contains no working production credentials.
- UAT/production startup rejects the known local signing-secret defaults.

## Required before accepting users or deploying publicly

- Configure Google OAuth and Twilio Verify credentials and production callback/domain values in a secret manager; verify real provider callbacks in UAT.
- Configure production SMTP delivery, domain authentication, bounce handling, and recovery-link origin.
- Implement server-side RBAC dependencies on every admin endpoint; audit privileged actions.
- Add server-side RBAC dependencies to every admin endpoint; audit privileged actions.
- Add login, OTP, and reset rate limits; hashed single-use expiring OTP/reset values; SMS/email provider adapters; do not log codes or secrets.
- Validate Google OAuth tokens on the server. Do not treat a frontend profile payload as identity proof.
- Add secure headers, production HTTPS termination, restrictive CORS, request-size limits, upload MIME/content inspection, malware scanning, and private object storage before accepting resumes.
- Add secret management, database TLS, least-privilege roles, dependency scanning, monitoring, backups, and tested incident/restore procedures.
- Treat resumes, job descriptions, and retrieved text as untrusted prompt-injection content. AI must not make authorization decisions or execute generated SQL.

Do not expose this foundation as a functioning account or job application service until these controls and the relevant flows are implemented and tested.