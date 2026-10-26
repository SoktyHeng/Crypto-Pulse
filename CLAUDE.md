# CLAUDE.md — CryptoPulse AI

> **Project:** CryptoPulse AI — cryptocurrency short-horizon trend analysis and probabilistic forecasting  
> **Document version:** 1.0  
> **Product status:** New implementation; all output must be built and tested incrementally.  
> **Primary horizons:** 15m, 30m, 1h, 4h; 5m is a gated research extension.  
> **Markets:** BTCUSDT, ETHUSDT, SOLUSDT on Binance Spot only for MVP.  
> **Budget:** $0 mandatory software/API subscription; local-first Docker Compose.  
> **Main objective:** A trustworthy, auditable market-analysis product—not an automated trading bot.

## 0. INSTRUCTIONS TO CLAUDE CODE — READ FIRST

You are the lead architect, engineer, data engineer, ML engineer, QA engineer, and technical writer implementing **CryptoPulse AI**. Read this entire file and existing `docs/` before writing code. It is the project's canonical development instruction. Follow these rules strictly:

1. **Implement one milestone at a time (M0–M6).** Do not start the next milestone until all acceptance criteria for the current milestone are demonstrated, unless explicitly instructed by the user.
2. **Never fabricate prices, forecasts, accuracy, backtest returns, probabilities, user testimonials, or exchange data.** Sample/mock data must be visibly labeled and must never mix into production charts, history, or evaluation.
3. **Never represent statistical predictions as certainty or financial advice.** Show forecast timestamps, thresholds, model versions, data freshness, uncertainty, and limitations.
4. **Never place or simulate a real order through an authenticated exchange account.** Trading, custody, deposits, withdrawals, private account data, leverage management, and brokerage functionality are out of scope. Paper trading is a future feature, not MVP.
5. **Free/local-first:** No required paid APIs, hosted LLMs, cloud resources, premium chart libraries, proprietary market-data subscriptions, or required user account to browse. Use OSS and local infrastructure where practical. Investigate library license obligations before release.
6. **Backend is source of truth.** React/Next.js never computes authoritative indicators, features, probabilities, evaluation results, or prediction outcomes. It only presents API data, performs simple UI calculations, and visualizes chart series.
7. **Single market meaning:** All initial symbols represent Binance Spot USDT quote markets (e.g. `BTCUSDT`). Never silently substitute global market averages, futures, or another exchange.
8. **Time integrity:** Use UTC throughout APIs, DB, workers, models and logs. Convert to browser-local time only in UI; clearly show timezone. Models must not access future candles or future-derived features. Use only **finalized** 1m candles as features for published predictions.
9. **No silent fallback.** If provider is inaccessible, DB is empty, model untrained, calibration missing, data stale, or probabilities invalid, return explicit status with explanation (`DATA_UNAVAILABLE`, `DATA_STALE`, `MODEL_UNAVAILABLE`, `CALIBRATION_UNAVAILABLE`, `NO_SIGNAL`), not pretend data.
10. **Security:** Never commit secrets, tokens, passwords, local environment files, trained proprietary artifacts, huge datasets, or personal info. Whitelist supported symbols, rate-limit public routes and WebSocket connections, protect administrative commands.
11. **Always build tests alongside code.** Unit + integration + frontend + end-to-end + ML leakage tests (milestone-specific). Tests may run against explicitly seeded fixtures only.
12. **Keep diffs focused.** Do not refactor unrelated folders or make large tool-generated changes without a reason. Prefer coherent modules and small commits.
13. **On incomplete requirements:** Follow the defaults here. If a decision is consequential and genuinely unspecified, document it in `docs/DECISIONS.md` with options and rationale before implementing; do not silently pick a costly service.
14. **Milestone finish report:** Report changed files, commands executed, tests, test results, unresolved issues, and acceptance checklist. Stop and wait for next implementation instruction.
15. **Verify current vendor contracts** before implementing integrations: provider API formats, rate limits, regional availability, terms for data redistribution, and OSS licensing. Never infer data redistribution rights from free API access.
16. **Use predictable, repeatable builds.** Commit lockfiles. Use migrations, environment templates, explicit schemas, pinned major dependencies and reproducible training seeds.

### Definition of success

A user can load the local application, see live or clearly identified delayed prices for BTC/ETH/SOL, inspect validated historical candles and computed indicators, see the latest **genuine model-produced** direction probabilities when an approved model exists, read a non-promissory explanation, review immutable prediction history, and examine honestly evaluated past performance. Every prediction can be reproduced as closely as practical from versioned data/feature/model artifacts and is evaluated when its horizon matures.

---

## 1. PRODUCT VISION AND BOUNDARIES

### 1.1 Users

- Retail crypto traders wanting market context, not guaranteed buy/sell tips.
- Researchers wanting transparent forecast evaluation.
- Developers learning end-to-end quantitative analytics.

### 1.2 Scope — MVP

- Public, responsive web app without mandatory signup.
- Market overview for BTCUSDT, ETHUSDT, SOLUSDT.
- Real-time ticker updates and **finalized** 1-minute OHLCV stream with historical backfill.
- Candlestick price/volume charts and indicators (EMA 9/20/50/200, RSI 14, MACD 12/26/9, Bollinger 20/2, ATR 14, return and relative-volume features).
- Coin detail pages with selectable visible chart interval (1m, 5m, 15m, 1h, 4h), clearly distinguished from forecast horizon.
- Predictions for 15m, 30m, 1h, 4h, evaluated one-step forecast snapshots at predetermined issue intervals. 5m research option can be added only after backtest validation.
- Three-class UP, DOWN, SIDEWAYS classification; explicit abstention status `NO_SIGNAL`.
- Baseline models and XGBoost multiclass model with documented target threshold, chronological walk-forward validation, purged/embargoed splits, probability calibration, full metrics and independent held-out period.
- View latest prediction and model diagnostics: issue time, target time, reference close price, class probabilities, target threshold, freshness, version and top feature drivers.
- Immutable prediction archive and realized result evaluator.
- Evaluation dashboard: class distribution, macro-F1, balanced accuracy, log loss, multiclass Brier, per-class precision/recall, calibration plots, confusion matrix, coverage and performance versus baselines. Optional simple trading simulation must report fees/slippage and label assumptions.
- System-health view and JSON structured logs.
- User-facing disclosure, source/licensing/attribution and limitations pages.

### 1.3 Explicitly OUT OF SCOPE for MVP

- Exchange sign-in, API keys for private Binance account functions, order placement, margin/futures/leverage and wallet custody.
- Paid OpenAI/Anthropic/Gemini calls; all explanations should initially use transparent templates/feature contributions, not an LLM.
- Free-form price-target generation, claims of exact future prices, guaranteed profitability or directional edge.
- Personalized investment recommendations.
- Thousands of coins, multi-exchange consolidated indexes, push notifications, email marketing, multi-tenant roles, social features, sentiment scraping, complex order-book execution strategies.
- Fabricated simulated analytics presented as live.

### 1.4 Nonfunctional goals (targets, not guaranteed facts)

- Responsive at 360px, tablet 768px, desktop 1280px+; dark/light theme.
- For 3 symbols and modest local traffic, last-price updates arrive through backend WebSocket/SSE with visible last-updated time; reconnection behavior is explicit.
- Final 1m candles persist exactly once (idempotent upsert) and survive restarts.
- Predictions available shortly after an eligible candle close under healthy local conditions; record actual latency and warn when late.
- Accessibility: keyboard navigation, labeled controls, contrast, chart text summaries, and reduced-motion support.
- Clear degradation when internet/provider/model is unavailable.
- App runs on Windows/macOS/Linux developers with Docker, although Docker Desktop license terms must be checked separately for organizational use.

---

## 2. FINAL TECHNOLOGY STACK

| Area | Technology | Why |
|---|---|---|
| Web | Next.js App Router + TypeScript | React UI, static/SSR pages where useful |
| UI | Tailwind CSS + shadcn/ui + Lucide icons | Responsive accessible components |
| Chart | TradingView Lightweight Charts (OSS Apache 2.0) | Candlestick and volume visualizations |
| Data query | TanStack Query + typed fetch clients | API cache, retry and stale state |
| Backend | Python FastAPI, Pydantic v2 | Typed REST and SSE/WebSocket endpoints |
| ORM/migrations | SQLAlchemy 2 + Alembic | Database schema and reproducibility |
| Database | PostgreSQL (vanilla initially) | OHLCV, metadata, models, predictions, outcomes |
| Ingestion | Python asyncio + httpx + websockets | REST backfill and stream handling |
| Quant / ML | NumPy, pandas, scikit-learn, XGBoost | Features, baselines, model, calibration, metrics |
| Models | joblib or XGBoost native serialization with manifest | Versioned inference artifacts |
| Background tasks | Dedicated Python processes and database-aware scheduler | Predict/evaluate/backfill; no hidden magic |
| Test | pytest, pytest-asyncio, Testcontainers or ephemeral Postgres, Vitest, Playwright | Logic, integration, UI/E2E |
| Lint/format | Ruff + mypy (Python), ESLint + TypeScript strict + Prettier (web) | Quality controls |
| Runtime | Docker Compose local; optional single VPS | $0 paid dependencies locally |

**Do not add Redis or TimescaleDB without demonstrated need.** Start with indexed/partition-ready PostgreSQL and simple per-instance ephemeral UI broadcasts. Add Redis pub/sub later only if multiple API replicas need fan-out; add TimescaleDB only for scale justified by measurement. No requirement to use Supabase, Clerk, Firebase or a hosted backend.

### 2.1 Sources and current documentation to consult

- Binance official market-data-only API: https://github.com/binance/binance-spot-api-docs/blob/master/faqs/market_data_only.md
- Binance Spot WebSocket streams: https://github.com/binance/binance-spot-api-docs/blob/master/web-socket-streams.md
- Binance API REST: https://github.com/binance/binance-spot-api-docs/blob/master/rest-api.md
- Binance bulk public data: https://github.com/binance/binance-public-data
- Lightweight Charts: https://www.tradingview.com/lightweight-charts/
- Verify licensing, attribution, API quotas and usage conditions again before publication.

---

## 3. SYSTEM ARCHITECTURE

```mermaid
flowchart TB
  BinanceREST[Binance Spot Public REST] --> Collector[Collector + Historical Backfill]
  BinanceWS[Binance Spot Public WebSocket] --> Collector
  Collector --> Verify[Validate, Finalize, Deduplicate, Gap Check]
  Verify --> PG[(PostgreSQL)]
  PG --> Features[Feature Generator]
  Features --> Infer[Model Inference + Calibration + Quality Gate]
  Infer --> PG
  PG --> Evaluator[Outcome Evaluator]
  Evaluator --> PG
  PG --> API[FastAPI]
  Collector --> Broadcast[Live Broadcaster]
  Broadcast --> API
  API --> WEB[Next.js Web App]
  WEB --> Visitor[Browser]
  PG --> Offline[Offline Training / Walk-forward Backtesting]
  Offline --> Registry[Versioned Model Registry]
  Registry --> Infer
```

### 3.1 Services to implement

1. **`web`**: Next.js presentation; REST queries; subscribe to live public updates. Dynamic chart/client components load client-side when browser APIs required. Never embed direct Binance collection logic in UI.
2. **`api`**: FastAPI typed REST; centralized error schema, pagination, CORS allowlist, request logging, health checks; read-only public endpoints.
3. **`collector`**: fetches/backfills historical candles, watches live kline streams, persists only finalized candles, emits live ticker previews, manages feed disconnections.
4. **`prediction-worker`**: schedules model scoring when eligible completed candles arrive, obtains consistent feature snapshots, performs inference and calibration, enforces model/data gates, saves prediction atomically.
5. **`outcome-worker`**: finds matured unresolved predictions, obtains finalized target candle, calculates outcome using the **stored original threshold**, writes immutable outcome once.
6. **`training`**: offline CLI job triggered explicitly; not inside a web request. Supports reproducible datasets, chronology, calibration, model registration and rollback.
7. **`postgres`**: canonical structured data and persisted job cursors.

### 3.2 Data integrity invariants

- `market_id + interval + open_time` unique for every finalized candle.
- Never persist a mutable, unfinished candle as finalized.
- For market data and pricing calculations use exchange event timestamps plus candle timestamps, not server reception time as substitute.
- Unix milliseconds for Binance live/REST API; **bulk downloads may use microseconds in newer spot archives**—detect/normalize units explicitly and test.
- Store all timestamps as `TIMESTAMPTZ UTC`; record close time according to documented candle semantics.
- Prices/volumes stored as high-precision `NUMERIC` for persisted source data; convert to float only within ML features with documented precision expectations.
- Reject OHLC outliers violating invariants (`high < low`, `high < open/close`, negative volume, missing timestamps). Do not silently repair contradictory data.
- Strictly monotonic finalized candle sequence per symbol and interval; gap detection and recovery.
- Feature snapshots are calculated at `as_of_candle_close`, from data timestamped no later than `as_of`.
- Target outcome does not exist until the target timeframe has fully completed.
- Published predictions must never change. Retraining creates a new model version.

---

## 4. REPOSITORY STRUCTURE

```text
cryptopulse-ai/
  CLAUDE.md
  README.md
  .env.example
  .gitignore
  .editorconfig
  docker-compose.yml
  Makefile
  apps/
    web/
      app/
        (public)/page.tsx
        markets/[symbol]/page.tsx
        predictions/page.tsx
        predictions/history/page.tsx
        backtesting/page.tsx
        system/page.tsx
        methodology/page.tsx
        limitations/page.tsx
      components/
        layout/
        market/
        charts/
        indicators/
        predictions/
        evaluation/
        states/
      hooks/
      lib/
        api/
        format/
        schemas/
      tests/
      e2e/
      package.json
  services/
    backend/
      app/
        main.py
        api/v1/
        core/
        db/
        models/
        schemas/
        repositories/
        services/
        streams/
        ml/
          features/
          labeling/
          models/
          calibration/
          inference/
          evaluation/
          backtesting/
        workers/
          collector/
          predictions/
          outcomes/
      alembic/
      tests/
      pyproject.toml
      Dockerfile
  scripts/
    backfill.py
    train.py
    evaluate.py
    seed_demo.py
  artifacts/
    models/.gitkeep
    reports/.gitkeep
  docs/
    PRD.md
    ARCHITECTURE.md
    DATA_CONTRACTS.md
    DATABASE.md
    API.md
    ML_SPEC.md
    BACKTESTING.md
    UI_UX.md
    OPERATIONS.md
    SECURITY.md
    DECISIONS.md
    ROADMAP.md
    CHANGELOG.md
  .github/workflows/ci.yml
```

This organization is a starting blueprint, not a mandate to create empty files up front. Use meaningful feature-oriented backend modules and maintain imports/testability.

---

## 5. MARKET-DATA CONTRACT

### 5.1 Provider and endpoints

Use only Binance Spot public market-data endpoints in MVP. Current official market-data-only REST base is `https://data-api.binance.vision`, including `GET /api/v3/klines`, `GET /api/v3/exchangeInfo`, and ticker endpoints. Current market-only WS base is `wss://data-stream.binance.vision:443/ws/` and stream names use lowercase (e.g. `btcusdt@kline_1m`). Verify these against official docs at implementation time.

- No Binance trading or user account API keys.
- Use combined streams when useful for three symbols; obey current connection and stream limits.
- Detect closed candle from kline property `k.x == true`; retain previews separately only in memory/broadcast.
- Binance WebSocket connections have documented lifetime/heartbeat behavior; implement ping/pong, backoff+jitter, connection replacement, daily reconnect, and REST backfill after rejoin.
- Honor 429 and any provider-specific temporary ban feedback; implement bounded concurrency and response-header-informed quota handling.
- Handle provider network/geographic restrictions by surfacing data unavailability rather than circumventing restrictions or silently swapping data.

### 5.2 Historical import

- Implement `backfill --symbol BTCUSDT --from ISO8601 --to ISO8601 --interval 1m` and analogous commands.
- Seed at least 6 months of eligible candles if feasible. Longer history should be explicitly configurable; never assume it has been downloaded.
- Use paginated REST and optionally public exchange archives with documented timestamp-unit conversion, integrity checks and reproducible import logs.
- Backfill end is bounded, records cannot be in the future, and retries must be idempotent.
- Check expected minute count per market; distinguish gaps from periods when market/trading was unavailable.
- Track records downloaded, inserted, duplicated, rejected, still missing, and provider request failures.

### 5.3 Live updates

- Candle snapshots before `k.x=true` are provisional; use for price UI only and visually label as provisional.
- Final candles persisted in transaction and initiate feature/prediction scheduling.
- If new candle arrives and previous is missing, schedule REST gap reconciliation before dependent predictions.
- Feed status: `CONNECTED`, `RECONNECTING`, `DEGRADED`, `STALE`, `OFFLINE`.
- Model freshness thresholds: configurable (default: max 2 minutes since latest finalized 1m candle under normal operations). If past threshold, abstain.
- Track exchange event lag and processing lag in observability metrics.

### 5.4 Candle validation

At minimum: symbol whitelisted; interval supported; start/open/close timestamps valid; `open>0`, `high>=max(open,close)`, `low<=min(open,close)`, `low>0`, all volume fields >=0; number of trades >=0; no duplicate key; complete chronological continuity. Record provider raw field names in `docs/DATA_CONTRACTS.md`.

---

## 6. INDICATORS AND FEATURE ENGINEERING

Features must be deterministic and reusable identically for training and live inference.

### 6.1 Price and return features

- Log returns at 1, 3, 5, 15, 30, 60, 240 minutes.
- Rolling mean and standard deviation over 5, 15, 30, 60, 240 candles.
- Price distance from EMA 9, EMA 20, EMA 50, EMA 200.
- EMA slopes or normalized differences, not ambiguous raw units.
- High-low range normalized by close; candle body/wick proportions; volume-weighted features where validated.

### 6.2 Technical indicators

- RSI 14 (document Wilder smoothing vs alternate implementations).
- MACD (12, 26, 9), histogram and signal-line delta.
- Bollinger Bands (20, 2), width and price position.
- ATR 14 and rolling realized volatility.
- Relative volume (current finalized volume / trailing volume average excluding unintended future data), taker buy ratio if available.
- Trend/regime tag for diagnostics (not treated as truth).
- BTC contemporaneous aligned historical returns as optional feature for ETH and SOL; no future alignment.

### 6.3 Computation rules

- Create indicator unit tests using independent hand-verified vectors or reference implementation, including warm-up behavior.
- Warm-up period should be sufficient for longest indicator; at least 250 closed candles by default, otherwise `INSUFFICIENT_HISTORY`.
- Do not forward-fill missing exchange OHLCV across actual gaps to fabricate candles. Mark data invalid and abstain/skip features until continuity restored.
- Use same timezone, rounding, look-back and parameter versions in training and inference.
- Save a feature-set version identifier, feature list/hash, latest input candle timestamp, and checksum where practical.
- No future normalization: fit scalers only on training split if used; transform validation/test/live with frozen training parameters.
- Check NaN/infinity and inconsistent features; do not silently replace them with zeros.

---

## 7. PREDICTION DEFINITIONS, MODEL, AND ABSTENTION

### 7.1 Horizons and scheduling

| Horizon | Minutes | Default issue cadence | Initial status |
|---|---:|---|---|
| 5m | 5 | Every finalized 1m candle | Research-gated; not in public MVP |
| 15m | 15 | Each finalized 1m candle | MVP |
| 30m | 30 | Each finalized 5th 1m candle | MVP |
| 1h | 60 | Each finalized 5th 1m candle | MVP |
| 4h | 240 | Each finalized 15th 1m candle | MVP |

*Important:* Issue cadence and horizon are distinct; displayed outcome metrics must account for overlap and dependencies. No duplicate predictions for the same market/horizon/feature-as-of/model-version issue.

### 7.2 Label definition

For issue reference close `P_t`, future close `P_(t+h)`, define simple return `r = (P_(t+h) / P_t) - 1`. Set a **predeclared, fixed or time-adaptive trailing-only** threshold `tau(t,h) >= 0` and label:

- UP if `r > tau`.
- DOWN if `r < -tau`.
- SIDEWAYS otherwise, including equality.

For MVP choose a configurable fixed threshold per horizon recorded with each prediction, and document how it was selected **using training-only data and a declared economic/noise rationale**. Example candidate study (not hard-coded final truth): 0.10% for 15m, 0.15% for 30m, 0.20% for 1h, 0.35% for 4h. These are experiments only; tune without using final held-out test results. Market fees/spread are not automatically included by this definition.

Never change a prediction's stored threshold or label interpretation after it is issued.

### 7.3 Models

Start with benchmarks: constant/majority class, persistence or momentum heuristic, and multinomial logistic regression. Then train XGBoost multi-class classifier to output probabilities for `UP`, `DOWN`, `SIDEWAYS` (fixed canonical class order). Compare LightGBM later only if justified; deep learning is not MVP.

- Separate model per horizon is the simplest MVP default; either build per-coin per-horizon models or test shared model with symbol identifier, documenting the chosen strategy. Default per-horizon across three symbols with one-hot symbol if data is adequate; compare against per-coin performance.
- Handle class imbalance through evaluation and justified training adjustments, not deceptive upsampling across future observations.
- Use time-based partitions and walk-forward folds. Purge observations whose **label windows** overlap between training and validation/test; add embargo as required for dependence. Never use random train/test split on time series.
- Maintain train, validation (including hyperparameter selection), separate calibration, and untouched final test periods; reserve most recent period for final test.
- Probability calibration (e.g. sigmoid/isotonic with suitable data) must be trained only on separate, chronologically valid calibration records; compare raw vs calibrated log loss and Brier score before approving.
- Write model artifact and manifest: `model_id`, semantic version, git commit, horizon, assets, source, training range, calibration range, test range, threshold method, feature schema/hash, training seed, library versions, model metrics, checksum, creation timestamp.
- Registry statuses: `CANDIDATE`, `APPROVED`, `ACTIVE`, `RETIRED`, `REJECTED`. Activate only tested, schema-compatible artifacts. Ensure atomic rollback to last known good artifact.

### 7.4 Prediction output and safety

Output must include `symbol`, `exchange`, `horizon_minutes`, `issued_at`, `feature_as_of`, `target_at`, `reference_price`, `p_up`, `p_down`, `p_sideways`, `predicted_class`, `decision_status`, `threshold_pct`, `model_version`, `feature_version`, `data_status`, `quality_flags`, `top_features` (optional verified), and `latency_ms`.

- `p_up,p_down,p_sideways` must be finite, nonnegative, each <=1, and sum to 1 within documented numerical tolerance.
- Use `NO_SIGNAL` if model confidence is below predefined threshold, data stale, out-of-distribution flags triggered or model degraded. Still distinguish unavailable predictions from low-confidence predictions; do **not** publish probability values from an untrained model.
- Do not label a high-probability class as a guaranteed trading recommendation. Use 'directional forecast', not 'buy now' or 'sell now'.
- Explain drivers using verifiable feature deltas or properly computed SHAP values; no invented rationale. Templates should explicitly separate observed indicators from speculative interpretation.
- The system must still function with no installed model: chart and data work, prediction panel says 'Model not trained'.

---

## 8. OUTCOME EVALUATION AND BACKTESTING

### 8.1 Outcome settlement

An evaluator scans due predictions, verifies finalized target close exists and matches the market, calculates realized return from the prediction's original `reference_price`, applies **stored threshold and original label policy**, and records one immutable outcome. If target data missing, record `PENDING_DATA`/`UNRESOLVED`, do not guess or interpolate. Persist evaluation timestamp and outcome source candle key. No double settlement.

### 8.2 Required metrics

- Sample sizes, outcome base rates and abstention/coverage ratios by coin/horizon/model/version/date.
- Accuracy and balanced accuracy.
- Macro-F1, class precision/recall/F1 and confusion matrix.
- Multiclass log loss and Brier score; per-class reliability/calibration bins and expected calibration error (interpreted carefully).
- Performance against majority, persistence/momentum, and logistic regression baselines on same periods.
- Metrics by volatility regime and contiguous time windows.
- Block/bootstrap confidence intervals for dependent/overlapping time-series observations where feasible.
- Feature drift/performance drift as post-MVP monitoring.

### 8.3 Backtesting: rules against hindsight bias

- Walk-forward chronology; strictly preserve temporal order.
- Purge overlapping label windows and protect untouched final test interval.
- No tuning thresholds or models on final test period. If tuning occurs, demote it from test to validation and establish a fresh untouched period.
- No using future-close, future range, same-bar close before finalization, future-derived rolling indicators, revised source data unavailable at historical issue time, or all-period-fit scalers.
- Record latency assumptions: inference after closed candle; earliest hypothetical fill occurs later (e.g. next candle) and uses actual available price, not forecast's historic close.
- If offering a simulation, model exchange fees, bid/ask spread, slippage and missed fills. No leverage or real orders. Show buy-and-hold and no-trade baselines.
- Financial performance is distinct from classifier accuracy. A classifier can have >50% accuracy but lose money after fees.
- All charts must identify in-sample, validation, calibration, test and forward/live tracking periods.
- 'Live performance' only counts predictions saved before outcomes occurred, not hindsight replay.

### 8.4 Model promotion gate

Never state that the model has predictive edge simply because it trains. For promotion to `ACTIVE`, require: complete artifact/schema checks; no feature leakage tests failing; adequate held-out sample counts; reproducible evaluation; calibrated probabilities that outperform or at least reasonably compare with baselines; no materially broken class behavior; and documented limitations. If no candidate passes, retain an `UNAVAILABLE` or research-only forecast state. Quantitative thresholds should be written to `docs/ML_SPEC.md` before looking at final holdout.

---

## 9. DATABASE DESIGN

Use SQLAlchemy 2 migrations via Alembic; no schema created ad hoc in application startup. Key tables and suggested columns:

### Reference entities

- `exchanges(id PK, code UNIQUE, name, enabled, created_at)`
- `assets(id PK, symbol UNIQUE, name, created_at)`
- `markets(id PK, exchange_id FK, base_asset_id FK, quote_asset_id FK, provider_symbol, status, precision_json, UNIQUE(exchange_id, provider_symbol))`

### Market observations

- `candles(id BIGINT PK, market_id FK, interval, open_time TIMESTAMPTZ, close_time TIMESTAMPTZ, open NUMERIC(28,12), high NUMERIC(28,12), low NUMERIC(28,12), close NUMERIC(28,12), base_volume NUMERIC(38,16), quote_volume NUMERIC(38,16), trade_count BIGINT, taker_buy_base_volume NUMERIC(38,16) NULL, source_event_time TIMESTAMPTZ NULL, received_at TIMESTAMPTZ, is_final BOOLEAN, UNIQUE(market_id,interval,open_time))`
- `ingestion_cursors(id, market_id, stream, last_final_open_time, last_event_at, last_checked_at, state, error_count, metadata_json)`
- `ingestion_gaps(id, market_id, interval, from_time, to_time, status, last_attempt_at, attempt_count, details_json)`

### Prediction and model entities

- `feature_snapshots(id, market_id, feature_as_of, feature_version, values_json, feature_checksum, input_candle_open_time, UNIQUE(market_id,feature_as_of,feature_version))`
- `model_versions(id UUID PK, name, horizon_minutes, status, artifact_path, artifact_checksum, manifest_json, activated_at, created_at)`
- `predictions(id UUID PK, market_id FK, horizon_minutes, issued_at, feature_as_of, target_at, reference_price NUMERIC, threshold_pct NUMERIC, p_up DOUBLE PRECISION, p_down DOUBLE PRECISION, p_sideways DOUBLE PRECISION, predicted_class, decision_status, model_version_id FK, feature_snapshot_id FK, data_status, quality_flags_json, explanation_json, latency_ms, created_at, UNIQUE(market_id,horizon_minutes,feature_as_of,model_version_id))`
- `prediction_outcomes(id UUID PK, prediction_id UNIQUE FK, target_candle_id FK, actual_price NUMERIC, actual_return DOUBLE PRECISION, actual_class, settlement_state, evaluated_at)`
- `evaluation_runs(id UUID PK, model_version_id FK, dataset_start, dataset_end, method, metrics_json, report_path, created_at)`
- `audit_events(id BIGINT PK, actor, event_type, entity_type, entity_id, payload_json, occurred_at)`

Include CHECK constraints for probabilities, positive prices, valid time ordering, intervals, volume, enums and referential integrity; indices on `(market_id, open_time DESC)`, `(market_id, horizon_minutes, issued_at DESC)`, `target_at`, and pending outcome lookup. Enforce publication immutability through application rules and controlled permissions. Define retention policy: keep candle history and all prediction/outcome audit history in MVP; add archival only when necessary.

**Implementation detail:** `is_final` may be always true in the canonical `candles` table if provisional candles never persist; document and test that interpretation.

---

## 10. BACKEND API CONTRACT

All endpoints versioned `/api/v1`. Document with OpenAPI and provide generated or manually synchronized frontend types. JSON UTC timestamps ISO 8601 with timezone; paginated endpoints bounded and deterministic. Standard error: `{ "error": { "code": "DATA_STALE", "message": "...", "details": {} }, "request_id": "..." }`.

### Public REST

| Route | Meaning |
|---|---|
| `GET /api/v1/markets` | Supported symbols, latest known price, freshness and source |
| `GET /api/v1/markets/{symbol}` | Symbol detail and source metadata |
| `GET /api/v1/markets/{symbol}/candles?interval=1m&from=...&to=...&limit=...` | Historical finalized OHLCV, bounded queries |
| `GET /api/v1/markets/{symbol}/indicators?interval=1m&...` | Indicators aligned to candle timestamps |
| `GET /api/v1/predictions/latest?symbol=BTCUSDT&horizon_minutes=15` | Latest prediction or explicit status |
| `GET /api/v1/predictions/history?symbol=...&horizon_minutes=...&cursor=...` | Immutable forecast records incl. outcome status |
| `GET /api/v1/predictions/{prediction_id}` | Full details and provenance |
| `GET /api/v1/models/metrics?symbol=...&horizon_minutes=...` | Evaluation summary and supported period |
| `GET /api/v1/models/versions` | Approved/active model manifests minus private paths |
| `GET /api/v1/system/health` | Liveness/status; no credentials |
| `GET /api/v1/system/readiness` | DB/feed/readiness diagnostic, sanitized |

### Real-time

- `GET /api/v1/stream` via SSE or `WS /ws/v1/market` (choose one supported initial interface and document why). Suggested events: `price.preview`, `candle.closed`, `prediction.published`, `feed.status`.
- Include monotonically sortable timestamps, source, exchange, market, event version, status and resync instructions.
- Clients must refetch canonical REST after reconnect; never rely on stream for historical completeness.
- Rate-limit subscriptions, bound symbols, and prevent unbounded queues. Handle slow clients with controlled drop/resync policy.

### API behavior

- HTTP 200 for valid empty lists; 400 for invalid query; 404 unsupported symbol or prediction; 409 data consistency conflicts if relevant; 429 too many requests; 503 for unavailable upstream/resource if no cached result. Use consistent `status` and `as_of` for unavailable forecasts rather than forging empty probabilities.
- Validate `symbol` against DB-supported market whitelist and `interval`/`horizon` against allowlist.
- Do not leak internal stack traces or filesystem artifact paths.

### Example prediction payload (ILLUSTRATIVE ONLY)

```json
{
  "id": "00000000-0000-0000-0000-000000000001",
  "exchange": "BINANCE_SPOT",
  "symbol": "BTCUSDT",
  "horizon_minutes": 15,
  "issued_at": "2026-10-26T03:45:05Z",
  "feature_as_of": "2026-10-26T03:45:00Z",
  "target_at": "2026-10-26T04:00:00Z",
  "reference_price": "68450.00",
  "movement_threshold_pct": "0.10",
  "probabilities": { "up": 0.61, "down": 0.24, "sideways": 0.15 },
  "predicted_class": "UP",
  "decision_status": "ACTIVE",
  "model_version": "xgb-15m-v1",
  "feature_version": "features-v1",
  "data_status": "FRESH",
  "is_demo": true
}
```

Never serve this example as a live forecast. Mock fixture routes, if any, are disabled outside explicitly selected demo mode.

---

## 11. FRONTEND PRODUCT AND UI/UX SPECIFICATION

### 11.1 Design language

- Modern professional market terminal: restrained, readable and information-dense, not neon/gambling aesthetics.
- Dark and light modes; accessible contrast. Gains green, losses red **plus text/icon labels** so color is not the only signal.
- Desktop sidebar + top navigation; mobile bottom bar/compact nav. Responsive 360/768/1280+.
- Consistent typography, compact tables, structured skeletons, empty, offline, retry, loading and error states.
- No fake market data during API loading; use skeletons rather than fabricated values.
- Monetary rounding appropriate to asset; use formatted values without losing precision in backend.
- Display exchange source and latency/last candle time clearly on market and prediction panels.

### 11.2 Page inventory

1. `/` **Market dashboard:** top market summary; 3 symbols cards; sortable market table; status strip; quick prediction snapshot by horizons. No fake total crypto market cap (Binance-only data cannot derive all-market totals).
2. `/markets/[symbol]` **Coin analysis:** header with source/price/24h stats; historical candlestick chart and volume histogram; indicator controls and settings; horizon tabs; probability card; explanation based on real indicators; past outcomes. Forecast chart overlays must label forecast horizon and probability visualization clearly; avoid generating pseudo-precise projected price trajectories from direction probabilities alone.
3. `/predictions` **Forecast overview:** three symbols x approved horizons; confidence, status, issued/target time, predicted class, sideway threshold; allow filters.
4. `/predictions/history` **History:** date/time/horizon filters, sortable immutable forecasts, realized outcomes, pagination, pending/unavailable status and version details.
5. `/backtesting` **Evaluation:** holdout/forward periods, class confusion matrix, baselines, accuracy/calibration, reliability and coverage; warning if sample insufficient. Visually separate research backtests from live forward tracking.
6. `/system` **Transparency:** provider status, latest candle/lag, gap counts, active model versions, read-only worker status and limitations.
7. `/methodology` **How it works:** feature definitions, target labels, forecasting horizon, confidence vs calibration, metrics methodology and backtesting limitations.
8. `/limitations` **Risk and source disclosure:** not a recommendation, technical failures and data licensing/source attribution.

### 11.3 Components

`AppShell`, `MarketSwitcher`, `MarketStats`, `LivePrice`, `MarketStatusBanner`, `CandlestickChart`, `VolumeChart`, `IndicatorSelector`, `HorizonTabs`, `PredictionProbabilityBars`, `PredictionStatus`, `ForecastEvidence`, `PredictionHistoryTable`, `ModelVersionBadge`, `ConfusionMatrix`, `ReliabilityChart`, `BacktestComparison`, `FreshnessIndicator`, `LoadingState`, `EmptyState`, `ErrorState`, `OfflineState`.

### 11.4 Charting requirements

- Use Lightweight Charts only for rendering. Source OHLCV comes from backend.
- Plot finalized candles solid; current provisional candle visually distinguished if shown.
- Toggle EMA, Bollinger and separate RSI/MACD pane as supported by library and UX. Avoid plotting incompatible scales on price axis.
- Chart timezone and sampled interval clear; no implicit interpretation of candles as forecast horizons.
- Lazy-load expensive chart component; dispose subscriptions on unmount and symbol switch.
- Date/time selected in browser local, API timestamp UTC; allow visible UTC option.
- Add accessible text summaries for users who cannot consume charts.

---

## 12. EXPLANATION ENGINE (NO PAID LLM)

- Use verified, deterministic templates populated from features and model interpretation values where available.
- Split explanation into: **observed facts** (e.g. RSI=57.4), **model interpretation** (e.g. high normalized momentum contributed positively according to local SHAP), **limitations** (overlap, uncertainty, headline/liquidation risk).
- No invented causal chain; an indicator correlation is not proof of price cause.
- Never assert 'whales are buying', 'institutional inflows' or 'news-driven rally' unless actual sourced data supports it.
- Separate numeric model probabilities from textual narrative; explanations must not alter predictions.
- Cache only versioned explanation tied to prediction_id and feature snapshot.

---

## 13. LOCAL DEVELOPMENT, CONFIG AND OPERATIONS

### 13.1 Environment variables

Provide `.env.example` with non-secret placeholders/defaults:

```dotenv
APP_ENV=development
DATABASE_URL=postgresql+psycopg://cryptopulse:local_change_me@postgres:5432/cryptopulse
PUBLIC_API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000
BINANCE_REST_BASE=https://data-api.binance.vision
BINANCE_WS_BASE=wss://data-stream.binance.vision:443
SUPPORTED_SYMBOLS=BTCUSDT,ETHUSDT,SOLUSDT
PRIMARY_CANDLE_INTERVAL=1m
PREDICTION_HORIZONS_MINUTES=15,30,60,240
MAX_CANDLE_STALENESS_SECONDS=120
MODEL_ARTIFACT_DIR=/app/artifacts/models
ENABLE_DEMO_MODE=false
LOG_LEVEL=INFO
```

**Note:** `local_change_me` is an example local-only password; real environments must override it with proper secrets. `NEXT_PUBLIC_*` variables are visible to browsers and must never hold credentials. Browser API hostname may differ inside Docker vs host; document both paths.

### 13.2 Docker Compose

- Services: `postgres`, `api`, `collector`, `prediction-worker`, `outcome-worker`, `web`, optional one-off `training` profile.
- Health checks and dependency readiness gates, volume for DB and model artifacts.
- No startup demand for pretrained model; clean startup should still display UI and report `MODEL_UNAVAILABLE`.
- Startup migrations as explicit controlled command or single migration service, **not every worker auto-running migrations**.
- Limit CPU/memory where appropriate; workers exit or retry gracefully on provider failure.

### 13.3 Scripts and commands

Implement documented commands (names may be Makefile aliases):

```bash
cp .env.example .env
docker compose up --build -d
docker compose ps
docker compose logs -f api
docker compose run --rm api alembic upgrade head
docker compose run --rm api python -m app.cli.backfill --symbol BTCUSDT --days 30
docker compose run --rm api python -m app.cli.train --horizon 15
docker compose run --rm api python -m app.cli.evaluate --horizon 15
docker compose run --rm api pytest
docker compose exec web npm run lint
docker compose exec web npm run typecheck
docker compose down
```

Ensure actual commands work; adapt file/modules to finalized layout and update README rather than leaving pseudocommands.

### 13.4 Reliability and observability

- Structured JSON logs with component, request_id/job_id, symbol, event timestamp, lag, model_id, error code; exclude secrets.
- Collector reconnect attempts, backfill counts, last finalized candle, unresolved gaps, API error rates, inference latency, worker heartbeat, unresolved evaluations, disk usage.
- Health endpoints separate liveness and readiness, avoid exposing private configuration.
- Fail safely if disk full/DB unavailable or provider rate-limited; do not drop authoritative closed candles without logging/recovery.
- Model serving: load once per worker/version, check checksums and feature schema before scoring; reload only on explicit version promotion.
- Backups: daily PostgreSQL dump for production, documented restore test, artifact checksum, retention policy.
- No anonymous access to internal admin actions; initial MVP requires CLI/manual operator for training/promotion.

---

## 14. SECURITY, PRIVACY, LICENSING

- Validate and sanitize all inputs with Pydantic; query parameter bounds, symbol allowlist, cursor-based pagination and query timeout.
- Parameterized SQL; no raw interpolated SQL. Database app role least privilege. Distinct read/write roles if feasible.
- CORS restrict origins; security headers on web; appropriate CSRF protections if write endpoints eventually added.
- Rate-limit API and streaming clients (trusted proxy handling carefully); max connections per IP.
- Dependency scanning and automated package security updates; never auto-merge breaking updates.
- No secrets or `.env` committed; `.gitignore` model artifact binaries, DB dumps, downloaded archives, caches, local credentials.
- Never run arbitrary deserialization of model artifacts obtained from untrusted sources (pickle/joblib security risk); local trusted artifacts only, validated checksum/path.
- Include public **financial-risk disclosure**: informational analysis; not financial advice; outcomes uncertain; exchange/data outages; not a guarantee of profit.
- Verify Binance market data usage and redistribution rights and any regional restrictions before a publicly accessible/commercial product.
- Comply with OSS requirements for chart attribution and any bundled fonts/icons; check dependency licenses. No assumption that 'free access' means unlimited commercial rights.
- Avoid processing personal financial/account information since no user accounts in MVP.

---

## 15. TEST STRATEGY

### 15.1 Backend tests

- Pydantic API request/response, symbols, intervals, pagination and date validations.
- Binance kline payload parser: partial vs closed, decimal strings, UTC timestamps, reconnect, duplication, out-of-order, invalid OHLC, provider 429, websocket disconnect.
- Historical backfill: normal pagination, partial/empty response, idempotent rerun, gap detection, archive microsecond timestamp conversion.
- Indicator golden data vectors, warm-up, missing candle gaps, NaN/Infinity and no-lookahead property.
- Prediction gating: no model; stale data; insufficient history; mismatched feature hash; probabilities not summing to 1; no-signal threshold.
- Outcome settlement: exact horizon price, pending data, threshold boundary, immutable settlement and idempotence.
- Time split and leakage: label window purge, chronological order, scaler fit only on training, future manipulation cannot change earlier features.
- Model serialization/versioning, artifact/checksum compatibility and calibration set independence.

### 15.2 Frontend tests

- Home and symbol pages render API real/empty/offline states correctly.
- Timeframe vs forecast horizon controls never get conflated.
- Chart correctly maps UTC and ignores provisional bars for published predictions.
- Probabilities render exactly and display warning for unavailable model rather than a fake number.
- Filtering and pagination maintain URL state; correct responsive keyboard interactions.
- No `NaN`, `undefined`, fake chart data, or misleading forecast curve.

### 15.3 End-to-end tests

- Local Docker stack starts cleanly with empty DB (UI reflects no data/model).
- Seeded synthetic fixture mode shows clear 'DEMO DATA' watermark; never available by default in production.
- Historical backfill -> indicator -> model training -> inference -> saved prediction -> target candle -> immutable outcome -> dashboard evaluation.
- Stop collector, verify data freshness and prediction abstention; restart, verify reconciliation.
- Switch between BTC/ETH/SOL and horizons without leaking prior symbol's results.

### 15.4 Quality gates before milestone done

- Python: Ruff, type-check for changed modules, pytest.
- Web: ESLint, `tsc --noEmit`, unit tests, production build, Playwright smoke test.
- Migration: apply from empty DB, downgrade test where safe, indexes and unique constraints verified.
- Docs: update `README.md`, API schemas, decision log and milestone checklist.
- No silent test skips; explain justified external-provider tests when offline and use reproducible fixtures in CI.

---

## 16. MILESTONE PLAN AND ACCEPTANCE CRITERIA

Each milestone is a hard stop; do not write features for the next one until user says to continue.

### M0 — Foundation, repository, docs, local environment

**Deliver:** Next.js TypeScript App Router, Tailwind/shadcn and initial app shell; FastAPI skeleton; Postgres Docker service; migration scaffold; lint/test/CI baseline; `.env.example`; run scripts; documentation; initial market enums and health endpoint.

**Acceptance:** `docker compose up --build` starts UI/API/DB from fresh clone; frontend and API health page work; schema migration works; no paid accounts; lint/typecheck/seed tests pass; README clean start instructions are accurate; no fictitious forecast displayed.

### M1 — Reliable public Binance market ingestion

**Deliver:** Exchange metadata and symbols; paginated historical 1m candle import; current spot 1m WebSocket consumer; finalized OHLCV validation; dedup/upsert; gap detection/backfill; feed status; indexed candle table; market REST API; collector tests.

**Acceptance:** Backfill at least one verified historical window, preserve unique timestamps, survive restart/reconnect, recover known gap, reject invalid candles, close candles only, expose up-to-date and stale feed status. Can simulate provider outage deterministically.

### M2 — Professional market UI and indicators

**Deliver:** Responsive dashboard, coin detail, markets table, market selector, source status, financial charts and volume; backend EMA/RSI/MACD/Bollinger/ATR; interval resampling of finalized 1m candles; indicator endpoints; mobile states; public risk banner.

**Acceptance:** Prices/candles originate from real backend DB/stream (or explicitly demo fixture mode); all indicators match tests; no inconsistent chart interval conversion; no misleading forecast yet; dark/light mobile/desktop checked.

### M3 — Quantitative research and training pipeline

**Deliver:** Versioned features, target label generation and threshold study; baselines; XGBoost; chronological/purged walk-forward validation; segregated calibration and holdout; metrics and model manifest; CLI train/evaluate; model registry and approval gate.

**Acceptance:** Reproducible training run with saved seed/artifact/report; leakage tests pass; artifact schema and checksum validated; baselines reported alongside model; no profitable/accurate claim without evidence; model not activated if research gate fails.

### M4 — Inference, forecast history, explanations, and evaluator

**Deliver:** Scoring on finalized candles at scheduled cadence; calibrated probabilities; staleness/quality abstention; immutable predictions; outcome worker; rest latest/history/detail; frontend probability and explanation panels; version-aware timeline.

**Acceptance:** Prediction is produced only with active approved model; each forecast has exact timestamps and provenance; probability sum valid; no duplicate issue; outcome settled once only after full target candle; bad feed correctly yields no-signal/data-unavailable state; history accurate.

### M5 — Backtesting dashboard and operating readiness

**Deliver:** Metrics API, charts including reliability and confusion matrix, performance by horizon/symbol, chronological simulation framework with transaction costs (if chosen), CI, security hardening, tracing/logging, backup/restore instructions, production Docker guide, source/terms disclosure.

**Acceptance:** Walk-forward and holdout are clearly separated from live performance; user can inspect why a model is active/rejected; API responds securely to invalid input; operator can rebuild stack/restore backup; performance tests and E2E flows pass.

### M6 — Optional research extension (NOT required for initial MVP)

Explore 5-minute predictions, book ticker/order-book features, transaction-fee-aware calibration, user-defined alerts/watchlists and paper trading **only after** measured forward performance supports further investment. Never add external-account trading automatically.

---

## 17. CODING CONVENTIONS

### Python

- Python current supported stable version selected in M0 and pinned by minor in Docker image. `pyproject.toml` for dependency management; lock dependencies.
- Full type annotations on public functions; Python `Decimal` for DB source price boundaries and explicit `float` conversions for ML.
- Structured classes/modules; async I/O separated from CPU-heavy training; no long-running training inside FastAPI request handler.
- Pydantic domain schemas at API boundary, SQLAlchemy models for persistence, service/repository separation only where it reduces coupling.
- Decimal/timestamp parsing tests; no unhandled timezone-naive datetimes.
- Use exceptions with stable machine-readable error codes; log stack details server-side.

### TypeScript / Next.js

- Strict TypeScript; no `any` unless documented and contained.
- Prefer Server Components for static content and Client Components for charts/live interactive widgets.
- Typed API client, schema validation for external JSON where practical, TanStack Query for REST state, one shared live subscription manager.
- Feature-based folders, small composable components and hooks; React keys stable; cancel/cleanup subscriptions on route transitions.
- Environment-specific API base URL without leaking private addresses/credentials.
- Loading/empty/error/disabled states first-class; never substitute mocked numbers in a production component.

### General

- Explicit UTC handling, immutable append-oriented research records, consistent schema naming, commit conventional changes, docs updated with behavior changes.
- All performance figures, forecasts and research conclusions trace to stored reproducible evaluation artifacts.

---

## 18. MILESTONE EXECUTION PROTOCOL

For each user instruction to build a milestone:

1. Read `CLAUDE.md`, `README.md`, and relevant `docs/` plus current implementation.
2. Summarize milestones already completed from actual code/tests, not assumptions.
3. Write a short implementation plan and identify impacted modules.
4. Implement only that milestone with tests, fixtures and migrations.
5. Run the tests/lint/build available locally. Fix failures from your changes.
6. Update `.env.example`, README, API/ML/DB docs and `CHANGELOG.md` where relevant.
7. Report: features completed, changed paths, commands run, actual test outcomes, known limitations, risk/technical debt, acceptance checklist, and the exact next milestone prompt.
8. **STOP. Do not proceed until asked.**

If network access to Binance is unavailable: create a clear provider adapter and local deterministic fixture tests; do not fabricate a successful live-connection result, and document the blocker. If long historical training is impractical locally: create demonstrable reproducible CLI and validation on fixtures, mark model `UNAVAILABLE`, and explicitly state what full real-data training remains.

---

## 19. DOCUMENTATION DELIVERABLES

Maintain these docs as work progresses:

- `docs/PRD.md`: personas, functional requirements, nonfunctional constraints, exclusions, acceptance rules.
- `docs/ARCHITECTURE.md`: services, sequence diagrams, event/data flow, deployment and failure modes.
- `docs/DATA_CONTRACTS.md`: public provider endpoints, precise candle schema, units, timestamp and data-quality handling.
- `docs/DATABASE.md`: ERD, migrations, indexes, retention and uniqueness semantics.
- `docs/API.md`: endpoint contract, examples, errors, rate limits, WebSocket/SSE events.
- `docs/ML_SPEC.md`: labels, features, splits, benchmarks, model gating, evaluation and provenance.
- `docs/BACKTESTING.md`: walk-forward methodology, trading assumptions, limitations and reporting.
- `docs/UI_UX.md`: layouts, states, accessibility, responsive patterns, examples and attribution.
- `docs/SECURITY.md`: threat model, rate limits, injection, secrets and dependency risks.
- `docs/OPERATIONS.md`: runbook, startup, data backfill, retraining, rollback, backups, incidents.
- `docs/DECISIONS.md`: ADR-style choices, especially deviations from this document.
- `docs/ROADMAP.md`: current milestone/status/acceptance matrix.
- `docs/CHANGELOG.md`: completed changes by milestone.

---

## 20. FINAL PROJECT COMPLETION CHECKLIST

The complete MVP is not done unless all checked by evidence:

- [ ] Local stack runs reproducibly with no mandatory paid API/services.
- [ ] Markets clearly bound to Binance Spot, not composite market averages.
- [ ] Historical candles imported and validated; closed candles remain immutable; reconnection fills gaps.
- [ ] UTC and timestamp-unit correctness tested, including spot archive units.
- [ ] Chart/indicator values are real, labeled, responsive and accessible.
- [ ] Training uses chronological, overlap-aware folds and separate calibration/holdout.
- [ ] Benchmarks, feature definitions and class thresholds documented before final test.
- [ ] No untrained model yields fake predictions.
- [ ] Forecasts carry probabilities, model version, reference price, thresholds, issue and target times.
- [ ] No-signal is distinct from unavailable data; stale data stops publishing forecasts.
- [ ] Every prediction is immutable and settles against finalized target candle, once.
- [ ] Backtest and live forward-tracking results are clearly separated, with honest metrics.
- [ ] Fees, spread, slippage and latency included in any optional trading simulation.
- [ ] Backend, frontend, E2E, and ML leakage/integrity tests pass.
- [ ] No exchange-account/trading code, secrets or financial guarantees.
- [ ] Current Binance terms and chart attribution/licensing verified before launch.
- [ ] Operator documentation, backups, health checks, and deployment path complete.
- [ ] All known limitations are explicitly disclosed to users.

---

## 21. READY-TO-USE CLAUDE CODE PROMPTS

**Start / M0:**

> Read `CLAUDE.md` in full. Implement M0 only: initialize CryptoPulse AI's Next.js TypeScript frontend, FastAPI backend, PostgreSQL Docker Compose environment, migration scaffold, shared configuration, docs, tests, CI and responsive application shell. Follow all free/local-first constraints. Verify all M0 acceptance criteria, report test results, and stop; do not start M1.

**M1:**

> Read `CLAUDE.md` and the existing code. Implement M1 only: Binance Spot public REST historical 1-minute candle ingestion, verified closed-candle WebSocket streaming, PostgreSQL upsert, gap detection/backfill, provider health and market-data APIs. Include reconnect/429/timestamp tests. Verify M1 acceptance criteria and stop.

**M2:**

> Read `CLAUDE.md` and the existing code. Implement M2 only: responsive market dashboard, coin analysis pages, Lightweight Charts with volume, indicator calculations (EMA, RSI, MACD, Bollinger, ATR), live price updates and robust data states. Use genuine backend data only. Test UI and indicator parity, then stop.

**M3:**

> Read `CLAUDE.md` and the existing code. Implement M3 only: leak-safe feature pipeline, time-aligned UP/DOWN/SIDEWAYS labels, baseline classifiers, XGBoost training, purged walk-forward tests, probability calibration, model manifests, metrics, and model approval gate. Reproduce reports and stop.

**M4:**

> Read `CLAUDE.md` and the existing code. Implement M4 only: approved-model inference jobs, calibrated probability publishing, NO_SIGNAL safety gates, immutable forecast history, matured-outcome settlement, REST endpoints, and UI evidence/explanation cards. Test temporal integrity and stop.

**M5:**

> Read `CLAUDE.md` and the existing code. Implement M5 only: evaluation/backtesting UI, baseline comparisons, calibration metrics, operational monitoring, security checks, backups, release documentation, and complete E2E acceptance verification. Do not claim predictive success without independent evidence. Stop with release report.

---

**Project principle:** Build the system to **measure whether predictions work**, not to display convincing but unvalidated predictions.
