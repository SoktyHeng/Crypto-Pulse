/**
 * Browser-facing API base URL. `NEXT_PUBLIC_*` values are inlined at build time and are
 * public: never put credentials here.
 */
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");
