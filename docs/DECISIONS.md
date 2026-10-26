# Architecture Decision Records

Each record lists the context, the options considered, the decision and its consequences.
Deviations from `CLAUDE.md` are always recorded here.

## ADR-001 — Python 3.13 with uv and a committed `uv.lock` (M0, 2026-10-26)

- **Context:** CLAUDE.md §17 asks for a pinned Python minor version, `pyproject.toml` and locked
  dependencies.
- **Options:** pip-tools; Poetry; uv.
- **Decision:** Python **3.13** (`python:3.13-slim-bookworm`), managed with **uv 0.13.5** and a
  committed `uv.lock`. Docker and CI install with `uv sync --frozen`.
- **Why:** 3.13 is mature and every dependency supports it. uv's lockfile is cross-platform and
  fast, and the Docker workflow doesn't need Python on the host.

## ADR-002 — Next.js 16, TypeScript 6.0 and ESLint 9 (M0)

- **Decision:** Next.js 16.4 (App Router, Turbopack build), React 19.3, TypeScript ~6.0.
- **TypeScript 7** (the native compiler) is not used yet: `typescript-eslint` 8.72 supports
  TypeScript `<6.1`.
- **ESLint 9** is pinned even though it is end-of-life. The plugins bundled with
  `eslint-config-next` 16.4.3 (`eslint-plugin-react`, `-import`, `-jsx-a11y`) declare ESLint ≤9 as
  a peer, so ESLint 10 would only install with forced peer overrides.
- **Revisit:** move to ESLint 10 when `eslint-config-next` supports it.

## ADR-003 — `httpx2` for the Starlette test client (M0)

Starlette now deprecates `httpx` in `starlette.testclient`, and pytest runs with
`filterwarnings=error`. The dev dependency is `httpx2` (published by the pydantic org). The HTTP
client for Binance ingestion is a separate choice that M1 will make.

## ADR-004 — Enumerations stored as VARCHAR + CHECK, not PostgreSQL ENUM (M0)

- **Options:** native `ENUM` types; lookup tables; `VARCHAR` with named `CHECK` constraints.
- **Decision:** `VARCHAR` + `CHECK` (for example `ck_markets_status_allowed`). Adding a value
  means replacing one constraint in a migration; no `ALTER TYPE` is needed. Migrations freeze
  their own value lists and never import live application enums.

## ADR-005 — Reference markets seeded by migration with status `CONFIGURED` (M0)

The three whitelisted markets (and BTC/ETH/SOL/USDT assets plus the `BINANCE_SPOT` exchange) are
static reference metadata, so they are seeded in migration `0001`. No prices or observations are
seeded. The status is `CONFIGURED`, not `TRADING`, because nothing has been verified against
Binance `exchangeInfo` yet. M1 performs that verification.

## ADR-006 — Compose services are added with the milestone that implements them (M0)

CLAUDE.md §13.2 lists `collector`, `prediction-worker`, `outcome-worker` and `training`. Adding
them as empty containers in M0 would show "running" services that do nothing, which is
misleading. M0 ships `postgres`, `migrate` (one-off), `api` and `web`. Readiness reports
`market_feed: not_configured` and `model: unavailable` explicitly. The collector arrives in M1,
training in M3 and the workers in M4.

## ADR-007 — Local web image keeps sources and dev tooling (M0)

The compose `web` image runs `next start` on a production build but keeps sources and
devDependencies, so `docker compose exec web npm run lint|typecheck|test` (CLAUDE.md §13.3) work.
A slim `output: "standalone"` production image is planned for M5. `NODE_ENV` is not set in the
image: `next start` serves production mode anyway, and leaving it unset lets tests run React in
test mode.

## ADR-008 — Readiness returns 503 with a diagnostic body (M0)

`/api/v1/system/readiness` returns `200` when the database, schema revision and reference markets
are OK. Otherwise it returns `503`, with the same `ReadinessResponse` body naming the failing
component, rather than the generic error envelope. Messages are sanitized: no hosts,
credentials, driver errors or paths. A missing market feed or model never makes the API
"not ready", because the UI must work without them.

## ADR-009 — Integration tests use throwaway databases (M0)

Integration tests create a uniquely named database on the `TEST_DATABASE_URL` server for each
test and drop it afterwards. Running `pytest` inside the compose stack therefore never touches
the development database. When `CI` is set and `TEST_DATABASE_URL` is missing, the run fails
instead of skipping.

## Open decisions (to be made in later milestones)

- Real-time interface: SSE `GET /api/v1/stream` vs `WS /ws/v1/market` (M1/M2).
- HTTP/WebSocket client libraries for ingestion (M1).
- Rate-limiting implementation for public routes (M1/M5).
- Movement thresholds per horizon (M3), chosen on training data only.
