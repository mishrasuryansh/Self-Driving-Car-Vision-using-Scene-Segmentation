"""Custom Exceptions and Standardized Exception Handlers.

Defines API exception hierarchy, standardized JSON error response payloads,
and FastAPI error handler functions matching Section 8.3 schema.
"""

import logging
from typing import Any, Optional
from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger("app.exceptions")


class APIException(Exception):
    """Base API exception with HTTP status code, error code, message, and details."""

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        code: str = "INTERNAL_SERVER_ERROR",
        message: str = "An unexpected error occurred.",
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details


class NotFoundException(APIException):
    """HTTP 404 Not Found Exception."""

    def __init__(
        self,
        message: str = "Requested resource not found.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NOT_FOUND",
            message=message,
            details=details,
        )


class BadRequestException(APIException):
    """HTTP 400 Bad Request Exception."""

    def __init__(
        self,
        message: str = "Invalid request input.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="BAD_REQUEST",
            message=message,
            details=details,
        )


class UnauthorizedException(APIException):
    """HTTP 401 Unauthorized Exception."""

    def __init__(
        self,
        message: str = "Authentication credentials required.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            code="UNAUTHORIZED",
            message=message,
            details=details,
        )


class ForbiddenException(APIException):
    """HTTP 403 Forbidden Exception."""

    def __init__(
        self,
        message: str = "Operation forbidden.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            code="FORBIDDEN",
            message=message,
            details=details,
        )


class InternalServerErrorException(APIException):
    """HTTP 500 Internal Server Error Exception."""

    def __init__(
        self,
        message: str = "An internal server error occurred.",
        details: Optional[Any] = None,
    ):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="INTERNAL_SERVER_ERROR",
            message=message,
            details=details,
        )


def get_request_id(request: Request) -> str:
    """Extract request_id attached by RequestIDMiddleware."""
    return getattr(request.state, "request_id", "N/A")


def format_error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    request_id: str = "N/A",
) -> dict:
    """Format standardized JSON error payload matching Section 8.3 contract."""
    payload = {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id,
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def api_exception_handler(request: Request, exc: APIException) -> JSONResponse:
    """Handler for custom APIException instances."""
    req_id = get_request_id(request)
    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=exc.code,
            message=exc.message,
            details=exc.details,
            request_id=req_id,
        ),
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handler for standard FastAPI/Starlette HTTPException instances."""
    req_id = get_request_id(request)
    code = "HTTP_ERROR"
    if exc.status_code == 404:
        code = "NOT_FOUND"
    elif exc.status_code == 400:
        code = "BAD_REQUEST"
    elif exc.status_code == 401:
        code = "UNAUTHORIZED"
    elif exc.status_code == 403:
        code = "FORBIDDEN"

    return JSONResponse(
        status_code=exc.status_code,
        content=format_error_response(
            code=code,
            message=str(exc.detail),
            details=None,
            request_id=req_id,
        ),
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handler for Pydantic/FastAPI request validation errors (HTTP 422)."""
    req_id = get_request_id(request)
    formatted_errors = []
    for err in exc.errors():
        formatted_errors.append({
            "msg": str(err.get("msg", "")),
            "type": str(err.get("type", "")),
            "loc": [str(x) for x in err.get("loc", [])],
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=format_error_response(
            code="VALIDATION_ERROR",
            message="Request validation failed.",
            details=formatted_errors,
            request_id=req_id,
        ),
    )


async def unhandled_exception_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Handler for unexpected unhandled Python exceptions (HTTP 500)."""
    req_id = get_request_id(request)
    logger.exception("[%s] Unhandled exception occurred: %s", req_id, exc)

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=format_error_response(
            code="INTERNAL_SERVER_ERROR",
            message="An unexpected internal server error occurred.",
            details=None,
            request_id=req_id,
        ),
    )


__all__ = [
    "APIException",
    "NotFoundException",
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "InternalServerErrorException",
    "format_error_response",
    "api_exception_handler",
    "http_exception_handler",
    "validation_exception_handler",
    "unhandled_exception_handler",
]
