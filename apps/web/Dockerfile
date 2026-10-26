# syntax=docker/dockerfile:1
# Local image: production build served by `next start`, with sources and dev tooling kept so
# `docker compose exec web npm run lint|typecheck|test` works. A slim standalone production
# image is planned for M5 (docs/DECISIONS.md ADR-007).
FROM node:24.11-bookworm-slim AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

FROM node:24.11-bookworm-slim AS app
WORKDIR /app
RUN chown node:node /app
ENV NEXT_TELEMETRY_DISABLED=1
# Browser-facing API URL, inlined into client bundles at build time (public value only).
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=${NEXT_PUBLIC_API_BASE_URL}
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
COPY --chown=node:node . .
USER node
RUN npm run build
# NODE_ENV is deliberately not set: `next start` always serves the production build, and
# leaving it unset lets `docker compose exec web npm test` run React in test mode.
ENV PORT=3000 HOSTNAME=0.0.0.0
EXPOSE 3000
CMD ["npm", "run", "start"]
