# Convenience aliases. Every target is a plain command documented in README.md, so `make`
# is optional (it is not installed by default on Windows).

.PHONY: env up down ps logs migrate test-api lint-api web-check e2e reset

env:
	test -f .env || cp .env.example .env

up: env
	docker compose up --build -d --wait

down:
	docker compose down

ps:
	docker compose ps

logs:
	docker compose logs -f api

migrate:
	docker compose run --rm migrate

test-api:
	docker compose run --rm api pytest

lint-api:
	docker compose run --rm --no-deps api sh -c "ruff check . && ruff format --check . && mypy"

web-check:
	docker compose exec web npm run lint
	docker compose exec web npm run typecheck
	docker compose exec web npm test

e2e:
	cd apps/web && E2E_BASE_URL=http://localhost:3000 npx playwright test

# Destroys the local database volume.
reset:
	docker compose down -v
