# Public Deployment: Netlify, Render, and Supabase

This guide deploys the Vite frontend to Netlify, the FastAPI API to Render, PostgreSQL to Supabase, and Redis-compatible rate limiting to Render Key Value. Supabase is used as the database only; do not put database credentials in the browser.

> This repository's production notes identify security, privacy, backup, monitoring, and rollback work that is not complete. Use this setup for a public demo with non-sensitive test data until those items have been reviewed. Do not use it for real candidate data yet.

## 1. Prepare the repository

1. Push the project to a private GitHub repository. Do not commit `.env`, database passwords, OAuth secrets, or generated signing secrets. The repository `.gitignore` excludes `.env` files; verify your repository's secret-scanning page after pushing.
2. Confirm the latest code is pushed, including the Alembic migrations. Render and Netlify both deploy from this Git repository.
3. Use one production frontend hostname. The examples below use `https://YOUR-SITE.netlify.app`; replace it with your actual Netlify domain everywhere. Do not include a trailing slash in environment-variable origins.

## 2. Create the Supabase database

1. Create a Supabase organization and project. Choose a region close to the Render region. Set and securely store a unique database password.
2. In the project dashboard, click **Connect**, choose **Session pooler**, and copy its connection string. The shared session pooler is reachable over IPv4 and supports the persistent backend and migrations used here. Do not use transaction pooler port `6543` for this SQLAlchemy service.
3. Convert the copied URI scheme from `postgresql://` to `postgresql+psycopg://`, keep the pooler-provided username/host/port/database, and add `?sslmode=require` (or `&sslmode=require` if the URI already has query parameters). It should look like:

   ```text
   postgresql+psycopg://postgres.PROJECT_REF:URL_ENCODED_PASSWORD@POOLER_HOST:5432/postgres?sslmode=require
   ```

4. URL-encode reserved characters in the database password. Copy the host and username from Supabase; do not construct the pooler hostname yourself. Store the completed URI for the Render `DATABASE_URL` setting only.
5. The app creates its tables using Alembic at backend startup. No Supabase Auth setup, Supabase anon key, or service-role key is needed for this app's current backend.

Supabase connection instructions: https://supabase.com/docs/guides/database/connecting-to-postgres

## 3. Create Redis on Render

Login, signup, and Google sign-in rate limiting require Redis. Without it, auth requests fail closed with HTTP 503.

1. In Render, create **New + → Key Value**.
2. Choose the same region as the backend service. Wait for the instance to become available.
3. Open its **Connect** menu and copy the **internal URL**. It looks like `redis://red-...:6379`.
4. Set this value as the backend's `REDIS_URL`. Keep the Key Value instance and web service in the same Render workspace and region so the internal URL is reachable.

Render may label new Redis-compatible instances as Key Value/Valkey. Use the internal URL, not the external URL.

## 4. Deploy the FastAPI backend to Render

1. In Render, choose **New + → Web Service** and connect the Git repository.
2. Configure the service:
   - **Name:** for example `manaworks-api`
   - **Root Directory:** `backend`
   - **Runtime/Language:** Python 3
   - **Region:** the same region as Render Key Value, preferably near Supabase
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/api/v1/health`
3. Add these environment variables in the Render service's **Environment** page. Use the exact names and enter real values in the dashboard, never in Git:

   | Name | Value |
   | --- | --- |
   | `APP_ENV` | `prod` |
   | `DEBUG` | `false` |
   | `DATABASE_URL` | Supabase session-pooler URI from step 2 |
   | `REDIS_URL` | Render Key Value internal URL from step 3 |
   | `FRONTEND_URL` | `https://YOUR-SITE.netlify.app` |
   | `CORS_ORIGINS` | `https://YOUR-SITE.netlify.app` |
   | `JWT_SECRET` | A new random string, at least 32 characters |
   | `SESSION_SECRET` | A different new random string, at least 32 characters |
   | `ADMIN_USERNAME` | A private admin username, for example `siteadmin` |
   | `ADMIN_PASSWORD` | A unique, strong admin password |
   | `GOOGLE_CLIENT_ID` | Add after creating the Google OAuth client in step 7 |
   | `GOOGLE_CLIENT_SECRET` | Add after creating the Google OAuth client in step 7 |
   | `GOOGLE_CALLBACK_URL` | `https://YOUR-SITE.netlify.app/api/v1/auth/google/callback` |
   | `QDRANT_URL` | Optional; configure a hosted Qdrant endpoint only if using semantic search |
   | `QDRANT_API_KEY` | Optional; key for the hosted Qdrant endpoint |

   Generate two independent signing secrets locally, for example by running this command twice:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Do not use the defaults from local `.env`. Do not set `AUTH_COOKIE_DOMAIN` for the Netlify proxy setup; leaving it unset keeps cookies host-only and secure.
4. Create the service and wait for its first deploy. The start command applies all Alembic migrations before Uvicorn starts.
5. Test `https://YOUR-RENDER-SERVICE.onrender.com/api/v1/health` and `/api/v1/ready`. The first checks the API process; `/ready` also checks the database.
6. Copy the actual Render service hostname. You need it in the Netlify proxy rule in step 5.

The Celery worker is not required for the current login, job browsing, saved jobs, or admin job publishing flows. Qdrant/semantic search will remain unavailable unless you configure and populate a hosted Qdrant service; do not point production services at local `localhost` URLs.

## 5. Configure Netlify's API proxy and deploy the frontend

The frontend sends requests to relative `/api/v1/...` paths. Netlify must proxy those paths to Render. This keeps API requests and auth cookies on the Netlify site origin, including the Google OAuth callback.

1. Create `public/_redirects` in the repository with the following two lines. Replace the Render hostname with the actual service hostname from step 4:

   ```text
   /api/*  https://YOUR-RENDER-SERVICE.onrender.com/api/:splat  200
   /*      /index.html                                           200
   ```

   The API rule must be first; the SPA fallback must be last. Vite copies files from `public` into `dist`, which is Netlify's publish directory.
2. Commit and push `public/_redirects`.
3. In Netlify, choose **Add new project → Import an existing project**, connect the Git repository, and select the production branch.
4. Set the build configuration:
   - **Base directory:** leave blank (repository root)
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
5. Deploy. Netlify will assign a domain such as `https://YOUR-SITE.netlify.app`.
6. If the assigned hostname differs from the placeholder, update the Render `FRONTEND_URL`, `CORS_ORIGINS`, and `GOOGLE_CALLBACK_URL` values to use the exact Netlify hostname, then redeploy the backend. Update the Render hostname in `public/_redirects` if necessary, push the change, and let Netlify redeploy.
7. Open the Netlify site and test `/`, `/jobs`, `/admin`, and a direct refresh on `/jobs/<job-id>`. The final SPA rewrite is needed for direct route refreshes.

Netlify redirect reference: https://docs.netlify.com/routing/redirects/rewrites-proxies/

## 6. Configure the admin account

At backend startup, the app seeds or updates the admin account from `ADMIN_USERNAME` and `ADMIN_PASSWORD`.

1. Set both values in Render before testing admin access. Pick a username without an email address unless you specifically want the email-like username.
2. Open `https://YOUR-SITE.netlify.app/admin` and sign in with those values.
3. Change `ADMIN_PASSWORD` in Render and redeploy if it was temporary. Since startup re-seeds the configured password, keep the Render value in a password manager and do not change it only in the UI/database.

## 7. Configure Google sign-in

The OAuth callback is intentionally served through Netlify's `/api/*` proxy. This lets the backend set cookies for the same host used by the frontend.

1. In Google Cloud Console, create/select a project and configure the OAuth consent screen for **External** users. For a public launch, publish the consent screen; while it remains in Testing, only listed test users can sign in.
2. Create an OAuth client with application type **Web application**.
3. Add this exact **Authorized redirect URI**:

   ```text
   https://YOUR-SITE.netlify.app/api/v1/auth/google/callback
   ```

4. If the console asks for an authorized JavaScript origin, add:

   ```text
   https://YOUR-SITE.netlify.app
   ```

5. Copy the client ID and client secret into Render's `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` variables. Set `GOOGLE_CALLBACK_URL` to the exact redirect URI above.
6. Save, redeploy the Render service, then test Google sign-in from the Netlify site. If using a custom domain, update all three places: Render frontend/callback/CORS variables, the Netlify proxy target if its Render host changed, and Google's redirect URI/origin.

Never put `GOOGLE_CLIENT_SECRET`, `DATABASE_URL`, `JWT_SECRET`, `SESSION_SECRET`, or a Supabase service-role key in Netlify's frontend environment. Vite variables prefixed with `VITE_` are public in the generated JavaScript.

## 8. Public launch checks

1. Confirm `https://YOUR-SITE.netlify.app/api/v1/health` returns API JSON through the Netlify proxy.
2. Confirm `https://YOUR-SITE.netlify.app/api/v1/ready` reports the database ready.
3. Create a regular account, sign out/in, and confirm session refresh works.
4. Test Google OAuth with an allowed account and confirm it returns to the Netlify domain.
5. Sign in to `/admin`, create a job with an HTTPS application URL, edit it, delete it, and verify the public job listing updates.
6. Test direct refresh of `/jobs` and `/jobs/<id>`.
7. In Supabase, verify the `alembic_version`, `users`, `auth_sessions`, `auth_tokens`, and `jobs` tables exist. Never expose the database publicly with a frontend key; the app connects from the backend only.
8. Configure backups, retention, monitoring, error alerts, custom-domain HTTPS, and account recovery before storing real user data.

## Troubleshooting

- **Netlify shows a page but API calls fail:** check the first `/api/*` rule in `public/_redirects`, confirm the Render hostname, and redeploy Netlify.
- **API health works but `/ready` fails:** inspect `DATABASE_URL`; use the Supabase session-pooler host, username, port `5432`, encoded password, and `sslmode=require`.
- **Login/signup returns 503:** check `REDIS_URL` and ensure Render Key Value and the backend are in the same workspace and region.
- **Google `redirect_uri_mismatch`:** make the Google Authorized redirect URI byte-for-byte equal to `GOOGLE_CALLBACK_URL`, including HTTPS, hostname, path, and no trailing slash.
- **Google login returns to the wrong host or loses the session:** use the Netlify proxy callback URL, keep `FRONTEND_URL` on the same Netlify site, and leave `AUTH_COOKIE_DOMAIN` unset.
- **Admin login fails:** check the current `ADMIN_USERNAME`/`ADMIN_PASSWORD` in Render, redeploy after changing them, and confirm the backend can connect to Supabase during startup.
- **Service starts but first request is slow:** check the current Render plan's idle/sleep behavior. Database, Redis, and web service availability and billing depend on current provider plans.
