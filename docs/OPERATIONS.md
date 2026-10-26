# Operations runbook

## Start / stop

```bash
cp .env.example .env
docker compose up --build -d          # add --wait to block until healthy
docker compose ps
docker compose logs -f api            # one JSON object per line
docker compose down                   # keep data
docker compose down -v                # also delete pgdata and model_artifacts volumes
```

## Migrations

Migrations run through the one-off `migrate` service, which `api` depends on (and which must
complete successfully). Never add migrations to API or worker startup.

```bash
docker compose run --rm migrate
docker compose run --rm api alembic current
docker compose run --rm api alembic history
```

## Health

| Check | Meaning |
|---|---|
| `GET /api/v1/system/health` → 200 | API process alive |
| `GET /api/v1/system/readiness` → 200 / 503 | Database, schema and reference markets; feed and model reported informationally |
| Web `/system` | Same information, rendered for humans |

## Troubleshooting

| Symptom | Action |
|---|---|
| `migrate` exits non-zero | `docker compose logs migrate`; check `DATABASE_URL` and the Postgres health |
| Readiness `schema` error | Run `docker compose run --rm migrate` |
| Readiness `DATABASE_UNAVAILABLE` | `docker compose ps postgres`; check the credentials in `.env` match the existing volume (the password is fixed when the volume is first created) |
| Web shows "API unreachable" | Check `api` is healthy and that `NEXT_PUBLIC_API_BASE_URL` matches the host port; rebuild `web` after changing it |
| Port already in use | Change `POSTGRES_HOST_PORT` / `API_HOST_PORT` / `WEB_HOST_PORT` in `.env` (and `CORS_ORIGINS` / `NEXT_PUBLIC_API_BASE_URL` accordingly) |

## Backups (development)

```bash
docker compose exec -T postgres pg_dump -U cryptopulse -Fc cryptopulse > cryptopulse.dump   # git-ignored
docker compose exec -T postgres pg_restore -U cryptopulse -d cryptopulse --clean < cryptopulse.dump
```

Production backup policy (daily dumps, restore test, retention, artifact checksums) arrives in
M5. Backfill, retraining, promotion and rollback procedures arrive in M1, M3 and M4.
