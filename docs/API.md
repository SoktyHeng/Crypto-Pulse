# API contract

Base path `/api/v1`. OpenAPI: `GET /api/v1/openapi.json`; interactive docs at `/api/v1/docs`. All
endpoints are read-only `GET`; other methods return `405`. Timestamps are UTC ISO 8601 with an
offset.

## Conventions

- **Request id:** every response carries `X-Request-ID`. A caller-supplied id is echoed only if it
  matches `[A-Za-z0-9._-]{1,64}`; otherwise a new one is generated.
- **CORS:** only the origins in `CORS_ORIGINS` (wildcards are rejected at startup); `GET` only;
  no credentials.
- **Error envelope** (all 4xx/5xx except readiness):

```json
{ "error": { "code": "NOT_FOUND", "message": "Not Found", "details": {} }, "request_id": "…" }
```

| HTTP | Code |
|---|---|
| 400 | `INVALID_REQUEST` (validation issues in `details.issues[]` with `loc` and `msg`) |
| 404 | `NOT_FOUND`, `UNSUPPORTED_SYMBOL` (from M1) |
| 405 | `METHOD_NOT_ALLOWED` |
| 409 | `CONFLICT` |
| 429 | `RATE_LIMITED` (from M1/M5) |
| 500 | `INTERNAL_ERROR` (no stack traces or paths) |
| 503 | `NOT_READY`, `DATABASE_UNAVAILABLE`, `DATA_UNAVAILABLE`, `DATA_STALE`, `MODEL_UNAVAILABLE`, `CALIBRATION_UNAVAILABLE` |

`NO_SIGNAL` is a valid forecast decision state, not an HTTP error.

## Implemented endpoints (M0)

### `GET /api/v1/system/health`

Liveness only: it does not check dependencies.

```json
{ "status": "ok", "service": "cryptopulse-api", "version": "0.1.0",
  "environment": "development", "time": "2026-10-26T05:50:34.161730Z" }
```

### `GET /api/v1/system/readiness`

Returns `200` when ready and `503` when not, with the same body in both cases (ADR-008).
Messages never include hosts, credentials or paths.

```json
{
  "status": "ready",
  "checked_at": "2026-10-26T05:50:34.681410Z",
  "components": [
    { "name": "database", "state": "ok", "code": null, "message": "Database reachable." },
    { "name": "schema", "state": "ok", "code": null, "message": "Schema is at the latest revision." },
    { "name": "reference_markets", "state": "ok", "code": null, "message": "3 configured markets present." },
    { "name": "market_feed", "state": "not_configured", "code": "DATA_UNAVAILABLE", "message": "Market data collector is not running; no market data is available." },
    { "name": "model", "state": "unavailable", "code": "MODEL_UNAVAILABLE", "message": "No approved model is installed; no forecasts are published." }
  ]
}
```

`state` ∈ `ok | error | not_configured | unavailable`. Only `database`, `schema` and
`reference_markets` affect overall readiness.

## Planned endpoints

`/markets`, `/markets/{symbol}`, `/markets/{symbol}/candles` (M1); `/markets/{symbol}/indicators`
(M2); `/predictions/latest|history|{id}` (M4); `/models/metrics|versions` (M3–M5); a real-time
stream (SSE vs WebSocket decided in M1/M2). See `CLAUDE.md` §10.

## Frontend types

`apps/web/lib/schemas/*.ts` contains zod schemas that mirror the Pydantic models and validate
every response at runtime. Keep them synchronised whenever a backend schema changes.
