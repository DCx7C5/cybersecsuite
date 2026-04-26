/**
 * Playwright fixtures for CyberSecSuite E2E tests
 * Provides reusable fixtures for:
 * - API authentication (Bearer tokens)
 * - Test data creation/cleanup
 * - Response window context
 * - Worker context
 */

import { test as base, expect } from "@playwright/test";
import type {
  APIRequestContext,
  PlaywrightTestOptions,
  PlaywrightWorkerOptions,
} from "@playwright/test";

type TestFixtures = PlaywrightTestOptions & {
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

/**
 * Test fixtures using utilities from src packages
 */

const createAuthHeader = (): Record<string, string> => {
  const token = process.env.TEST_API_KEY || "test-key";
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
};

export const test = base.extend<TestFixtures>({
  authenticatedApi: async ({ playwright }, use: (arg: APIRequestContext) => Promise<void>) => {
    const context = await playwright.request.newContext({
      baseURL: process.env.PLAYWRIGHT_BASE_URL || "http://localhost:8000",
      extraHTTPHeaders: createAuthHeader(),
    });
    await use(context);
    await context.dispose();
  },

  testFinding: async (
    { authenticatedApi },
    use: (arg: { id: number; cve_id: string; severity: string }) => Promise<void>
  ) => {
    const response = await authenticatedApi.post("/api/v1/findings/", {
      data: {
        cve_id: `CVE-2024-${Math.random().toString().slice(2, 6)}`,
        severity: "HIGH",
        description: "Test finding for E2E tests",
      },
    });

    const finding = await response.json();

    await use(finding);

    await authenticatedApi.delete(`/api/v1/findings/${finding.id}`);
  },

  responseWindowContext: async (
    { page },
    use: (arg: {
      open: () => Promise<void>;
      close: () => Promise<void>;
      isVisible: () => Promise<boolean>;
    }) => Promise<void>
  ) => {
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
        return page.locator('[data-testid="response-window"]').isVisible();
      },
    };

    await use(responseWindow);
  },

  workerContext: async (
    { page },
    use: (arg: {
      status: () => Promise<string>;
      logs: () => Promise<string[]>;
    }) => Promise<void>
  ) => {
    const workerContext = {
      async status() {
        const status = await page
          .locator('[data-testid="worker-status"]')
          .textContent();
        return status || "unknown";
      },
      async logs() {
        return page
          .locator('[data-testid="worker-logs"] .log-entry')
          .allTextContents();
      },
    };

    await use(workerContext);
  },
});

export { expect };
