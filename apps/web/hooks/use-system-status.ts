"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchHealth, fetchReadiness } from "@/lib/api/system";

export function useSystemHealth() {
  return useQuery({
    queryKey: ["system", "health"],
    queryFn: ({ signal }) => fetchHealth(signal),
    refetchInterval: 30_000,
  });
}

export function useSystemReadiness() {
  return useQuery({
    queryKey: ["system", "readiness"],
    queryFn: ({ signal }) => fetchReadiness(signal),
    refetchInterval: 30_000,
  });
}
