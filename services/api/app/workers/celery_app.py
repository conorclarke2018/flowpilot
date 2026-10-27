from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "flowpilot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

if settings.environment == "test":
    celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)
