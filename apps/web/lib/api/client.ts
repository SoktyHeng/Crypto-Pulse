import type { z } from "zod";
import { errorEnvelopeSchema } from "@/lib/schemas/system";
import { API_BASE_URL } from "./config";

export type ApiErrorKind = "network" | "http" | "invalid_response";

/** A failed API call. `code` is the backend's machine-readable error code when available. */
export class ApiError extends Error {
  constructor(
    message: string,
    readonly kind: ApiErrorKind,
    readonly status: number | null = null,
    readonly code: string | null = null,
    readonly requestId: string | null = null,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

interface FetchOptions {
  signal?: AbortSignal;
  /** Treat these non-2xx statuses as valid payloads (e.g. readiness returns 503 + body). */
  acceptStatuses?: number[];
}

/**
 * Typed GET against the CryptoPulse API with runtime schema validation.
 * Never substitutes fallback data: every failure surfaces as an `ApiError`.
 */
export async function apiGet<T>(
  path: string,
  schema: z.ZodType<T>,
  { signal, acceptStatuses = [] }: FetchOptions = {},
): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: "application/json" },
      cache: "no-store",
      signal,
    });
  } catch (cause) {
    if (cause instanceof DOMException && cause.name === "AbortError") throw cause;
    throw new ApiError("The API could not be reached.", "network");
  }

  const body: unknown = await response.json().catch(() => null);

  if (!response.ok && !acceptStatuses.includes(response.status)) {
    const envelope = errorEnvelopeSchema.safeParse(body);
    if (envelope.success) {
      throw new ApiError(
        envelope.data.error.message,
        "http",
        response.status,
        envelope.data.error.code,
        envelope.data.request_id,
      );
    }
    throw new ApiError(`The API responded with HTTP ${response.status}.`, "http", response.status);
  }

  const parsed = schema.safeParse(body);
  if (!parsed.success) {
    throw new ApiError(
      "The API returned an unexpected response.",
      "invalid_response",
      response.status,
    );
  }
  return parsed.data;
}
