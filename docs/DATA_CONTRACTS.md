# Data contracts

## Market identity

| Field | Value |
|---|---|
| Exchange code | `BINANCE_SPOT` (Binance Spot only; never futures, never cross-exchange averages) |
| Symbols | `BTCUSDT`, `ETHUSDT`, `SOLUSDT` (USDT-quoted spot markets) |
| Status before verification | `CONFIGURED` (see ADR-005) |

## Canonical enums (`app/domain/enums.py`; frontend mirror `apps/web/lib/markets.ts`)

| Enum | Values |
|---|---|
| Candle interval | `1m`, `5m`, `15m`, `1h`, `4h` (chart sampling only) |
| Forecast horizon (minutes) | `15`, `30`, `60`, `240` public; `5` research-gated |
| Predicted class (canonical order) | `UP`, `DOWN`, `SIDEWAYS` |
| Decision status | `ACTIVE`, `NO_SIGNAL` |
| Data status | `FRESH`, `DATA_STALE`, `DATA_UNAVAILABLE`, `INSUFFICIENT_HISTORY` |
| Feed status | `CONNECTED`, `RECONNECTING`, `DEGRADED`, `STALE`, `OFFLINE` |
| Model status | `CANDIDATE`, `APPROVED`, `ACTIVE`, `RETIRED`, `REJECTED` |
| Settlement state | `SETTLED`, `PENDING_DATA`, `UNRESOLVED` |

## Provider endpoints (to be verified at M1 implementation time)

| Purpose | Endpoint |
|---|---|
| REST base (market data only) | `https://data-api.binance.vision` |
| Klines | `GET /api/v3/klines` |
| Exchange info | `GET /api/v3/exchangeInfo` |
| WebSocket base | `wss://data-stream.binance.vision:443/ws/` (lowercase stream names, e.g. `btcusdt@kline_1m`) |
| Bulk archives | `https://github.com/binance/binance-public-data` (newer spot archives may use **microsecond** timestamps) |

No API keys are used. Rate limits, connection lifetimes and redistribution terms are verified
and recorded here in M1.

## Timestamps and numbers

- Stored as `TIMESTAMPTZ` in UTC; database sessions run with `timezone=UTC`; API responses are ISO
  8601 with an offset.
- Binance REST/WS use Unix **milliseconds**; archive units are detected explicitly (M1).
- Prices and volumes are stored as `NUMERIC`, transported as decimal strings, and converted to
  float only inside ML features.

## Candle validation rules (implemented in M1)

Whitelisted symbol; supported interval; valid open/close times; `open > 0`, `low > 0`,
`high >= max(open, close)`, `low <= min(open, close)`; volumes and trade count `>= 0`; only
finalized (`k.x == true`) candles persisted; unique `(market_id, interval, open_time)`; gaps
detected, never forward-filled. The raw Binance kline field mapping will be documented here in M1.
