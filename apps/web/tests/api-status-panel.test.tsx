import { screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ApiStatusPanel } from "@/components/system/api-status-panel";
import { FORBIDDEN_TEXT, renderWithQuery } from "./render";

function routeFetch(routes: Record<string, { status: number; body: unknown }>) {
  vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
    const url = String(input);
    const match = Object.entries(routes).find(([path]) => url.endsWith(path));
    if (!match) throw new TypeError("Failed to fetch");
    return new Response(JSON.stringify(match[1].body), { status: match[1].status });
  });
}

describe("ApiStatusPanel", () => {
  it("renders live health and readiness components", async () => {
    routeFetch({
      "/api/v1/system/health": {
        status: 200,
        body: {
          status: "ok",
          service: "cryptopulse-api",
          version: "0.1.0",
          environment: "development",
          time: "2026-10-26T03:45:05Z",
        },
      },
      "/api/v1/system/readiness": {
        status: 200,
        body: {
          status: "ready",
          checked_at: "2026-10-26T03:45:05Z",
          components: [
            { name: "database", state: "ok", code: null, message: "Database reachable." },
            {
              name: "model",
              state: "unavailable",
              code: "MODEL_UNAVAILABLE",
              message: "No approved model is installed.",
            },
          ],
        },
      },
    });
    const { container } = renderWithQuery(<ApiStatusPanel />);
    expect(await screen.findByTestId("api-health")).toHaveTextContent("0.1.0");
    expect(await screen.findByText("Ready")).toBeInTheDocument();
    expect(screen.getByText("Forecast model")).toBeInTheDocument();
    expect(screen.getByText("MODEL_UNAVAILABLE")).toBeInTheDocument();
    expect(container.textContent).not.toMatch(FORBIDDEN_TEXT);
  });

  it("shows a not-ready readiness response (HTTP 503) as diagnostics", async () => {
    routeFetch({
      "/api/v1/system/readiness": {
        status: 503,
        body: {
          status: "not_ready",
          checked_at: "2026-10-26T03:45:05Z",
          components: [
            {
              name: "database",
              state: "error",
              code: "DATABASE_UNAVAILABLE",
              message: "Database is unreachable.",
            },
          ],
        },
      },
    });
    renderWithQuery(<ApiStatusPanel />);
    expect(await screen.findByText("Not ready")).toBeInTheDocument();
    expect(screen.getByText("DATABASE_UNAVAILABLE")).toBeInTheDocument();
  });

  it("shows an offline state with retry when the API is unreachable", async () => {
    routeFetch({});
    renderWithQuery(<ApiStatusPanel />);
    expect(await screen.findByText("API unreachable")).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /retry/i }).length).toBeGreaterThan(0);
  });
});
