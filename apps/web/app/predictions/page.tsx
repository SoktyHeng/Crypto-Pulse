import type { Metadata } from "next";
import { PageHeader } from "@/components/layout/page-header";
import { ModelUnavailable } from "@/components/predictions/model-unavailable";
import { PREDICTION_HORIZONS_MINUTES, SUPPORTED_SYMBOLS, formatHorizon } from "@/lib/markets";

export const metadata: Metadata = { title: "Forecasts" };

export default function PredictionsPage() {
  return (
    <>
      <PageHeader
        title="Forecasts"
        description={`Direction forecasts (UP, DOWN, SIDEWAYS) for ${SUPPORTED_SYMBOLS.join(", ")} at ${PREDICTION_HORIZONS_MINUTES.map(formatHorizon).join(", ")} horizons. Each forecast is a probability, not a recommendation.`}
      />
      <ModelUnavailable />
    </>
  );
}
