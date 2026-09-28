from celery import Celery

from app.core.config import get_settings

settings = get_settings()
celery_app = Celery("manaworks", broker=settings.redis_url, backend=settings.redis_url)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(name="manaworks.health_check")
def health_check() -> str:
    return "ok"