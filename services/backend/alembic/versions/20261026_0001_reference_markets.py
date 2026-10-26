"""Reference entities (exchanges, assets, markets) and the MVP market whitelist.

Seeds only static reference metadata (exchange code, asset tickers, market symbols). No
prices, candles or other market observations are created here. Markets start as
CONFIGURED until verified against Binance `exchangeInfo` (M1).

Revision ID: 0001
Revises:
Create Date: 2026-10-26 00:00:00+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Frozen copies of the values at the time of this revision. Migrations must not import
# live application enums, because later edits would silently rewrite history.
EXCHANGE_CODES = ("BINANCE_SPOT",)
MARKET_STATUSES = ("CONFIGURED", "TRADING", "HALTED", "DISABLED")
ASSETS = (("BTC", "Bitcoin"), ("ETH", "Ethereum"), ("SOL", "Solana"), ("USDT", "Tether USD"))
MARKETS = (("BTC", "USDT", "BTCUSDT"), ("ETH", "USDT", "ETHUSDT"), ("SOL", "USDT", "SOLUSDT"))


def _in(column: str, values: Sequence[str]) -> str:
    return f"{column} IN ({', '.join(repr(v) for v in values)})"


def upgrade() -> None:
    op.create_table(
        "exchanges",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(32), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(_in("code", EXCHANGE_CODES), name=op.f("ck_exchanges_code_allowed")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_exchanges")),
        sa.UniqueConstraint("code", name=op.f("uq_exchanges_code")),
    )
    op.create_table(
        "assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint("symbol = upper(symbol)", name=op.f("ck_assets_symbol_uppercase")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_assets")),
        sa.UniqueConstraint("symbol", name=op.f("uq_assets_symbol")),
    )
    op.create_table(
        "markets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("exchange_id", sa.Integer(), nullable=False),
        sa.Column("base_asset_id", sa.Integer(), nullable=False),
        sa.Column("quote_asset_id", sa.Integer(), nullable=False),
        sa.Column("provider_symbol", sa.String(32), nullable=False),
        sa.Column("status", sa.String(16), nullable=False),
        sa.Column(
            "precision_json",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.CheckConstraint(
            "base_asset_id <> quote_asset_id", name=op.f("ck_markets_distinct_assets")
        ),
        sa.CheckConstraint(_in("status", MARKET_STATUSES), name=op.f("ck_markets_status_allowed")),
        sa.CheckConstraint(
            "provider_symbol = upper(provider_symbol)", name=op.f("ck_markets_symbol_uppercase")
        ),
        sa.ForeignKeyConstraint(
            ["exchange_id"],
            ["exchanges.id"],
            name=op.f("fk_markets_exchange_id_exchanges"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["base_asset_id"],
            ["assets.id"],
            name=op.f("fk_markets_base_asset_id_assets"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["quote_asset_id"],
            ["assets.id"],
            name=op.f("fk_markets_quote_asset_id_assets"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_markets")),
        sa.UniqueConstraint(
            "exchange_id", "provider_symbol", name=op.f("uq_markets_exchange_id_provider_symbol")
        ),
    )

    # Reference seed (static metadata only; parameterized statements).
    conn = op.get_bind()
    conn.execute(
        sa.text("INSERT INTO exchanges (code, name) VALUES (:code, :name)"),
        {"code": "BINANCE_SPOT", "name": "Binance Spot"},
    )
    conn.execute(
        sa.text("INSERT INTO assets (symbol, name) VALUES (:symbol, :name)"),
        [{"symbol": symbol, "name": name} for symbol, name in ASSETS],
    )
    conn.execute(
        sa.text(
            """
            INSERT INTO markets
                (exchange_id, base_asset_id, quote_asset_id, provider_symbol, status)
            SELECT e.id, b.id, q.id, :provider_symbol, 'CONFIGURED'
            FROM exchanges e, assets b, assets q
            WHERE e.code = 'BINANCE_SPOT' AND b.symbol = :base AND q.symbol = :quote
            """
        ),
        [{"base": b, "quote": q, "provider_symbol": s} for b, q, s in MARKETS],
    )


def downgrade() -> None:
    op.drop_table("markets")
    op.drop_table("assets")
    op.drop_table("exchanges")
