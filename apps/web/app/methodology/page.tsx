import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";

export const metadata: Metadata = { title: "Methodology" };

export default function MethodologyPage() {
  return (
    <>
      <PageHeader
        title="How CryptoPulse AI works"
        description="Design rules for the analysis pipeline. Detailed model metrics will be published here only after an evaluated model exists."
      />
      <article className="max-w-3xl space-y-6 text-sm leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Data source</h2>
          <p>
            Prices and candles come only from Binance Spot public market data for BTCUSDT, ETHUSDT
            and SOLUSDT. Only finalized 1-minute candles are stored and used for analysis. Times are
            stored in UTC and shown in your local timezone.
          </p>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Forecast labels</h2>
          <p>
            For a forecast horizon <em>h</em>, the realized return is{" "}
            <code className="font-mono">r = close(t+h) / close(t) − 1</code>. The outcome is UP when
            r is above a fixed threshold, DOWN when below the negative threshold, and SIDEWAYS
            otherwise. The threshold is recorded with every forecast and never changed afterwards.
          </p>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Chart interval vs forecast horizon</h2>
          <p>
            The chart interval (1m, 5m, 15m, 1h, 4h) controls how candles are drawn. The forecast
            horizon (15m, 30m, 1h, 4h) is how far ahead a forecast looks. They are independent.
          </p>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Validation</h2>
          <p>
            Models are validated chronologically with walk-forward splits, purged overlapping label
            windows, a separate calibration period and an untouched final test period. A model is
            only published if it passes documented gates and compares reasonably with simple
            baselines.
          </p>
        </section>
      </article>
    </>
  );
}
