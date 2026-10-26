import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DashboardPage from "@/app/(public)/page";
import MarketPage, { generateStaticParams } from "@/app/markets/[symbol]/page";
import PredictionsPage from "@/app/predictions/page";
import { FORBIDDEN_TEXT } from "./render";

vi.mock("next/navigation", () => ({
  notFound: () => {
    throw new Error("NEXT_NOT_FOUND");
  },
}));

// Any digit followed by a percent sign or a price-like decimal would indicate a fabricated value.
const NUMERIC_VALUE = /\d+(\.\d+)?\s*%|\$\s*\d|\d{1,3}(,\d{3})+(\.\d+)?/;

describe("dashboard", () => {
  it("shows every supported market without inventing prices", () => {
    const { container } = render(<DashboardPage />);
    for (const symbol of ["BTCUSDT", "ETHUSDT", "SOLUSDT"]) {
      expect(screen.getByTestId(`market-card-${symbol}`)).toBeInTheDocument();
    }
    expect(screen.getAllByText("DATA_UNAVAILABLE").length).toBeGreaterThan(0);
    expect(container.textContent).not.toMatch(NUMERIC_VALUE);
    expect(container.textContent).not.toMatch(FORBIDDEN_TEXT);
  });

  it("does not claim total crypto market figures", () => {
    const { container } = render(<DashboardPage />);
    expect(container.textContent).not.toMatch(/market cap/i);
  });
});

describe("forecast surfaces", () => {
  it("say the model is unavailable instead of showing probabilities", () => {
    const { container } = render(<PredictionsPage />);
    expect(screen.getByText("Model not trained")).toBeInTheDocument();
    expect(screen.getByText("MODEL_UNAVAILABLE")).toBeInTheDocument();
    expect(container.textContent).not.toMatch(NUMERIC_VALUE);
    expect(container.textContent).not.toMatch(/\b(buy|sell) now\b/i);
  });
});

describe("market detail", () => {
  it("is generated only for whitelisted symbols", () => {
    expect(generateStaticParams()).toEqual([
      { symbol: "BTCUSDT" },
      { symbol: "ETHUSDT" },
      { symbol: "SOLUSDT" },
    ]);
  });

  it("keeps chart interval and forecast horizon separate", async () => {
    render(await MarketPage({ params: Promise.resolve({ symbol: "ETHUSDT" }) }));
    expect(screen.getByRole("heading", { name: "ETH/USDT" })).toBeInTheDocument();
    expect(
      screen.getByText(/1m, 5m, 15m, 1h, 4h\). It is not a forecast horizon/),
    ).toBeInTheDocument();
    expect(screen.getByText(/Horizons: 15m, 30m, 1h, 4h ahead/)).toBeInTheDocument();
    expect(screen.getByText("Model not trained")).toBeInTheDocument();
  });

  it("rejects unsupported symbols instead of substituting another market", async () => {
    await expect(MarketPage({ params: Promise.resolve({ symbol: "DOGEUSDT" }) })).rejects.toThrow(
      "NEXT_NOT_FOUND",
    );
  });
});
