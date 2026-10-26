# Security

## Threat model (MVP)

A public, read-only, unauthenticated analysis site. There are no user accounts, exchange keys or
write endpoints. The main risks are:
- abuse of public endpoints (scraping, DoS);
- leaking internal details (stack traces, DSNs, paths);
- injection through query parameters;
- supply-chain risk in dependencies;
- unsafe deserialization of model artifacts;
- misleading financial content.

## Controls in M0

| Control | Implementation |
|---|---|
| No secrets in git | `.env*` ignored (except `.env.example`); artifacts, dumps and datasets ignored |
| Secret handling | `DATABASE_URL` is a `SecretStr` (never in reprs); logs redact secret-looking keys; readiness messages are sanitized |
| Network exposure | Compose binds Postgres, API and web to `127.0.0.1` only |
| CORS | Explicit origin allowlist; wildcard rejected at startup; `GET` only; no credentials |
| Error hygiene | Standard envelope; 500s return a generic message; details go to server logs only |
| Input validation | Pydantic settings validation (symbol and horizon whitelists); 400 envelope for invalid requests |
| SQL | SQLAlchemy and parameterized statements only (including migration seeds) |
| DB session limits | `statement_timeout=5s`, connect timeout, bounded pool |
| Containers | Non-root users (`app`, `node`); memory limits |
| Web headers | CSP (`default-src 'self'`, restricted `connect-src`, `frame-ancestors 'none'`), `X-Frame-Options: DENY`, `nosniff`, `Referrer-Policy`, `Permissions-Policy`; `X-Powered-By` removed |
| Request ids | Caller-supplied ids accepted only if they match a safe pattern (prevents header/log injection) |
| Browser config | `NEXT_PUBLIC_*` holds only public values |
| CI | Least-privilege `permissions: contents: read` |

## Planned

- **M1/M5:** rate limiting per IP for REST and stream connections, with a max connections per IP
  and careful handling of trusted proxies.
- **M5:** CSP nonces in place of `'unsafe-inline'`; separate read and write database roles;
  dependency scanning (Dependabot / `pip-audit` / `npm audit`) without auto-merging breaking
  updates; a production image without dev tooling.
- **M3:** load model artifacts only from the local trusted directory, after verifying checksum
  and path; never unpickle untrusted files.
- **Before public launch:** verify Binance market-data terms, redistribution rights and regional
  restrictions.

## Known local-only defaults

`local_change_me` (Postgres password) and `ci_only_password` (CI service container) are
placeholders for disposable environments. Never reuse them anywhere else.
