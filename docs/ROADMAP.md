# Roadmap and acceptance matrix

| Milestone | Scope | Status |
|---|---|---|
| **M0** | Foundation: repo, docs, Docker Compose, FastAPI skeleton, migrations, Next.js shell, CI | **Done (2026-10-26)** |
| M1 | Binance Spot public ingestion: backfill, closed-candle WebSocket, upsert, gaps, feed status, market API | Not started |
| M2 | Market UI and indicators: dashboard, coin pages, Lightweight Charts, EMA/RSI/MACD/BB/ATR | Not started |
| M3 | Research pipeline: features, labels, baselines, XGBoost, purged walk-forward, calibration, registry | Not started |
| M4 | Inference, immutable forecast history, explanations, outcome settlement | Not started |
| M5 | Evaluation dashboard, security hardening, backups, release docs | Not started |
| M6 | Optional research extensions | Not planned |

## M0 acceptance checklist

| Criterion | Evidence |
|---|---|
| `docker compose up --build` starts UI/API/DB from a fresh clone | Verified on 2026-10-26: only git-tracked files copied to a clean directory; empty volumes; `postgres`, `api` and `web` healthy, `migrate` exited 0 |
| Frontend works | All 8 pages render (Playwright: 22 tests at 1280px and 360px, against `next start` and against the compose stack) |
| API health page works | `/api/v1/system/health` returns 200; `/system` page shows live API status (or an explicit offline state) |
| Schema migration works | `alembic upgrade head` on an empty DB; downgrade to base and re-upgrade; ORM ↔ schema diff is empty; constraints enforced (pytest integration suite) |
| No paid accounts | Only OSS images and packages; no API keys; no hosted services |
| Lint/typecheck/tests pass | Ruff, mypy strict, pytest 37/37; ESLint, tsc, Prettier, Vitest 20/20, `next build`, Playwright 22/22 |
| README clean-start instructions accurate | Each documented compose command was run against the fresh-clone stack |
| No fictitious forecast displayed | UI shows `MODEL_UNAVAILABLE` / `DATA_UNAVAILABLE`; tests assert no prices, percentages, `NaN` or `undefined` |
