"""Engine/session factories. Schema is managed only by Alembic, never at app startup."""

from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, get_settings


def build_engine(settings: Settings) -> Engine:
    return create_engine(
        settings.database_url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        connect_args={
            "connect_timeout": settings.database_connect_timeout_seconds,
            "options": "-c timezone=UTC -c statement_timeout=5000",
        },
    )


@lru_cache
def get_engine() -> Engine:
    return build_engine(get_settings())


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding a session bound to the cached engine."""
    factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with factory() as session:
        yield session
