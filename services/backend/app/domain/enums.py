"""Canonical enumerations.

These values are part of the public API and database contracts. Changing or reordering a
member is a breaking change: add a migration and update `docs/DATA_CONTRACTS.md` and the
frontend mirror in `apps/web/lib/markets.ts`.
"""

from enum import IntEnum, StrEnum


class ExchangeCode(StrEnum):
    """Exchanges whose public market data we consume. MVP: Binance Spot only."""

    BINANCE_SPOT = "BINANCE_SPOT"


class SupportedSymbol(StrEnum):
    """Binance Spot USDT-quoted markets in the MVP whitelist (never global averages)."""

    BTCUSDT = "BTCUSDT"
    ETHUSDT = "ETHUSDT"
    SOLUSDT = "SOLUSDT"


class MarketStatus(StrEnum):
    """Lifecycle of a market row.

    `CONFIGURED` means whitelisted by configuration but not yet verified against the
    exchange's `exchangeInfo` endpoint (verification arrives with ingestion in M1).
    """

    CONFIGURED = "CONFIGURED"
    TRADING = "TRADING"
    HALTED = "HALTED"
    DISABLED = "DISABLED"


class CandleInterval(StrEnum):
    """Chart/candle sampling intervals. Distinct from forecast horizons."""

    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    H1 = "1h"
    H4 = "4h"

    @property
    def minutes(self) -> int:
        return _INTERVAL_MINUTES[self]


_INTERVAL_MINUTES: dict[CandleInterval, int] = {
    CandleInterval.M1: 1,
    CandleInterval.M5: 5,
    CandleInterval.M15: 15,
    CandleInterval.H1: 60,
    CandleInterval.H4: 240,
}


class HorizonMinutes(IntEnum):
    """Forecast horizons. 5m is research-gated and excluded from the public MVP."""

    M5 = 5
    M15 = 15
    M30 = 30
    H1 = 60
    H4 = 240


PUBLIC_MVP_HORIZONS: tuple[HorizonMinutes, ...] = (
    HorizonMinutes.M15,
    HorizonMinutes.M30,
    HorizonMinutes.H1,
    HorizonMinutes.H4,
)


class PredictedClass(StrEnum):
    """Direction classes. Iteration order is the canonical model output order."""

    UP = "UP"
    DOWN = "DOWN"
    SIDEWAYS = "SIDEWAYS"


CANONICAL_CLASS_ORDER: tuple[PredictedClass, ...] = tuple(PredictedClass)


class DecisionStatus(StrEnum):
    ACTIVE = "ACTIVE"
    NO_SIGNAL = "NO_SIGNAL"


class DataStatus(StrEnum):
    FRESH = "FRESH"
    DATA_STALE = "DATA_STALE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    INSUFFICIENT_HISTORY = "INSUFFICIENT_HISTORY"


class FeedStatus(StrEnum):
    CONNECTED = "CONNECTED"
    RECONNECTING = "RECONNECTING"
    DEGRADED = "DEGRADED"
    STALE = "STALE"
    OFFLINE = "OFFLINE"


class ModelStatus(StrEnum):
    CANDIDATE = "CANDIDATE"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"
    REJECTED = "REJECTED"


class SettlementState(StrEnum):
    SETTLED = "SETTLED"
    PENDING_DATA = "PENDING_DATA"
    UNRESOLVED = "UNRESOLVED"
