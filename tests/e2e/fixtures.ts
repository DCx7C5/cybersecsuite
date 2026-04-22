/**
 * Playwright fixtures for CyberSecSuite E2E tests
 * Provides reusable fixtures for:
 * - API authentication (Bearer tokens)
 * - Test data creation/cleanup
 * - Response window context
 * - Worker context
 */

import { test as base, expect } from "@playwright/test";
import { APIRequestContext } from "@playwright/test";

type TestFixtures = {
  authenticatedApi: APIRequestContext;
  testFinding: {
    id: number;
    cve_id: string;
    severity: string;
  };
  responseWindowContext: {
    open: () => Promise<void>;
    close: () => Promise<void>;
    isVisible: () => Promise<boolean>;
  };
  workerContext: {
    status: () => Promise<string>;
    logs: () => Promise<string[]>;
  };
};

export const test = base.extend<TestFixtures>({
  authenticatedApi: async ({ playwright }, use) => {
    const context = await playwright.request.newContext({
      baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000",
      extraHTTPHeaders: {
        Authorization: `Bearer ${process.env.TEST_API_KEY || "test-key"}`,
        "Content-Type": "application/json",
      },
    });
    await use(context);
    await context.dispose();
  },

  testFinding: async ({ authenticatedApi }, use) => {
    // Create test finding
    const response = await authenticatedApi.post("/api/v1/findings/", {
      data: {
        cve_id: `CVE-2024-${Math.random().toString().slice(2, 6)}`,
        severity: "HIGH",
        description: "Test finding for E2E tests",
      },
    });

    const finding = await response.json();

    await use(finding);

    // Cleanup
    await authenticatedApi.delete(`/api/v1/findings/${finding.id}`);
  },

  responseWindowContext: async ({ page }, use) => {
    const responseWindow = {
      async open() {
        await page.click('[data-testid="response-window-toggle"]');
        await page.waitForSelector('[data-testid="response-window"]', {
          state: "visible",
          timeout: 5000,
        });
      },
      async close() {
        await page.click('[data-testid="response-window-close"]');
        await page.waitForSelector('[data-testid="response-window"]', {
          state: "hidden",
          timeout: 5000,
        });
      },
      async isVisible() {
        const element = page.locator('[data-testid="response-window"]');
        return element.isVisible();
      },
    };

    await use(responseWindow);
  },

  workerContext: async ({ page }, use) => {
    const workerContext = {
      async status() {
        const status = await page
          .locator('[data-testid="worker-status"]')
          .textContent();
        return status || "unknown";
      },
      async logs() {
        const logs = await page
          .locator('[data-testid="worker-logs"] .log-entry')
          .allTextContents();
        return logs;
      },
    };

    await use(workerContext);
  },
});

export { expect };
