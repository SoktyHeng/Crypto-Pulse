"""Migration tests against a real, freshly created PostgreSQL database."""

import pytest
from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from fastapi.testclient import TestClient
from sqlalchemy import Engine, inspect, text
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.db.session import get_engine
from app.main import create_app
from app.services.readiness import alembic_config, expected_schema_heads
from tests.conftest import make_settings

pytestmark = pytest.mark.integration


def _upgrade(url: str, revision: str = "head") -> None:
    config = alembic_config()
    config.attributes["database_url"] = url
    command.upgrade(config, revision)


def _downgrade(url: str, revision: str) -> None:
    config = alembic_config()
    config.attributes["database_url"] = url
    command.downgrade(config, revision)


def test_upgrade_from_empty_database_creates_schema(
    empty_database_url: str, empty_engine: Engine
) -> None:
    _upgrade(empty_database_url)
    inspector = inspect(empty_engine)
    assert {"exchanges", "assets", "markets", "alembic_version"} <= set(inspector.get_table_names())
    uniques = {u["name"] for u in inspector.get_unique_constraints("markets")}
    assert "uq_markets_exchange_id_provider_symbol" in uniques
    with empty_engine.connect() as conn:
        version = conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    assert {version} == expected_schema_heads()


def test_seeds_only_reference_markets(empty_database_url: str, empty_engine: Engine) -> None:
    _upgrade(empty_database_url)
    with empty_engine.connect() as conn:
        rows = conn.execute(
            text(
                """
                SELECT e.code, m.provider_symbol, b.symbol, q.symbol, m.status
                FROM markets m
                JOIN exchanges e ON e.id = m.exchange_id
                JOIN assets b ON b.id = m.base_asset_id
                JOIN assets q ON q.id = m.quote_asset_id
                ORDER BY m.provider_symbol
                """
            )
        ).all()
    assert [tuple(r) for r in rows] == [
        ("BINANCE_SPOT", "BTCUSDT", "BTC", "USDT", "CONFIGURED"),
        ("BINANCE_SPOT", "ETHUSDT", "ETH", "USDT", "CONFIGURED"),
        ("BINANCE_SPOT", "SOLUSDT", "SOL", "USDT", "CONFIGURED"),
    ]


def test_constraints_reject_invalid_reference_data(
    empty_database_url: str, empty_engine: Engine
) -> None:
    _upgrade(empty_database_url)
    duplicate_market = """
        INSERT INTO markets (exchange_id, base_asset_id, quote_asset_id, provider_symbol, status)
        SELECT exchange_id, base_asset_id, quote_asset_id, provider_symbol, status
        FROM markets WHERE provider_symbol = 'BTCUSDT'
    """
    bad_status = "UPDATE markets SET status = 'LIVE' WHERE provider_symbol = 'BTCUSDT'"
    same_assets = (
        "UPDATE markets SET quote_asset_id = base_asset_id WHERE provider_symbol = 'BTCUSDT'"
    )
    bad_exchange = "INSERT INTO exchanges (code, name) VALUES ('KRAKEN', 'Kraken')"
    lowercase_asset = "INSERT INTO assets (symbol, name) VALUES ('doge', 'Doge')"
    for statement in (duplicate_market, bad_status, same_assets, bad_exchange, lowercase_asset):
        with empty_engine.connect() as conn, pytest.raises(IntegrityError):
            conn.execute(text(statement))


def test_models_match_migrated_schema(empty_database_url: str, empty_engine: Engine) -> None:
    _upgrade(empty_database_url)
    with empty_engine.connect() as conn:
        context = MigrationContext.configure(conn, opts={"compare_type": True})
        diff = compare_metadata(context, Base.metadata)
    assert diff == []


def test_downgrade_to_base_and_upgrade_again(empty_database_url: str, empty_engine: Engine) -> None:
    _upgrade(empty_database_url)
    _downgrade(empty_database_url, "base")
    assert set(inspect(empty_engine).get_table_names()) == {"alembic_version"}
    _upgrade(empty_database_url)
    with empty_engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM markets")).scalar_one() == 3


def test_readiness_tracks_schema_state(empty_database_url: str, empty_engine: Engine) -> None:
    app = create_app(make_settings(database_url=empty_database_url))
    app.dependency_overrides[get_engine] = lambda: empty_engine
    client = TestClient(app)

    before = client.get("/api/v1/system/readiness")
    assert before.status_code == 503
    schema = next(c for c in before.json()["components"] if c["name"] == "schema")
    assert schema["state"] == "error"

    _upgrade(empty_database_url)
    after = client.get("/api/v1/system/readiness")
    assert after.status_code == 200
    body = after.json()
    assert body["status"] == "ready"
    states = {c["name"]: c["state"] for c in body["components"]}
    assert states == {
        "database": "ok",
        "schema": "ok",
        "reference_markets": "ok",
        "market_feed": "not_configured",
        "model": "unavailable",
    }
