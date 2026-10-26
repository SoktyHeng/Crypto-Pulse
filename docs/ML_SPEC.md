# ML specification

> **Status:** draft requirements only. No features, labels or models exist yet (M3). Quantitative
> promotion thresholds **must be written here before anyone looks at the final held-out period**.

## Task

Three-class direction classification for each `(symbol, horizon)` with horizons 15, 30, 60 and 240
minutes. The canonical class order is `UP, DOWN, SIDEWAYS`.

## Labels

For issue reference close `P_t` and future close `P_(t+h)`: `r = P_(t+h) / P_t − 1`.
`UP` if `r > τ`, `DOWN` if `r < −τ`, otherwise `SIDEWAYS` (including equality). `τ` is a fixed,
per-horizon threshold chosen on training data only, with a documented noise/economic rationale.
It is stored with every prediction and never changed after issue. Candidate study values (not
decisions): 0.10% / 0.15% / 0.20% / 0.35%.

## Features (planned)

Log returns, rolling mean and standard deviation, EMA distances and slopes, RSI 14 (Wilder),
MACD 12/26/9, Bollinger 20/2, ATR 14, relative volume and candle shape. Only finalized 1m candles
are used, with ≥250 candles of warm-up, a versioned feature set and a checksum. There is no
forward-fill across gaps and no future normalisation.

## Models

Baselines: majority class, persistence/momentum, multinomial logistic regression. Main model:
XGBoost multiclass. One model per horizon (symbol one-hot) by default, compared against
per-symbol models.

## Validation

Chronological walk-forward folds; purge observations whose label windows overlap; embargo;
separate train / validation / calibration / final-test periods (most recent = test); never a
random split.

## Promotion gate (thresholds TBD in M3, before holdout)

Artifact and schema checks pass; leakage tests pass; held-out sample counts are adequate;
evaluation is reproducible; calibrated log loss and Brier score are at least comparable to the
baselines; no broken class behaviour; limitations are documented.

## Provenance

The manifest records: `model_id`, version, git commit, horizon, assets, training, calibration and
test ranges, threshold method, feature schema and hash, seed, library versions, metrics,
checksum, created_at.
