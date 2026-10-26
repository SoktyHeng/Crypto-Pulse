import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";

export const metadata: Metadata = { title: "Risks & limitations" };

export default function LimitationsPage() {
  return (
    <>
      <PageHeader title="Risks, limitations and sources" />
      <article className="max-w-3xl space-y-6 text-sm leading-relaxed">
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Not financial advice</h2>
          <p>
            CryptoPulse AI provides informational, statistical analysis only. It does not recommend
            buying or selling any asset, does not place orders, and does not guarantee any outcome
            or profit. Cryptocurrency markets are volatile and you can lose money.
          </p>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Forecast limitations</h2>
          <ul className="list-disc space-y-1 pl-5">
            <li>
              Forecasts are probabilities with real uncertainty; high probability is not certainty.
            </li>
            <li>Past evaluation results do not guarantee future performance.</li>
            <li>Sudden news, liquidations or exchange events are not visible to the model.</li>
            <li>When data is stale or unavailable, forecasts are withheld rather than guessed.</li>
          </ul>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Technical failures</h2>
          <p>
            Exchange outages, network problems or regional restrictions can interrupt data. The app
            shows these states explicitly and never substitutes data from another source.
          </p>
        </section>
        <section className="space-y-2">
          <h2 className="text-base font-semibold">Data sources and attribution</h2>
          <p>
            Market data: Binance Spot public market-data endpoints. Usage and redistribution terms
            must be verified before any public or commercial deployment. Icons: Lucide (ISC
            license).
          </p>
        </section>
      </article>
    </>
  );
}
