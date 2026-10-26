"""Reference entities: exchanges, assets and markets.

Enumerated columns are stored as VARCHAR guarded by CHECK constraints (see ADR-004 in
`docs/DECISIONS.md`) so new values only need a constraint migration.
"""

from datetime import datetime
from typing import Any

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.domain.enums import ExchangeCode, MarketStatus


def _in_check(column: str, values: list[str]) -> str:
    quoted = ", ".join(f"'{value}'" for value in values)
    return f"{column} IN ({quoted})"


EXCHANGE_CODE_CHECK = _in_check("code", [code.value for code in ExchangeCode])
MARKET_STATUS_CHECK = _in_check("status", [status.value for status in MarketStatus])


class Exchange(Base):
    __tablename__ = "exchanges"
    __table_args__ = (CheckConstraint(EXCHANGE_CODE_CHECK, name="code_allowed"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(32), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Asset(Base):
    __tablename__ = "assets"
    __table_args__ = (CheckConstraint("symbol = upper(symbol)", name="symbol_uppercase"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Market(Base):
    __tablename__ = "markets"
    __table_args__ = (
        UniqueConstraint("exchange_id", "provider_symbol"),
        CheckConstraint("base_asset_id <> quote_asset_id", name="distinct_assets"),
        CheckConstraint(MARKET_STATUS_CHECK, name="status_allowed"),
        CheckConstraint("provider_symbol = upper(provider_symbol)", name="symbol_uppercase"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exchange_id: Mapped[int] = mapped_column(ForeignKey("exchanges.id", ondelete="RESTRICT"))
    base_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"))
    quote_asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id", ondelete="RESTRICT"))
    provider_symbol: Mapped[str] = mapped_column(String(32))
    status: Mapped[str] = mapped_column(String(16))
    precision_json: Mapped[dict[str, Any]] = mapped_column(
        JSONB, server_default=text("'{}'::jsonb")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
