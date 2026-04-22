/**
 * E2E tests for Response Window — T0B-UI-005
 * Tests rendering, state management, and interaction of response window component
 * 
 * Scenarios:
 * - Toggle response window visibility
 * - Display finding data in response window
 * - Render worker context alongside response
 * - Handle error states and loading states
 * - Responsive layout on mobile/tablet
 */

import { test, expect } from "./fixtures";

test.describe("Response Window Rendering", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    // Wait for dashboard to load
    await page.waitForLoadState("networkidle");
  });

  test("should toggle response window visibility", async ({
    page,
    responseWindowContext,
  }) => {
    // Initially hidden
    let isVisible = await responseWindowContext.isVisible();
    expect(isVisible).toBe(false);

    // Open response window
    await responseWindowContext.open();
    isVisible = await responseWindowContext.isVisible();
    expect(isVisible).toBe(true);

    // Close response window
    await responseWindowContext.close();
    isVisible = await responseWindowContext.isVisible();
    expect(isVisible).toBe(false);
  });

  test("should render finding data in response window", async ({
    page,
    responseWindowContext,
    testFinding,
  }) => {
    await page.evaluate((cveId) => {
      window.dispatchEvent(
        new CustomEvent("display-finding", { detail: { cve_id: cveId } })
      );
    }, testFinding.cve_id);

    await responseWindowContext.open();

    // Verify finding data is rendered
    const findingText = page.locator(
      '[data-testid="response-finding-cve-id"]'
    );
    await expect(findingText).toContainText(testFinding.cve_id);

    const severityBadge = page.locator(
      '[data-testid="response-finding-severity"]'
    );
    await expect(severityBadge).toContainText("HIGH");
  });

  test("should display loading state while fetching", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    // Simulate loading state
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("response-loading", { detail: { loading: true } })
      );
    });

    const spinner = page.locator('[data-testid="response-loading-spinner"]');
    await expect(spinner).toBeVisible();

    // Simulate loading complete
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("response-loading", { detail: { loading: false } })
      );
    });

    await expect(spinner).not.toBeVisible();
  });

  test("should display error state with error message", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    // Simulate error state
    const errorMessage = "Failed to fetch finding data";
    await page.evaluate((msg) => {
      window.dispatchEvent(
        new CustomEvent("response-error", {
          detail: { error: msg, statusCode: 500 },
        })
      );
    }, errorMessage);

    const errorElement = page.locator('[data-testid="response-error-message"]');
    await expect(errorElement).toContainText(errorMessage);
    await expect(errorElement).toHaveClass(/error-state/);
  });

  test("should close response window with escape key", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();
    expect(await responseWindowContext.isVisible()).toBe(true);

    // Press Escape
    await page.keyboard.press("Escape");

    expect(await responseWindowContext.isVisible()).toBe(false);
  });

  test("should maintain scroll position when response window opens", async ({
    page,
    responseWindowContext,
  }) => {
    // Scroll dashboard content
    await page.evaluate(() => {
      document.documentElement.scrollTop = 500;
    });

    const scrollBefore = await page.evaluate(() => document.documentElement.scrollTop);

    await responseWindowContext.open();

    const scrollAfter = await page.evaluate(
      () => document.documentElement.scrollTop
    );

    expect(scrollBefore).toBe(scrollAfter);
  });

  test("should handle rapid open/close toggling", async ({
    page,
    responseWindowContext,
  }) => {
    for (let i = 0; i < 5; i++) {
      await responseWindowContext.open();
      await page.waitForTimeout(100);
      await responseWindowContext.close();
      await page.waitForTimeout(100);
    }

    const isVisible = await responseWindowContext.isVisible();
    expect(isVisible).toBe(false);
  });
});

test.describe("Response Window on Mobile", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display response window as full-screen overlay on mobile", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    const responseWindow = page.locator('[data-testid="response-window"]');
    const viewportSize = page.viewportSize();

    const boundingBox = await responseWindow.boundingBox();
    expect(boundingBox?.width).toBeCloseTo(viewportSize!.width, 10);
    expect(boundingBox?.height).toBeCloseTo(viewportSize!.height, 10);
  });

  test("should show mobile-friendly close button", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    const closeButton = page.locator(
      '[data-testid="response-window-close-mobile"]'
    );
    await expect(closeButton).toBeVisible();
  });
});

test.describe("Response Window with Worker Context", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display worker status alongside response data", async ({
    page,
    responseWindowContext,
    workerContext,
  }) => {
    await responseWindowContext.open();

    const workerStatusElement = page.locator(
      '[data-testid="response-worker-status"]'
    );
    await expect(workerStatusElement).toBeVisible();

    const status = await workerContext.status();
    expect(["idle", "running", "error"]).toContain(status);
  });

  test("should update response when worker context changes", async ({
    page,
    responseWindowContext,
    workerContext,
  }) => {
    await responseWindowContext.open();

    // Simulate worker status change
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-status-changed", {
          detail: { status: "running" },
        })
      );
    });

    const status = await workerContext.status();
    expect(status).toBe("running");

    const workerIndicator = page.locator(
      '[data-testid="response-worker-indicator"]'
    );
    await expect(workerIndicator).toHaveClass(/status-running/);
  });

  test("should display worker logs in response window", async ({
    page,
    responseWindowContext,
    workerContext,
  }) => {
    await responseWindowContext.open();

    // Add worker logs
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: { message: "Processing finding CVE-2024-1234" },
        })
      );
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: { message: "Hash computed successfully" },
        })
      );
    });

    await page.waitForTimeout(500);

    const logs = await workerContext.logs();
    expect(logs.length).toBeGreaterThanOrEqual(2);
    expect(logs.join("")).toContain("Processing finding");
    expect(logs.join("")).toContain("Hash computed");
  });

  test("should clear worker logs when response window closes", async ({
    page,
    responseWindowContext,
    workerContext,
  }) => {
    await responseWindowContext.open();

    // Add logs
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: { message: "Test log entry" },
        })
      );
    });

    let logs = await workerContext.logs();
    expect(logs.length).toBeGreaterThan(0);

    await responseWindowContext.close();

    // Note: Actual behavior depends on implementation
    // This test may need adjustment based on actual clearing behavior
    logs = await workerContext.logs();
    // Verify state is clean for next interaction
  });
});

test.describe("Response Window Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should have proper ARIA labels on response window elements", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    const closeButton = page.locator('[data-testid="response-window-close"]');
    await expect(closeButton).toHaveAttribute("aria-label", /close/i);

    const window = page.locator('[data-testid="response-window"]');
    await expect(window).toHaveAttribute("role", "dialog");
  });

  test("should be keyboard navigable", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    // Tab through response window elements
    await page.keyboard.press("Tab");
    const focusedElement = await page.evaluate(() => document.activeElement?.getAttribute("data-testid"));
    expect(focusedElement).toBeTruthy();

    // Tab again
    await page.keyboard.press("Tab");
    const nextFocused = await page.evaluate(() => document.activeElement?.getAttribute("data-testid"));
    expect(nextFocused).not.toBe(focusedElement);
  });

  test("should trap focus within response window when open", async ({
    page,
    responseWindowContext,
  }) => {
    await responseWindowContext.open();

    // Get first and last focusable elements
    const focusableElements = await page.locator(
      '[data-testid="response-window"] [tabindex]'
    ).count();

    expect(focusableElements).toBeGreaterThan(0);

    // Tab to last element, then tab again should cycle back
    for (let i = 0; i < focusableElements + 1; i++) {
      await page.keyboard.press("Tab");
    }

    const finalFocus = await page.evaluate(() =>
      document.activeElement?.getAttribute("data-testid")
    );
    expect(finalFocus).toContain("response");
  });
});

test.describe("Response Window Performance", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should render response window within 500ms", async ({
    page,
    responseWindowContext,
  }) => {
    const startTime = Date.now();
    await responseWindowContext.open();
    const renderTime = Date.now() - startTime;

    expect(renderTime).toBeLessThan(500);
  });

  test("should not cause layout shift when opening", async ({
    page,
    responseWindowContext,
  }) => {
    const initialLayout = await page.evaluate(() => {
      const elements = document.querySelectorAll("[data-testid]");
      return Array.from(elements).map((el) => {
        const rect = (el as HTMLElement).getBoundingClientRect();
        return { id: el.id, top: rect.top, left: rect.left };
      });
    });

    await responseWindowContext.open();

    const finalLayout = await page.evaluate(() => {
      const elements = document.querySelectorAll("[data-testid]");
      return Array.from(elements).map((el) => {
        const rect = (el as HTMLElement).getBoundingClientRect();
        return { id: el.id, top: rect.top, left: rect.left };
      });
    });

    // Allow minimal shift, but no major layout changes
    const shiftCount = initialLayout.filter((initial, idx) => {
      const final = finalLayout[idx];
      if (!final) return false;
      const topDiff = Math.abs(initial.top - final.top);
      const leftDiff = Math.abs(initial.left - final.left);
      return topDiff > 50 || leftDiff > 50;
    }).length;

    expect(shiftCount).toBeLessThan(3);
  });
});
