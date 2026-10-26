"""Stable machine-readable error codes and the standard error envelope.

Every error response has the shape
`{"error": {"code": ..., "message": ..., "details": {...}}, "request_id": ...}`.
Stack traces and internal paths are logged server-side only.
"""

import logging
from enum import StrEnum
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.request_context import get_request_id

logger = logging.getLogger(__name__)


class ErrorCode(StrEnum):
    INVALID_REQUEST = "INVALID_REQUEST"
    NOT_FOUND = "NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    UNSUPPORTED_SYMBOL = "UNSUPPORTED_SYMBOL"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    DATABASE_UNAVAILABLE = "DATABASE_UNAVAILABLE"
    NOT_READY = "NOT_READY"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    DATA_STALE = "DATA_STALE"
    MODEL_UNAVAILABLE = "MODEL_UNAVAILABLE"
    CALIBRATION_UNAVAILABLE = "CALIBRATION_UNAVAILABLE"
    NO_SIGNAL = "NO_SIGNAL"
    INTERNAL_ERROR = "INTERNAL_ERROR"


_STATUS_TO_CODE: dict[int, ErrorCode] = {
    400: ErrorCode.INVALID_REQUEST,
    404: ErrorCode.NOT_FOUND,
    405: ErrorCode.METHOD_NOT_ALLOWED,
    409: ErrorCode.CONFLICT,
    429: ErrorCode.RATE_LIMITED,
    503: ErrorCode.NOT_READY,
}


class ApiError(Exception):
    """Raise from route handlers to return a standard error envelope."""

    def __init__(
        self,
        status_code: int,
        code: ErrorCode,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or {}


def error_body(
    code: ErrorCode, message: str, details: dict[str, Any] | None = None
) -> dict[str, Any]:
    return {
        "error": {"code": code.value, "message": message, "details": details or {}},
        "request_id": get_request_id(),
    }


async def _api_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, ApiError):  # narrows the type for mypy
        raise exc
    return JSONResponse(
        status_code=exc.status_code, content=error_body(exc.code, exc.message, exc.details)
    )


async def _http_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, StarletteHTTPException):  # narrows the type for mypy
        raise exc
    code = _STATUS_TO_CODE.get(exc.status_code, ErrorCode.INVALID_REQUEST)
    message = exc.detail if isinstance(exc.detail, str) else code.value
    return JSONResponse(
        status_code=exc.status_code,
        content=error_body(code, message),
        headers=getattr(exc, "headers", None),
    )


async def _validation_error_handler(_: Request, exc: Exception) -> JSONResponse:
    if not isinstance(exc, RequestValidationError):  # narrows the type for mypy
        raise exc
    issues = [
        {"loc": [str(part) for part in err.get("loc", ())], "msg": str(err.get("msg", ""))}
        for err in exc.errors()
    ]
    return JSONResponse(
        status_code=400,
        content=error_body(
            ErrorCode.INVALID_REQUEST, "Request validation failed.", {"issues": issues}
        ),
    )


async def _unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
    logger.exception(
        "unhandled error", exc_info=exc, extra={"error_code": ErrorCode.INTERNAL_ERROR.value}
    )
    return JSONResponse(
        status_code=500,
        content=error_body(ErrorCode.INTERNAL_ERROR, "An internal error occurred."),
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(ApiError, _api_error_handler)
    app.add_exception_handler(StarletteHTTPException, _http_error_handler)
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(Exception, _unhandled_error_handler)
