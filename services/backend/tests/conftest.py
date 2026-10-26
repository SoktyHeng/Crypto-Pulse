"""Shared fixtures.

Unit tests never need a database. Integration tests (marker `integration`) need a PostgreSQL
server at TEST_DATABASE_URL; each test session creates a uniquely named throwaway database
on that server and drops it afterwards, so the development database is never touched.
"""

import os
import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.engine import make_url

from app.core.config import Settings
from app.db.session import build_engine, get_engine
from app.main import create_app

# Port 9 (discard) on localhost: connection is refused immediately.
UNREACHABLE_DATABASE_URL = "postgresql+psycopg://user:s3cret-pw@127.0.0.1:9/nodb"


def make_settings(**overrides: object) -> Settings:
    values: dict[str, object] = {"app_env": "test", "log_level": "WARNING"}
    values.update(overrides)
    return Settings.model_validate(values)


@pytest.fixture
def settings() -> Settings:
    return make_settings(database_url=UNREACHABLE_DATABASE_URL, database_connect_timeout_seconds=1)


@pytest.fixture
def client(settings: Settings) -> Iterator[TestClient]:
    app = create_app(settings)
    engine = build_engine(settings)
    app.dependency_overrides[get_engine] = lambda: engine
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    engine.dispose()


# --- integration ---------------------------------------------------------------------------


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    if os.environ.get("TEST_DATABASE_URL"):
        return
    if os.environ.get("CI"):
        # Never let CI pass by silently skipping the database-backed suite.
        raise pytest.UsageError("TEST_DATABASE_URL must be set in CI")
    reason = "TEST_DATABASE_URL is not set; integration tests need a PostgreSQL server"
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(pytest.mark.skip(reason=reason))


@pytest.fixture(scope="session")
def server_url() -> str:
    return os.environ["TEST_DATABASE_URL"]


@pytest.fixture
def empty_database_url(server_url: str) -> Iterator[str]:
    """A brand-new empty database, dropped after the test."""
    name = f"cryptopulse_test_{uuid.uuid4().hex[:12]}"
    admin = create_engine(server_url, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text(f'CREATE DATABASE "{name}"'))
    try:
        yield make_url(server_url).set(database=name).render_as_string(hide_password=False)
    finally:
        with admin.connect() as conn:
            conn.execute(text(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)'))
        admin.dispose()


@pytest.fixture
def empty_engine(empty_database_url: str) -> Iterator[Engine]:
    engine = create_engine(empty_database_url)
    yield engine
    engine.dispose()
