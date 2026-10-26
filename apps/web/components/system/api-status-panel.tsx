"use client";

import { CheckCircle2, CircleDashed, XCircle } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ErrorState, LoadingState, OfflineState } from "@/components/states/states";
import { useSystemHealth, useSystemReadiness } from "@/hooks/use-system-status";
import { ApiError } from "@/lib/api/client";
import { API_BASE_URL } from "@/lib/api/config";
import { formatTimestamp } from "@/lib/format/time";
import type { ComponentStatus } from "@/lib/schemas/system";

const COMPONENT_LABELS: Record<string, string> = {
  database: "Database",
  schema: "Database schema",
  reference_markets: "Market whitelist",
  market_feed: "Market data feed",
  model: "Forecast model",
};

function StateBadge({ state }: { state: ComponentStatus["state"] }) {
  switch (state) {
    case "ok":
      return (
        <Badge variant="success">
          <CheckCircle2 aria-hidden="true" /> OK
        </Badge>
      );
    case "error":
      return (
        <Badge variant="danger">
          <XCircle aria-hidden="true" /> Error
        </Badge>
      );
    case "not_configured":
      return (
        <Badge variant="warning">
          <CircleDashed aria-hidden="true" /> Not running
        </Badge>
      );
    case "unavailable":
      return (
        <Badge variant="warning">
          <CircleDashed aria-hidden="true" /> Unavailable
        </Badge>
      );
  }
}

function describeFailure(error: Error) {
  if (error instanceof ApiError && error.kind === "network") {
    return {
      offline: true,
      description: `The API at ${API_BASE_URL} could not be reached. Check that the api service is running.`,
    };
  }
  return { offline: false, description: error.message };
}

export function ApiStatusPanel() {
  const health = useSystemHealth();
  const readiness = useSystemReadiness();

  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>API liveness</CardTitle>
          <CardDescription>GET /api/v1/system/health</CardDescription>
        </CardHeader>
        <CardContent>
          {health.isPending ? (
            <LoadingState label="Checking API liveness" rows={2} />
          ) : health.isError ? (
            (() => {
              const failure = describeFailure(health.error);
              const Component = failure.offline ? OfflineState : ErrorState;
              return (
                <Component
                  title="API unreachable"
                  description={failure.description}
                  onRetry={() => void health.refetch()}
                />
              );
            })()
          ) : (
            <dl
              className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-2 text-sm"
              data-testid="api-health"
            >
              <dt className="text-muted-foreground">Status</dt>
              <dd>
                <Badge variant="success">
                  <CheckCircle2 aria-hidden="true" /> Live
                </Badge>
              </dd>
              <dt className="text-muted-foreground">Version</dt>
              <dd className="font-mono">{health.data.version}</dd>
              <dt className="text-muted-foreground">Environment</dt>
              <dd>{health.data.environment}</dd>
              <dt className="text-muted-foreground">Server time</dt>
              <dd>
                {formatTimestamp(health.data.time)}{" "}
                <span className="text-muted-foreground">
                  ({formatTimestamp(health.data.time, "utc")})
                </span>
              </dd>
            </dl>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Readiness</CardTitle>
          <CardDescription>GET /api/v1/system/readiness</CardDescription>
        </CardHeader>
        <CardContent>
          {readiness.isPending ? (
            <LoadingState label="Checking readiness" rows={4} />
          ) : readiness.isError ? (
            (() => {
              const failure = describeFailure(readiness.error);
              const Component = failure.offline ? OfflineState : ErrorState;
              return (
                <Component
                  title="Readiness unknown"
                  description={failure.description}
                  onRetry={() => void readiness.refetch()}
                />
              );
            })()
          ) : (
            <div className="space-y-3" data-testid="api-readiness">
              <p className="text-sm">
                Overall:{" "}
                {readiness.data.status === "ready" ? (
                  <Badge variant="success">Ready</Badge>
                ) : (
                  <Badge variant="danger">Not ready</Badge>
                )}
              </p>
              <ul className="divide-y rounded-md border text-sm">
                {readiness.data.components.map((component) => (
                  <li key={component.name} className="flex flex-col gap-1 p-3">
                    <div className="flex items-center justify-between gap-2">
                      <span className="font-medium">
                        {COMPONENT_LABELS[component.name] ?? component.name}
                      </span>
                      <StateBadge state={component.state} />
                    </div>
                    <p className="text-muted-foreground">{component.message}</p>
                    {component.code ? (
                      <code className="w-fit rounded bg-muted px-1.5 py-0.5 font-mono text-xs">
                        {component.code}
                      </code>
                    ) : null}
                  </li>
                ))}
              </ul>
              <p className="text-xs text-muted-foreground">
                Checked {formatTimestamp(readiness.data.checked_at)}
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
