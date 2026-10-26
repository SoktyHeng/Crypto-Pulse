import Link from "next/link";
import { ArrowRight } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { EXCHANGE, MARKET_META, type SupportedSymbol } from "@/lib/markets";

/**
 * Market card before ingestion exists. Shows identity and source only — never a price.
 */
export function MarketUnavailableCard({ symbol }: { symbol: SupportedSymbol }) {
  const meta = MARKET_META[symbol];
  return (
    <Card data-testid={`market-card-${symbol}`}>
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <div>
            <CardTitle>
              {meta.base}/{meta.quote}
            </CardTitle>
            <CardDescription>
              {meta.name} · {EXCHANGE.label}
            </CardDescription>
          </div>
          <Badge variant="warning">No data</Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-3 text-sm">
        <p className="text-muted-foreground">
          Price unavailable: market data has not been collected yet.
        </p>
        <code className="rounded bg-muted px-1.5 py-0.5 font-mono text-xs">DATA_UNAVAILABLE</code>
        <div>
          <Link
            href={`/markets/${symbol}`}
            className="inline-flex items-center gap-1 text-sm font-medium text-primary underline-offset-4 hover:underline"
          >
            View {symbol} analysis <ArrowRight className="size-3.5" aria-hidden="true" />
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
