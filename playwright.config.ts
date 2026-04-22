/**
 * Playwright configuration for CyberSecSuite E2E tests
 * - Base URL: http://localhost:8000 (local dev server)
 * - Browser: Chromium, Firefox, WebKit
 * - Reporters: HTML, JSON, GitHub Actions
 * - CI/CD: GitHub Actions workflow integration
 * - Retries: Disabled in CI, 2 retries in local dev
 * 
 * Usage (dev):
 *   npx playwright test
 * 
 * Usage (CI):
 *   npx playwright test --reporter=github
 * 
 * Debug:
 *   npx playwright test --debug
 */

import { defineConfig, devices } from "@playwright/test";

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000";
const CI = !!process.env.CI;

export default defineConfig({
  testDir: "./tests/e2e",
  testMatch: "*.spec.ts",
  timeout: 30 * 1000,
  expect: {
    timeout: 5 * 1000,
  },
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: CI ? 2 : 0,
  workers: CI ? 1 : undefined,
  reporter: CI
    ? [
        ["github"],
        ["html", { outputFolder: "test-results/html" }],
        ["json", { outputFile: "test-results/results.json" }],
      ]
    : [
        ["html", { outputFolder: "test-results/html", open: "on-failure" }],
        ["list"],
      ],
  use: {
    baseURL: BASE_URL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
    {
      name: "firefox",
      use: { ...devices["Desktop Firefox"] },
    },
    {
      name: "webkit",
      use: { ...devices["Desktop Safari"] },
    },
    {
      name: "Mobile Chrome",
      use: { ...devices["Pixel 5"] },
    },
  ],
  webServer: {
    command: "uv run uvicorn src.main:app --host 0.0.0.0 --port 8000",
    url: BASE_URL,
    timeout: 120 * 1000,
    reuseExistingServer: !CI,
  },
});
