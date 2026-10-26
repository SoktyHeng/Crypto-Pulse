import { expect, test } from "@playwright/test";

const PAGES = [
  { path: "/", heading: "Market dashboard" },
  { path: "/markets/BTCUSDT", heading: "BTC/USDT" },
  { path: "/predictions", heading: "Forecasts" },
  { path: "/predictions/history", heading: "Forecast history" },
  { path: "/backtesting", heading: "Evaluation" },
  { path: "/system", heading: "System status" },
  { path: "/methodology", heading: "How CryptoPulse AI works" },
  { path: "/limitations", heading: "Risks, limitations and sources" },
];

for (const { path, heading } of PAGES) {
  test(`${path} renders without fabricated values`, async ({ page }) => {
    const errors: string[] = [];
    page.on("pageerror", (err) => errors.push(err.message));
    await page.goto(path);
    await expect(page.getByRole("heading", { level: 1, name: heading })).toBeVisible();
    const text = await page.locator("main").innerText();
    expect(text).not.toMatch(/\bNaN\b|\bundefined\b/);
    expect(text).not.toMatch(/\d+(\.\d+)?\s*%/); // no probability numbers without a model
    // No horizontal overflow at any tested viewport (including 360px).
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    expect(overflow).toBeLessThanOrEqual(0);
    expect(errors).toEqual([]);
  });
}

test("unsupported market is a 404, not a substitute", async ({ page }) => {
  const response = await page.goto("/markets/DOGEUSDT");
  expect(response?.status()).toBe(404);
  await expect(page.getByText("Page or market not found")).toBeVisible();
});

test("system page reports API status or an explicit offline state", async ({ page }) => {
  await page.goto("/system");
  const live = page.getByTestId("api-health");
  const offline = page.getByText("API unreachable");
  await expect(live.or(offline)).toBeVisible({ timeout: 15_000 });
});

test("navigation is keyboard reachable and theme toggles", async ({ page, isMobile }) => {
  await page.goto("/");
  await page.keyboard.press("Tab");
  await expect(page.getByRole("link", { name: "Skip to content" })).toBeFocused();
  const nav = page.getByRole("navigation", { name: isMobile ? "Main mobile" : "Main" });
  await nav.getByRole("link", { name: isMobile ? "System" : "System status" }).click();
  await expect(page).toHaveURL(/\/system$/);
  const html = page.locator("html");
  const before = await html.getAttribute("class");
  await page.getByRole("button", { name: /switch to (dark|light) theme/i }).click();
  await expect(html).not.toHaveAttribute("class", before ?? "");
});
