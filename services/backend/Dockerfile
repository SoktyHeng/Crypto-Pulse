# syntax=docker/dockerfile:1
# Python minor version is pinned; dependencies come from the committed uv.lock.
FROM python:3.13-slim-bookworm AS base

COPY --from=ghcr.io/astral-sh/uv:0.13.5 /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

RUN groupadd --system app && useradd --system --gid app --home-dir /app app \
    && mkdir -p /app/artifacts/models && chown -R app:app /app/artifacts

# --- runtime: production dependencies only ---
FROM base AS runtime
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]

# --- dev: adds test/lint tooling so `docker compose run --rm api pytest` works ---
FROM base AS dev
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project
# Writable by `app` so test/lint tool caches work; the runtime image stays root-owned.
COPY --chown=app:app . .
RUN chown app:app /app
USER app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
