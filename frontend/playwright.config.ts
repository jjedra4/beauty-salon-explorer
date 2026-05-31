import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright e2e config.
 *
 * Starts the frontend dev server automatically (reusing one if already
 * running). The backend is expected at http://localhost:8000 with seed data
 * loaded — `make e2e` brings the stack up first.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  use: {
    baseURL: "http://localhost:3000",
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
