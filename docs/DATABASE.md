# Database

PostgreSQL 17. The schema is managed **only** by Alembic (`services/backend/alembic`); nothing is
created at application startup. Revision files are named `YYYYMMDD_<rev>_<slug>.py`.

## Current schema (revision `0001`)

```mermaid
erDiagram
  exchanges ||--o{ markets : lists
  assets ||--o{ markets : "base asset"
  assets ||--o{ markets : "quote asset"
  exchanges { int id PK; varchar code UK; varchar name; bool enabled; timestamptz created_at }
  assets { int id PK; varchar symbol UK; varchar name; timestamptz created_at }
  markets { int id PK; int exchange_id FK; int base_asset_id FK; int quote_asset_id FK; varchar provider_symbol; varchar status; jsonb precision_json; timestamptz created_at }
```

| Constraint | Meaning |
|---|---|
| `uq_exchanges_code`, `ck_exchanges_code_allowed` | One row per exchange code; only `BINANCE_SPOT` allowed |
| `uq_assets_symbol`, `ck_assets_symbol_uppercase` | Unique uppercase tickers |
| `uq_markets_exchange_id_provider_symbol` | One market per exchange symbol |
| `ck_markets_status_allowed` | `CONFIGURED`, `TRADING`, `HALTED`, `DISABLED` |
| `ck_markets_distinct_assets` | Base ≠ quote |
| `ck_markets_symbol_uppercase` | Provider symbols are uppercase |
| FKs `ON DELETE RESTRICT` | Reference rows cannot be deleted while markets use them |

Seed data: the `BINANCE_SPOT` exchange, assets BTC/ETH/SOL/USDT, and markets BTCUSDT/ETHUSDT/SOLUSDT
with status `CONFIGURED`. This is reference metadata only; no observations are seeded.

Constraint names follow a deterministic convention (`app/db/base.py`), so migrations and models
stay comparable. A test asserts that the ORM metadata and the migrated schema have no diff.

## Planned tables

`candles`, `ingestion_cursors` and `ingestion_gaps` (M1); `feature_snapshots` and
`model_versions` (M3); `predictions`, `prediction_outcomes`, `evaluation_runs` and
`audit_events` (M4–M5), as specified in `CLAUDE.md` §9.

## Operations

```bash
docker compose run --rm migrate                               # upgrade to head
docker compose run --rm api alembic current
docker compose run --rm api alembic downgrade -1              # development only
docker compose exec postgres psql -U cryptopulse -d cryptopulse
```

Retention (MVP): keep all candle history and all prediction/outcome audit history.
