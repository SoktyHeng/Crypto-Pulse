"""API schemas for the system health/readiness endpoints."""

from typing import Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict

ComponentState = Literal["ok", "error", "not_configured", "unavailable"]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict[str, object]


class ErrorEnvelope(BaseModel):
    error: ErrorDetail
    request_id: str | None


class HealthResponse(BaseModel):
    """Liveness only: the process is up. Says nothing about dependencies."""

    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]
    service: Literal["cryptopulse-api"]
    version: str
    environment: str
    time: AwareDatetime


class ComponentStatus(BaseModel):
    name: str
    state: ComponentState
    code: str | None = None
    message: str


class ReadinessResponse(BaseModel):
    """Sanitized dependency diagnostics. Never includes hosts, credentials or paths."""

    status: Literal["ready", "not_ready"]
    checked_at: AwareDatetime
    components: list[ComponentStatus]
