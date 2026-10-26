import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/states";

export const metadata: Metadata = { title: "Evaluation" };

export default function BacktestingPage() {
  return (
    <>
      <PageHeader
        title="Evaluation"
        description="Research backtests (walk-forward and held-out periods) and live forward tracking are always reported separately."
      />
      <div className="grid gap-4 lg:grid-cols-2">
        <EmptyState
          title="No research evaluation"
          description="No model has been trained or evaluated, so there are no backtest metrics."
          code="MODEL_UNAVAILABLE"
        />
        <EmptyState
          title="No live forward tracking"
          description="Live performance only counts forecasts saved before their outcome occurred. None exist yet."
          code="MODEL_UNAVAILABLE"
        />
      </div>
    </>
  );
}
