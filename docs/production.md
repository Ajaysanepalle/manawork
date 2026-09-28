# Production Preparation

The production Compose file is a deployment starting point, not a production certification. It requires separate database, Redis, Qdrant URL/API key, frontend URL, allowed origin, Ollama endpoint, and unique JWT/session signing secrets. It does not create local database or Redis volumes. Use managed, isolated, TLS-enabled services and a secret manager. Set an explicit production frontend domain and enforce HTTPS at the ingress/load balancer. Google OAuth, Twilio Verify, and SMTP credentials are optional at startup but required before enabling those methods; register the exact production Google callback URL.

Before release:

1. Complete authentication, server-side authorization, audit logging, input and upload security, rate limiting, and privacy/data-retention behavior.
2. Configure secrets, strict CORS, TLS, database/Redis network access, monitoring, alerting, and encrypted backups.
3. Run unit, integration, security, and browser journey tests against a production-like UAT deployment with synthetic data.
4. Review the Alembic migration and take/verify a restorable backup before applying schema changes.
5. Deploy an immutable image digest to UAT, validate health and critical journeys, then require explicit approval for production.
6. Keep the prior application image available for rollback. Database downgrade is not automatically safe; use a forward fix or restore plan agreed for each migration.

Production currently has no HTTPS ingress, provider credentials, migration approval gate, data backup integration, metrics, error tracking, or tested rollback. Qdrant semantic search requires an indexed published-job pipeline and the configured Ollama embedding model. Do not deploy this foundation to serve real candidate data.