# Changelog

## M0 — Foundation (2026-10-26)

### Added
- Repository skeleton: `.env.example`, `.gitignore`, `.gitattributes`, `.editorconfig`,
  `Makefile`, `docker-compose.yml` (postgres, one-off migrate, api, web; loopback-only ports,
  health checks, memory limits).
- Backend (`services/backend`): FastAPI app factory; typed settings with whitelist validation;
  JSON structured logging with secret redaction; request-id middleware; standard error envelope;
  `GET /api/v1/system/health` and `GET /api/v1/system/readiness`; canonical domain enums.
- Database: SQLAlchemy 2 models and Alembic migration `0001` (`exchanges`, `assets`, `markets`
  with unique/check/foreign-key constraints), plus a reference seed of the three Binance Spot USDT
  markets.
- Web (`apps/web`): Next.js 16 App Router shell with desktop sidebar, mobile bottom bar,
  dark/light theme, skip link, security headers; pages `/`, `/markets/[symbol]`, `/predictions`,
  `/predictions/history`, `/backtesting`, `/system`, `/methodology`, `/limitations`; loading,
  empty, error and offline states; typed, zod-validated API client.
- Tests: pytest (unit + PostgreSQL integration with throwaway databases), Vitest, Playwright
  smoke tests at desktop and 360px widths.
- CI (`.github/workflows/ci.yml`): backend, web and full compose-stack jobs.
- Documentation set in `docs/`.
