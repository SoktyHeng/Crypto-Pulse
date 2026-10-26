# Product Requirements — CryptoPulse AI

Canonical source: `CLAUDE.md` §1. This document summarises the requirements and tracks which
milestone delivers each one.

## Purpose

A trustworthy, auditable market-analysis product for short-horizon direction forecasts on Binance
Spot `BTCUSDT`, `ETHUSDT` and `SOLUSDT`. It is not an automated trading bot and not financial
advice.

## Personas

| Persona | Need |
|---|---|
| Retail crypto trader | Market context with honest uncertainty, not buy/sell tips |
| Researcher | Transparent forecast definitions and evaluation, including baselines |
| Developer/learner | A readable end-to-end quantitative analytics reference |

## Functional requirements (MVP)

| # | Requirement | Milestone |
|---|---|---|
| F1 | Public responsive web app; no signup | M0 shell, M2 |
| F2 | Market overview for the three whitelisted markets | M2 |
| F3 | Live ticker and finalized 1m OHLCV with historical backfill | M1 |
| F4 | Candlestick/volume charts; EMA 9/20/50/200, RSI 14, MACD 12/26/9, BB 20/2, ATR 14 | M2 |
| F5 | Chart interval (1m–4h) clearly separate from forecast horizon | M0 copy, M2 |
| F6 | UP/DOWN/SIDEWAYS forecasts for 15m/30m/1h/4h with `NO_SIGNAL` abstention | M3–M4 |
| F7 | Baselines + XGBoost; chronological purged walk-forward; calibration; held-out test | M3 |
| F8 | Forecast detail: times, reference price, probabilities, threshold, freshness, versions | M4 |
| F9 | Immutable forecast archive and outcome settlement | M4 |
| F10 | Evaluation dashboard (metrics, calibration, confusion matrix, baselines, coverage) | M5 |
| F11 | System health view and JSON logs | M0 (API health), M1+, M5 |
| F12 | Disclosure, methodology, sources and limitations pages | M0 |

## Non-functional constraints

- $0 mandatory subscriptions; local Docker Compose; no paid APIs or hosted LLMs.
- Responsive at 360 / 768 / 1280+ px; dark and light themes; keyboard navigation, reduced
  motion, text alternatives for charts.
- UTC everywhere in storage and APIs; local time only in the UI, always labelled.
- Explicit degraded states (`DATA_UNAVAILABLE`, `DATA_STALE`, `MODEL_UNAVAILABLE`,
  `CALIBRATION_UNAVAILABLE`, `NO_SIGNAL`); no silent fallback.

## Exclusions

Exchange login or private API keys, order placement, margin/futures/leverage, custody, paid LLMs,
price targets, personalised advice, multi-exchange indexes, social features, sentiment scraping
and notifications.

## Acceptance rules

Every milestone has acceptance criteria in `CLAUDE.md` §16 and evidence in `docs/ROADMAP.md`.
No performance claim is made without a stored, reproducible evaluation artifact.
