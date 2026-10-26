import { defineConfig, devices } from "@playwright/test";

// Smoke tests run against a production build. Set E2E_BASE_URL to target an already
// running stack (e.g. docker compose); otherwise Playwright starts `next start` itself.
const externalBaseUrl = process.env.E2E_BASE_URL;
const port = 3100;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? [["list"], ["html", { open: "never" }]] : "list",
  use: {
    baseURL: externalBaseUrl ?? `http://127.0.0.1:${port}`,
    trace: "retain-on-failure",
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1280, height: 800 } },
    },
    { name: "mobile", use: { ...devices["Pixel 7"], viewport: { width: 360, height: 780 } } },
  ],
  webServer: externalBaseUrl
    ? undefined
    : {
        command: `npm run start -- --port ${port}`,
        url: `http://127.0.0.1:${port}`,
        reuseExistingServer: !process.env.CI,
        timeout: 120_000,
      },
});
