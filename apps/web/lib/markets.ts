/**
 * Frontend mirror of backend enums in `services/backend/app/domain/enums.py`.
 * Keep in sync; values are part of the public API contract.
 */

export const EXCHANGE = { code: "BINANCE_SPOT", label: "Binance Spot" } as const;

export const SUPPORTED_SYMBOLS = ["BTCUSDT", "ETHUSDT", "SOLUSDT"] as const;
export type SupportedSymbol = (typeof SUPPORTED_SYMBOLS)[number];

export const MARKET_META: Record<SupportedSymbol, { base: string; quote: string; name: string }> = {
  BTCUSDT: { base: "BTC", quote: "USDT", name: "Bitcoin" },
  ETHUSDT: { base: "ETH", quote: "USDT", name: "Ethereum" },
  SOLUSDT: { base: "SOL", quote: "USDT", name: "Solana" },
};

/** Chart sampling intervals. Never conflate with forecast horizons. */
export const CANDLE_INTERVALS = ["1m", "5m", "15m", "1h", "4h"] as const;
export type CandleInterval = (typeof CANDLE_INTERVALS)[number];

/** Public MVP forecast horizons in minutes. 5m is research-gated and excluded. */
export const PREDICTION_HORIZONS_MINUTES = [15, 30, 60, 240] as const;
export type HorizonMinutes = (typeof PREDICTION_HORIZONS_MINUTES)[number];

export const PREDICTED_CLASSES = ["UP", "DOWN", "SIDEWAYS"] as const;

export function isSupportedSymbol(value: string): value is SupportedSymbol {
  return (SUPPORTED_SYMBOLS as readonly string[]).includes(value);
}

export function formatHorizon(minutes: HorizonMinutes): string {
  return minutes % 60 === 0 ? `${minutes / 60}h` : `${minutes}m`;
}
