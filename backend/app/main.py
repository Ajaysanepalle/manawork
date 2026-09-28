import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.router import api_router
from app.api.v1.endpoints.health import router as health_router
from app.core.config import get_settings
from app.services.bootstrap import seed_admin

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if not os.environ.get("PYTEST_CURRENT_TEST"):
        try:
            seed_admin()
        except Exception:
            pass
    yield


app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug, lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    session_cookie="mw_oauth_state",
    max_age=600,
    same_site="lax",
    https_only=settings.secure_cookies,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-CSRF-Token"],
)
app.include_router(api_router)
app.include_router(health_router)
