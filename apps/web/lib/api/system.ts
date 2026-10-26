import { healthSchema, readinessSchema } from "@/lib/schemas/system";
import { apiGet } from "./client";

export function fetchHealth(signal?: AbortSignal) {
  return apiGet("/api/v1/system/health", healthSchema, { signal });
}

export function fetchReadiness(signal?: AbortSignal) {
  // 503 carries a valid diagnostic body describing which component is not ready.
  return apiGet("/api/v1/system/readiness", readinessSchema, { signal, acceptStatuses: [503] });
}
