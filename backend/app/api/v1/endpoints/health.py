"""System Health & Worker Readiness Endpoints.

Provides detailed system health checks (`GET /api/v1/health`),
and Celery worker readiness checks (`GET /api/v1/health/worker`) conforming to Section 8.3 & T050 contract.
"""

import logging
from typing import Dict
from fastapi import APIRouter, Depends, status
from app.config import settings
from app.core.celery_app import celery_app
from app.db.redis import get_redis, redis_manager

logger = logging.getLogger("app.api.v1.endpoints.health")
router = APIRouter()


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    summary="System Health Check",
)
def get_system_health() -> dict:
    """Return application health status and version."""
    return {"status": "ok", "version": settings.VERSION}


@router.get(
    "/worker",
    status_code=status.HTTP_200_OK,
    response_model=dict,
    summary="Worker Readiness & Celery Ping Check (T050)",
)
async def get_worker_health(
    redis=Depends(get_redis),
) -> dict:
    """Check Redis connectivity and Celery background worker ping status."""
    redis_status = "disconnected"
    if redis is not None:
        try:
            await redis.ping()
            redis_status = "connected"
        except Exception as exc:
            logger.warning("Redis ping error in worker health check: %s", exc)

    worker_active = False
    celery_responses = []
    try:
        # Ping active Celery workers with 1s timeout
        ping_res = celery_app.control.ping(timeout=1.0)
        if ping_res:
            worker_active = True
            celery_responses = ping_res
    except Exception as exc:
        logger.warning("Celery ping error in worker health check: %s", exc)

    return {
        "status": "ok" if redis_status == "connected" or worker_active else "degraded",
        "redis_status": redis_status,
        "worker_active": worker_active,
        "celery_responses": celery_responses,
        "version": settings.VERSION,
    }


__all__ = ["router"]
