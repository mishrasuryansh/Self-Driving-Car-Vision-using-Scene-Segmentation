"""Celery Asynchronous Task Application Configuration.

Configures Celery distributed worker application, message broker bindings, result backend,
and task serialization settings conforming to Section 8.2 & EP5 specs.
"""

import logging
from celery import Celery
from app.config import settings

logger = logging.getLogger("app.core.celery_app")

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.inference_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    result_expires=3600,  # Expire task results after 1 hour
    broker_connection_retry_on_startup=False,
    broker_transport_options={"max_retries": 1, "interval_start": 0.1},
    result_backend_transport_options={"max_retries": 1, "interval_start": 0.1},
    task_always_eager=True,  # Local execution eager fallback
)

__all__ = ["celery_app"]
