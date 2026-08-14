"""HTTP Request Middleware Definitions (T091).

Provides request ID tracing (X-Request-ID), process time headers (X-Process-Time),
security HTTP response headers (T091), and IP rate-limiting middleware (T091).
"""

from collections import defaultdict
import logging
import time
import uuid
from fastapi import status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.middleware")

# In-memory Rate Limit Store: ip -> list of timestamps
_rate_limit_store = defaultdict(list)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting and propagating a unique X-Request-ID header."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """Middleware for tracking request processing execution time (X-Process-Time)."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        response.headers["X-Process-Time"] = f"{process_time:.6f}"

        # Structured request lifecycle logging
        req_id = getattr(request.state, "request_id", "N/A")
        logger.info(
            "[%s] %s %s -> HTTP %d (%.4fs)",
            req_id,
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for injecting security response headers (T091)."""

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """IP-based sliding window rate-limiting middleware (T091)."""

    def __init__(
        self,
        app,
        default_limit: int = 100,
        auth_limit: int = 10,
        window_seconds: int = 60,
    ):
        super().__init__(app)
        self.default_limit = default_limit
        self.auth_limit = auth_limit
        self.window_seconds = window_seconds

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        client_ip = request.client.host if request.client else "127.0.0.1"
        path = request.url.path
        now = time.time()

        # Determine rate limit quota for path
        is_auth_route = "/auth/login" in path or "/auth/register" in path
        limit = self.auth_limit if is_auth_route else self.default_limit

        # Clean old timestamps outside the sliding window
        window_start = now - self.window_seconds
        timestamps = [t for t in _rate_limit_store[client_ip] if t > window_start]
        _rate_limit_store[client_ip] = timestamps

        remaining = max(0, limit - len(timestamps))
        reset_time = int(self.window_seconds)

        if len(timestamps) >= limit:
            logger.warning("Rate limit exceeded for IP %s on path %s", client_ip, path)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": {
                        "code": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "details": {"limit": limit, "windowSeconds": self.window_seconds},
                    }
                },
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                    "Retry-After": str(reset_time),
                },
            )

        # Record current request timestamp
        _rate_limit_store[client_ip].append(now)

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining - 1 if remaining > 0 else 0)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        return response


__all__ = [
    "RequestIDMiddleware",
    "ProcessTimeMiddleware",
    "SecurityHeadersMiddleware",
    "RateLimiterMiddleware",
]
