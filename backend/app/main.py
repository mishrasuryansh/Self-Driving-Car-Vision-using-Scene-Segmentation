"""FastAPI Backend Application Main Entrypoint (T091, T095).

Initializes the FastAPI application instance, binds settings, configures CORS (T095) and custom security middlewares (T091),
registers global exception handlers (T094), manages database & cache connection lifecycles, and exposes API routes.
"""

from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.router import api_router
from app.config import settings
from app.db.mongodb import mongodb_manager
from app.db.redis import redis_manager
from app.exceptions import (
    APIException,
    api_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.middleware import (
    ProcessTimeMiddleware,
    RateLimiterMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)

# Configure structured Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager handling startup and shutdown events for databases & caches."""
    logger.info("Executing application startup sequence...")
    await mongodb_manager.connect()
    await redis_manager.connect()
    yield
    logger.info("Executing application shutdown sequence...")
    await redis_manager.close()
    await mongodb_manager.close()


# Single application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Register Global Exception Handlers (T094)
app.add_exception_handler(APIException, api_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Configure CORS Security Policy (T095)
origins = settings.ALLOWED_ORIGINS or ["http://localhost:5173", "http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Configure Custom HTTP Middlewares (T091)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware, default_limit=100, auth_limit=10)
app.add_middleware(ProcessTimeMiddleware)
app.add_middleware(RequestIDMiddleware)

# Include API V1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    f"{settings.API_V1_STR}/health",
    tags=["Health"],
    summary="System Health Check Endpoint",
    response_model=dict,
)
def get_health_v1() -> dict:
    """Return system health status and application version conforming to Section 8.3 contract."""
    return {"status": "ok", "version": settings.VERSION}


@app.get(
    "/health",
    tags=["Health"],
    summary="Root Health Check Alias",
    include_in_schema=False,
)
def get_health_root() -> dict:
    """Root health alias returning status and version."""
    return {"status": "ok", "version": settings.VERSION}


__all__ = ["app"]
