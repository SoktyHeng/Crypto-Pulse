import { describe, expect, it, vi } from "vitest";
import { ApiError, apiGet } from "@/lib/api/client";
import { fetchReadiness } from "@/lib/api/system";
import { healthSchema } from "@/lib/schemas/system";

function mockFetch(status: number, body: unknown) {
  return vi.spyOn(globalThis, "fetch").mockResolvedValue(
    new Response(JSON.stringify(body), {
      status,
      headers: { "Content-Type": "application/json" },
    }),
  );
}

const validHealth = {
  status: "ok",
  service: "cryptopulse-api",
  version: "0.1.0",
  environment: "test",
  time: "2026-10-26T03:45:05+00:00",
};

describe("apiGet", () => {
  it("returns schema-validated data", async () => {
    mockFetch(200, validHealth);
    await expect(apiGet("/api/v1/system/health", healthSchema)).resolves.toEqual(validHealth);
  });

  it("surfaces backend error envelopes with code and request id", async () => {
    mockFetch(404, {
      error: { code: "NOT_FOUND", message: "Not Found", details: {} },
      request_id: "abc",
    });
    const error = await apiGet("/x", healthSchema).catch((e: unknown) => e);
    expect(error).toBeInstanceOf(ApiError);
    expect(error).toMatchObject({ kind: "http", status: 404, code: "NOT_FOUND", requestId: "abc" });
  });

  it("rejects malformed payloads instead of passing them through", async () => {
    mockFetch(200, { ...validHealth, time: "not a time" });
    await expect(apiGet("/x", healthSchema)).rejects.toMatchObject({ kind: "invalid_response" });
  });

  it("reports network failures as offline errors", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new TypeError("Failed to fetch"));
    await expect(apiGet("/x", healthSchema)).rejects.toMatchObject({ kind: "network" });
  });

  it("accepts readiness 503 bodies as diagnostics", async () => {
    mockFetch(503, {
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
    });
    await expect(fetchReadiness()).resolves.toMatchObject({ status: "not_ready" });
  });
});
