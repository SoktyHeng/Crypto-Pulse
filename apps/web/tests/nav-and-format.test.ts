import { describe, expect, it } from "vitest";
import { NAV_ITEMS, isActive } from "@/components/layout/nav-items";
import { formatTimestamp } from "@/lib/format/time";
import { PREDICTION_HORIZONS_MINUTES, formatHorizon, isSupportedSymbol } from "@/lib/markets";

describe("navigation", () => {
  it("covers every page in the inventory", () => {
    expect(NAV_ITEMS.map((i) => i.href)).toEqual([
      "/",
      "/predictions",
      "/predictions/history",
      "/backtesting",
      "/system",
      "/methodology",
      "/limitations",
    ]);
    expect(NAV_ITEMS.filter((i) => i.primary)).toHaveLength(5);
  });

  it("marks exactly one active item", () => {
    const active = (path: string) =>
      NAV_ITEMS.filter((i) => isActive(path, i.href)).map((i) => i.href);
    expect(active("/")).toEqual(["/"]);
    expect(active("/markets/BTCUSDT")).toEqual(["/"]);
    expect(active("/predictions")).toEqual(["/predictions"]);
    expect(active("/predictions/history")).toEqual(["/predictions/history"]);
    expect(active("/system")).toEqual(["/system"]);
  });
});

describe("markets", () => {
  it("whitelists only Binance Spot USDT symbols, case-sensitively", () => {
    expect(isSupportedSymbol("BTCUSDT")).toBe(true);
    expect(isSupportedSymbol("btcusdt")).toBe(false);
    expect(isSupportedSymbol("BTCUSD")).toBe(false);
  });

  it("formats public horizons without the research-gated 5m", () => {
    expect(PREDICTION_HORIZONS_MINUTES.map(formatHorizon)).toEqual(["15m", "30m", "1h", "4h"]);
  });
});

describe("formatTimestamp", () => {
  it("renders UTC explicitly with the timezone label", () => {
    expect(formatTimestamp("2026-10-26T03:45:05Z", "utc")).toBe("26 Oct 2026, 03:45:05 UTC");
  });

  it("never renders NaN for invalid input", () => {
    expect(formatTimestamp("garbage")).toBe("Invalid time");
  });
});
