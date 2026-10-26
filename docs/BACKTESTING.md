# Backtesting methodology

> **Status:** requirements only; implemented in M3 (research) and M5 (dashboard). No backtest
> results exist.

## Rules against hindsight bias

- Strict walk-forward chronology; purge overlapping label windows; keep the final test interval
  untouched.
- Never tune on the final test period. If that happens, it becomes validation and a fresh
  untouched period is reserved.
- No future closes, future ranges, unfinalized bars, future-derived rolling indicators, revised
  data unavailable at issue time, or scalers fitted on the whole period.
- Latency assumption: inference happens after the candle closes, and the earliest hypothetical
  fill is later (for example the next candle) at an actually available price.

## Reporting

- Sample sizes, base rates, coverage/abstention; accuracy, balanced accuracy, macro-F1,
  per-class precision/recall, confusion matrix; log loss, multiclass Brier, reliability bins, ECE.
- The same periods are reported for every baseline. Results are broken down by volatility regime
  and time window, with block-bootstrap confidence intervals for overlapping observations.
- Every chart labels its period: in-sample, validation, calibration, test, or live forward
  tracking. "Live" counts only predictions stored before their outcome occurred.

## Optional trading simulation

If one is built, it must model fees, spread, slippage and missed fills, with no leverage. It shows
buy-and-hold and no-trade baselines. Classifier accuracy is never presented as profitability.
