"""Structured JSON logging to stdout.

Every record is one JSON object with a UTC timestamp, level, logger, component and message,
plus any whitelisted context passed via `extra=`. Values whose key looks secret are redacted.
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.request_context import get_request_id

CONTEXT_FIELDS = (
    "component",
    "request_id",
    "job_id",
    "symbol",
    "method",
    "path",
    "status_code",
    "duration_ms",
    "event_time",
    "lag_ms",
    "model_id",
    "error_code",
)
_SECRET_MARKERS = ("password", "secret", "token", "api_key", "authorization", "database_url")
REDACTED = "[REDACTED]"


def _is_secret_key(key: str) -> bool:
    lowered = key.lower()
    return any(marker in lowered for marker in _SECRET_MARKERS)


class JsonFormatter(logging.Formatter):
    def __init__(self, component: str) -> None:
        super().__init__()
        self._component = component

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "component": self._component,
            "message": record.getMessage(),
        }
        request_id = get_request_id()
        if request_id:
            payload["request_id"] = request_id
        for field in CONTEXT_FIELDS:
            if hasattr(record, field):
                payload[field] = getattr(record, field)
        extra_context = getattr(record, "context", None)
        if isinstance(extra_context, dict):
            for key, value in extra_context.items():
                payload[key] = REDACTED if _is_secret_key(str(key)) else value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str, component: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(component))
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    # Uvicorn installs its own handlers; route them through the JSON formatter instead.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uv_logger = logging.getLogger(name)
        uv_logger.handlers.clear()
        uv_logger.propagate = True
    # RequestContextMiddleware writes the structured access line; avoid a duplicate one.
    logging.getLogger("uvicorn.access").disabled = True
