import { EmptyState } from "@/components/states/states";

/** Shown wherever a forecast would appear while no approved model exists. No numbers. */
export function ModelUnavailable({ className }: { className?: string }) {
  return (
    <EmptyState
      className={className}
      title="Model not trained"
      description="No approved forecasting model is installed, so no direction probabilities are published. Forecasts appear only after a model passes chronological validation and calibration checks."
      code="MODEL_UNAVAILABLE"
    />
  );
}
