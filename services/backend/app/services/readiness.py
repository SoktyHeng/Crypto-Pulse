"""Readiness diagnostics: database reachability, schema version and reference data.

Messages are deliberately generic: no hostnames, credentials, driver errors or file paths.
Full exception details go to the server log only.
"""

import logging
from datetime import UTC, datetime
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import Engine, func, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.errors import ErrorCode
from app.domain.enums import ExchangeCode, SupportedSymbol
from app.models.reference import Exchange, Market
from app.schemas.system import ComponentStatus, ReadinessResponse

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parents[2]


def alembic_config() -> Config:
    config = Config()
    config.set_main_option("script_location", str(BACKEND_ROOT / "alembic"))
    return config


def expected_schema_heads() -> set[str]:
    return set(ScriptDirectory.from_config(alembic_config()).get_heads())


def _check_database(session: Session) -> ComponentStatus:
    session.execute(text("SELECT 1"))
    return ComponentStatus(name="database", state="ok", message="Database reachable.")


def _check_migrations(session: Session) -> ComponentStatus:
    try:
        rows = session.execute(text("SELECT version_num FROM alembic_version")).scalars().all()
    except SQLAlchemyError:
        session.rollback()
        rows = []
    if set(rows) == expected_schema_heads():
        return ComponentStatus(
            name="schema", state="ok", message="Schema is at the latest revision."
        )
    return ComponentStatus(
        name="schema",
        state="error",
        code=ErrorCode.NOT_READY.value,
        message="Database schema is not at the latest revision; run migrations.",
    )


def _check_reference_markets(session: Session, symbols: list[SupportedSymbol]) -> ComponentStatus:
    found = session.execute(
        select(func.count())
        .select_from(Market)
        .join(Exchange, Exchange.id == Market.exchange_id)
        .where(
            Exchange.code == ExchangeCode.BINANCE_SPOT.value,
            Market.provider_symbol.in_([s.value for s in symbols]),
        )
    ).scalar_one()
    if found == len(symbols):
        return ComponentStatus(
            name="reference_markets", state="ok", message=f"{found} configured markets present."
        )
    return ComponentStatus(
        name="reference_markets",
        state="error",
        code=ErrorCode.NOT_READY.value,
        message="Configured markets are missing from the database; run migrations.",
    )


# Components that are reported honestly but are not implemented yet; they never make
# the API "not ready", because the UI must work without market data or a model.
INFORMATIONAL_COMPONENTS: tuple[ComponentStatus, ...] = (
    ComponentStatus(
        name="market_feed",
        state="not_configured",
        code=ErrorCode.DATA_UNAVAILABLE.value,
        message="Market data collector is not running; no market data is available.",
    ),
    ComponentStatus(
        name="model",
        state="unavailable",
        code=ErrorCode.MODEL_UNAVAILABLE.value,
        message="No approved model is installed; no forecasts are published.",
    ),
)


def check_readiness(engine: Engine, symbols: list[SupportedSymbol]) -> ReadinessResponse:
    components: list[ComponentStatus] = []
    try:
        with Session(engine) as session:
            components.append(_check_database(session))
            components.append(_check_migrations(session))
            if components[-1].state == "ok":
                components.append(_check_reference_markets(session, symbols))
    except SQLAlchemyError:
        logger.warning(
            "readiness database check failed",
            exc_info=True,
            extra={"error_code": ErrorCode.DATABASE_UNAVAILABLE.value},
        )
        components = [
            ComponentStatus(
                name="database",
                state="error",
                code=ErrorCode.DATABASE_UNAVAILABLE.value,
                message="Database is unreachable.",
            )
        ]
    ready = all(component.state == "ok" for component in components)
    return ReadinessResponse(
        status="ready" if ready else "not_ready",
        checked_at=datetime.now(UTC),
        components=[*components, *INFORMATIONAL_COMPONENTS],
    )
