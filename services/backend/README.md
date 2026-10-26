# CryptoPulse AI — backend

FastAPI API, Alembic migrations and (from M1 on) the collector, prediction and outcome workers.
See the repository root `README.md` for how to run the stack and `docs/` for contracts.

```bash
uv sync                      # install runtime + dev dependencies from uv.lock
uv run uvicorn app.main:app --reload
uv run alembic upgrade head  # needs DATABASE_URL
uv run pytest                # integration tests need TEST_DATABASE_URL
uv run ruff check . && uv run ruff format --check . && uv run mypy
```
