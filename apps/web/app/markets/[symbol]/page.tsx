import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PageHeader } from "@/components/layout/page-header";
import { ModelUnavailable } from "@/components/predictions/model-unavailable";
import { EmptyState } from "@/components/states/states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  CANDLE_INTERVALS,
  EXCHANGE,
  MARKET_META,
  PREDICTION_HORIZONS_MINUTES,
  SUPPORTED_SYMBOLS,
  formatHorizon,
  isSupportedSymbol,
} from "@/lib/markets";

// Only whitelisted markets exist; anything else is a 404, never a substituted market.
export const dynamicParams = false;

export function generateStaticParams() {
  return SUPPORTED_SYMBOLS.map((symbol) => ({ symbol }));
}

type Props = { params: Promise<{ symbol: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { symbol } = await params;
  return { title: isSupportedSymbol(symbol) ? `${symbol} analysis` : "Market not supported" };
}

export default async function MarketPage({ params }: Props) {
  const { symbol } = await params;
  if (!isSupportedSymbol(symbol)) notFound();
  const meta = MARKET_META[symbol];

  return (
    <>
      <PageHeader
        title={`${meta.base}/${meta.quote}`}
        description={`${meta.name} · ${symbol} on ${EXCHANGE.label}. All data comes from this single exchange market.`}
      >
        <Badge variant="outline">{EXCHANGE.label}</Badge>
      </PageHeader>

      <div className="grid gap-4 xl:grid-cols-[1fr_22rem]">
        <Card>
          <CardHeader>
            <CardTitle>Price chart</CardTitle>
            <CardDescription>
              Chart interval controls how candles are sampled ({CANDLE_INTERVALS.join(", ")}). It is
              not a forecast horizon.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <EmptyState
              title="No candles available"
              description="Historical and live candles have not been collected for this market yet. The chart stays empty rather than showing sample data."
              code="DATA_UNAVAILABLE"
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Direction forecast</CardTitle>
            <CardDescription>
              Horizons: {PREDICTION_HORIZONS_MINUTES.map(formatHorizon).join(", ")} ahead. Separate
              from the chart interval.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <ModelUnavailable />
          </CardContent>
        </Card>
      </div>
    </>
  );
}
