"""HTTP Request Middleware Definitions.

Provides request ID tracing (X-Request-ID), request processing latency headers (X-Process-Time),
and structured request lifecycle logging for the FastAPI backend service.
"""

import logging
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("app.middleware")


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


__all__ = ["RequestIDMiddleware", "ProcessTimeMiddleware"]
