import { z } from "zod";

/** Mirrors `app/schemas/system.py`. External JSON is validated before use. */

export const errorEnvelopeSchema = z.object({
  error: z.object({
    code: z.string(),
    message: z.string(),
    details: z.record(z.string(), z.unknown()),
  }),
  request_id: z.string().nullable(),
});
export type ErrorEnvelope = z.infer<typeof errorEnvelopeSchema>;

export const healthSchema = z.object({
  status: z.literal("ok"),
  service: z.literal("cryptopulse-api"),
  version: z.string(),
  environment: z.string(),
  time: z.iso.datetime({ offset: true }),
});
export type Health = z.infer<typeof healthSchema>;

export const componentStatusSchema = z.object({
  name: z.string(),
  state: z.enum(["ok", "error", "not_configured", "unavailable"]),
  code: z.string().nullable().optional(),
  message: z.string(),
});
export type ComponentStatus = z.infer<typeof componentStatusSchema>;

export const readinessSchema = z.object({
  status: z.enum(["ready", "not_ready"]),
  checked_at: z.iso.datetime({ offset: true }),
  components: z.array(componentStatusSchema),
});
export type Readiness = z.infer<typeof readinessSchema>;
