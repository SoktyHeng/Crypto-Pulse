import { PageHeader } from "@/components/layout/page-header";
import { MarketUnavailableCard } from "@/components/market/market-unavailable-card";
import { ModelUnavailable } from "@/components/predictions/model-unavailable";
import { EmptyState } from "@/components/states/states";
import { EXCHANGE, SUPPORTED_SYMBOLS } from "@/lib/markets";

export default function DashboardPage() {
  return (
    <>
      <PageHeader
        title="Market dashboard"
        description={`${EXCHANGE.label} USDT markets only. Prices are never averaged across exchanges, and no total crypto market figures are shown because a single exchange cannot measure them.`}
      />

      <section aria-labelledby="feed-status" className="mb-6">
        <h2 id="feed-status" className="sr-only">
          Feed status
        </h2>
        <EmptyState
          title="Market data feed not running"
          description="No prices or candles have been collected yet. Live and historical data will appear here once the collector is running; nothing is shown until then."
          code="DATA_UNAVAILABLE"
        />
      </section>

      <section aria-labelledby="markets-heading" className="mb-8">
        <h2 id="markets-heading" className="mb-3 text-lg font-semibold">
          Markets
        </h2>
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {SUPPORTED_SYMBOLS.map((symbol) => (
            <MarketUnavailableCard key={symbol} symbol={symbol} />
          ))}
        </div>
      </section>

      <section aria-labelledby="forecast-heading">
        <h2 id="forecast-heading" className="mb-3 text-lg font-semibold">
          Forecast snapshot
        </h2>
        <ModelUnavailable />
      </section>
    </>
  );
}
