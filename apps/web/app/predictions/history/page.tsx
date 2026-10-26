import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";
import { EmptyState } from "@/components/states/states";

export const metadata: Metadata = { title: "Forecast history" };

export default function PredictionHistoryPage() {
  return (
    <>
      <PageHeader
        title="Forecast history"
        description="Every published forecast is stored unchanged and later settled against the finalized target candle."
      />
      <EmptyState
        title="No forecasts recorded"
        description="No forecasts have been published yet, so there is no history to show."
        code="MODEL_UNAVAILABLE"
      />
    </>
  );
}
