/**
 * Timestamp formatting. The API speaks UTC ISO-8601; conversion to browser-local time
 * happens only here, and the timezone is always shown.
 */

export type TimeDisplay = "local" | "utc";

export function formatTimestamp(iso: string, display: TimeDisplay = "local"): string {
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "Invalid time";
  return new Intl.DateTimeFormat("en-GB", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    hour12: false,
    timeZone: display === "utc" ? "UTC" : undefined,
    timeZoneName: "short",
  }).format(date);
}
