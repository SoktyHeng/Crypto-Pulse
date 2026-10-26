"""Request-id propagation and JSON access logging."""

import logging
import re
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import set_request_id

REQUEST_ID_HEADER = "X-Request-ID"
# Accept a caller-supplied id only if it is short and safe to echo into logs/headers.
_SAFE_REQUEST_ID = re.compile(r"^[A-Za-z0-9._-]{1,64}$")

access_logger = logging.getLogger("app.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER, "")
        request_id = incoming if _SAFE_REQUEST_ID.fullmatch(incoming) else uuid.uuid4().hex
        set_request_id(request_id)
        started = time.perf_counter()
        status_code = 500
        try:
            response = await call_next(request)
            status_code = response.status_code
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            access_logger.info(
                "request",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": status_code,
                    "duration_ms": round((time.perf_counter() - started) * 1000, 2),
                },
            )
            # The context var is not reset here: each ASGI request runs in its own context,
            # and the outermost 500 handler still needs the id for its error envelope.
