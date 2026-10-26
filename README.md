# CryptoPulse AI

Transparent, auditable short-horizon trend analysis for **Binance Spot** `BTCUSDT`, `ETHUSDT` and
`SOLUSDT`. CryptoPulse AI is a market-analysis product, **not a trading bot and not financial
advice**. It is built to *measure whether forecasts work*, not to display convincing but
unvalidated predictions.

> **Status: M0 (foundation).** The app shell, API skeleton, database and migrations run locally.
> There is **no market data and no forecasting model yet**; the UI says so explicitly
> (`DATA_UNAVAILABLE`, `MODEL_UNAVAILABLE`) instead of showing placeholder numbers.
> See [docs/ROADMAP.md](docs/ROADMAP.md).

## Stack

| Layer | Technology |
|---|---|
| Web | Next.js 16 (App Router) · TypeScript strict · Tailwind CSS 4 · shadcn/ui · Lucide · TanStack Query · zod |
| API | Python 3.13 · FastAPI · Pydantic v2 · SQLAlchemy 2 · Alembic |
| Database | PostgreSQL 17 |
| Tooling | uv (locked), Ruff, mypy, pytest · ESLint, Prettier, Vitest, Playwright |
| Runtime | Docker Compose, local only — no paid services, accounts or API keys |

## Quick start (fresh clone)

Requirements: Docker with Compose v2. Docker Desktop is free for personal use, but check its
licence terms if you use it inside an organisation. Nothing else needs to be installed on the host.

```bash
cp .env.example .env            # local, non-secret defaults (optional: compose has the same defaults)
docker compose up --build -d    # postgres → migrate (one-off) → api → web
docker compose ps               # api, web, postgres "healthy"; migrate "Exited (0)"
```

Then open:

- Web app: <http://localhost:3000> (the **System status** page shows live API health/readiness)
- API liveness: <http://localhost:8000/api/v1/system/health>
- API readiness: <http://localhost:8000/api/v1/system/readiness>
- OpenAPI docs: <http://localhost:8000/api/v1/docs>

All ports bind to `127.0.0.1` only. Stop with `docker compose down`; add `-v` to also delete the
database volume.

## Everyday commands

```bash
docker compose logs -f api                              # JSON structured logs
docker compose run --rm migrate                         # apply migrations (same as below)
docker compose run --rm api alembic upgrade head
docker compose run --rm api pytest                      # unit + PostgreSQL integration tests
docker compose run --rm --no-deps api sh -c "ruff check . && ruff format --check . && mypy"
docker compose exec web npm run lint
docker compose exec web npm run typecheck
docker compose exec web npm test
docker compose down
```

The `Makefile` wraps these (`make up`, `make test-api`, `make web-check`, …), but `make` is
optional.

Data ingestion (`backfill`), training and evaluation commands arrive with M1 and M3. Until then
they do not exist; see the roadmap.

### Working outside Docker

```bash
# Backend (needs uv: https://docs.astral.sh/uv/)
cd services/backend
uv sync
DATABASE_URL=postgresql+psycopg://cryptopulse:local_change_me@localhost:5432/cryptopulse uv run alembic upgrade head
DATABASE_URL=... uv run uvicorn app.main:app --reload
TEST_DATABASE_URL=postgresql+psycopg://cryptopulse:local_change_me@localhost:5432/postgres uv run pytest

# Web (Node 22.12+; Node 24 used in Docker/CI)
cd apps/web
npm ci
npm run dev                       # http://localhost:3000
npm run check                     # lint + typecheck + prettier + vitest
npm run build && npm run e2e      # Playwright smoke tests (installs: npx playwright install chromium)
E2E_BASE_URL=http://localhost:3000 npm run e2e   # against the running compose stack
```

Without `TEST_DATABASE_URL`, the PostgreSQL integration tests are **reported as skipped, with the
reason**. In CI they are mandatory: the run fails if the variable is missing.

## Configuration

Every setting is listed with its default in [.env.example](.env.example). Key points:

- `DATABASE_URL` uses host `postgres` inside Docker, and `localhost:${POSTGRES_HOST_PORT}` from the host.
- `NEXT_PUBLIC_API_BASE_URL` is the API address **as seen by the browser** (host machine). It is
  baked into the web bundle at build time, so rebuild `web` after changing it. Never put
  secrets in `NEXT_PUBLIC_*` values.
- `local_change_me` is a local-only example password. Override it everywhere else.
- `SUPPORTED_SYMBOLS` must be a subset of the whitelist. `PREDICTION_HORIZONS_MINUTES` rejects the
  research-gated 5-minute horizon. Wildcard CORS origins are rejected.
- `ENABLE_DEMO_MODE=false`. Demo fixtures, when they exist, must be watermarked and are never on
  by default.

## Repository layout

```text
apps/web/            Next.js app (app/, components/, hooks/, lib/, tests/, e2e/)
services/backend/    FastAPI app (app/), Alembic migrations (alembic/), tests/
docs/                Product, architecture, contracts, decisions, roadmap, changelog
artifacts/           Local model artifacts/reports (git-ignored, never committed)
.github/workflows/   CI: backend, web, full compose stack
```

## Documentation

[PRD](docs/PRD.md) · [Architecture](docs/ARCHITECTURE.md) · [Data contracts](docs/DATA_CONTRACTS.md) ·
[Database](docs/DATABASE.md) · [API](docs/API.md) · [ML spec](docs/ML_SPEC.md) ·
[Backtesting](docs/BACKTESTING.md) · [UI/UX](docs/UI_UX.md) · [Security](docs/SECURITY.md) ·
[Operations](docs/OPERATIONS.md) · [Decisions](docs/DECISIONS.md) · [Roadmap](docs/ROADMAP.md) ·
[Changelog](docs/CHANGELOG.md)

## Disclaimer

Informational analysis only. CryptoPulse AI does not place orders or give investment advice, and
it does not guarantee any outcome. Binance market-data usage and redistribution terms must be
verified before any public or commercial deployment.
