"""`/api/v1/system/*`: liveness and sanitized readiness."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import Engine

from app import __version__
from app.core.config import Settings, get_settings
from app.db.session import get_engine
from app.schemas.system import ErrorEnvelope, HealthResponse, ReadinessResponse
from app.services.readiness import check_readiness

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Annotated[Settings, Depends(get_settings)]) -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="cryptopulse-api",
        version=__version__,
        environment=settings.app_env,
        time=datetime.now(UTC),
    )


@router.get(
    "/readiness",
    response_model=ReadinessResponse,
    responses={
        503: {"model": ReadinessResponse, "description": "A required dependency is not ready."},
        500: {"model": ErrorEnvelope},
    },
)
def readiness(
    response: Response,
    settings: Annotated[Settings, Depends(get_settings)],
    engine: Annotated[Engine, Depends(get_engine)],
) -> ReadinessResponse:
    result = check_readiness(engine, settings.supported_symbols)
    if result.status != "ready":
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    return result
