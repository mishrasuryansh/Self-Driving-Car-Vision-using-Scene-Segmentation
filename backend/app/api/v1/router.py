"""API V1 Router Aggregator.

Aggregates all version 1 endpoint routers (Auth, Analytics, Health, Media, Inference, Jobs) under a unified router.
"""

from fastapi import APIRouter
from app.api.v1.endpoints import analytics, auth, health, inference, jobs, media

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(media.router, prefix="/media", tags=["Media Management"])
api_router.include_router(inference.router, prefix="/inference", tags=["Scene Segmentation Inference"])
api_router.include_router(jobs.router, prefix="/jobs", tags=["Job Management"])

__all__ = ["api_router"]
