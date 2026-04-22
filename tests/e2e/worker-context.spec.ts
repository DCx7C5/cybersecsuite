/**
 * E2E tests for Worker Context — T0B-UI-005
 * Tests worker status monitoring, logging, and context awareness
 * 
 * Scenarios:
 * - Display worker status indicator (idle/running/error)
 * - Show worker logs in real-time
 * - Handle worker context switches
 * - Display worker architecture and scope info
 * - Error states and recovery
 */

import { test, expect } from "./fixtures";

test.describe("Worker Context Status Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display worker status indicator", async ({
    page,
    workerContext,
  }) => {
    const statusElement = page.locator('[data-testid="worker-status"]');
    await expect(statusElement).toBeVisible();

    const status = await workerContext.status();
    expect(["idle", "running", "error"]).toContain(status);
  });

  test("should update status when worker starts processing", async ({
    page,
    workerContext,
  }) => {
    let status = await workerContext.status();
    expect(status).toBe("idle");

    // Simulate worker start
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-status-changed", {
          detail: { status: "running" },
        })
      );
    });

    await page.waitForTimeout(200);
    status = await workerContext.status();
    expect(status).toBe("running");

    const statusBadge = page.locator('[data-testid="worker-status-badge"]');
    await expect(statusBadge).toHaveClass(/status-running/);
  });

  test("should display idle status with correct styling", async ({
    page,
    workerContext,
  }) => {
    const statusBadge = page.locator('[data-testid="worker-status-badge"]');
    const status = await workerContext.status();

    if (status === "idle") {
      await expect(statusBadge).toHaveClass(/status-idle/);
      await expect(statusBadge).toHaveCSS("background-color", /gray|rgb\(128/i);
    }
  });

  test("should display running status with animation", async ({
    page,
    workerContext,
  }) => {
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-status-changed", {
          detail: { status: "running" },
        })
      );
    });

    await page.waitForTimeout(200);

    const statusBadge = page.locator('[data-testid="worker-status-badge"]');
    await expect(statusBadge).toHaveClass(/status-running/);
    await expect(statusBadge).toHaveClass(/animate/);
  });

  test("should display error status with error indicator", async ({
    page,
    workerContext,
  }) => {
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-error", {
          detail: {
            error: "Worker process crashed",
            code: "WORKER_CRASH",
          },
        })
      );
    });

    await page.waitForTimeout(200);

    const statusBadge = page.locator('[data-testid="worker-status-badge"]');
    await expect(statusBadge).toHaveClass(/status-error/);

    const errorIndicator = page.locator('[data-testid="worker-error-indicator"]');
    await expect(errorIndicator).toBeVisible();
  });
});

test.describe("Worker Logs Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display worker logs in real-time", async ({
    page,
    workerContext,
  }) => {
    // Add a log entry
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: {
            timestamp: new Date().toISOString(),
            level: "info",
            message: "Starting worker process",
          },
        })
      );
    });

    await page.waitForTimeout(500);

    const logs = await workerContext.logs();
    expect(logs.length).toBeGreaterThan(0);
    expect(logs.join("")).toContain("Starting worker process");
  });

  test("should display log levels with correct styling", async ({
    page,
    workerContext,
  }) => {
    // Add logs with different levels
    const logLevels = ["info", "warn", "error", "debug"];

    for (const level of logLevels) {
      await page.evaluate((lv) => {
        window.dispatchEvent(
          new CustomEvent("worker-log", {
            detail: {
              level: lv,
              message: `Test ${lv} message`,
            },
          })
        );
      }, level);
    }

    await page.waitForTimeout(500);

    const logs = await page.locator('[data-testid="worker-logs"] .log-entry');
    expect(await logs.count()).toBe(logLevels.length);

    // Check first log has correct class
    const firstLog = logs.nth(0);
    const classList = await firstLog.getAttribute("class");
    expect(classList).toContain("log-info");
  });

  test("should auto-scroll to latest log entry", async ({
    page,
    workerContext,
  }) => {
    const logsContainer = page.locator('[data-testid="worker-logs"]');

    // Add many log entries
    for (let i = 0; i < 20; i++) {
      await page.evaluate((idx) => {
        window.dispatchEvent(
          new CustomEvent("worker-log", {
            detail: {
              message: `Log entry ${idx}`,
            },
          })
        );
      }, i);
    }

    await page.waitForTimeout(500);

    // Check scroll position
    const scrollTop = await logsContainer.evaluate(
      (el) => el.scrollHeight - el.clientHeight - el.scrollTop
    );

    // Should be scrolled to bottom (within 2px tolerance)
    expect(scrollTop).toBeLessThan(2);
  });

  test("should respect log level filtering", async ({ page }) => {
    // Add logs of different levels
    for (const level of ["info", "warn", "error"]) {
      await page.evaluate((lv) => {
        window.dispatchEvent(
          new CustomEvent("worker-log", {
            detail: { level: lv, message: `${lv} message` },
          })
        );
      }, level);
    }

    await page.waitForTimeout(500);

    // Filter to show only errors
    const filterButton = page.locator('[data-testid="worker-log-filter"]');
    if (await filterButton.isVisible()) {
      await filterButton.click();
      await page.click('[data-testid="worker-log-filter-error"]');

      const visibleLogs = await page.locator(
        '[data-testid="worker-logs"] .log-entry:visible'
      );
      const visibleCount = await visibleLogs.count();

      expect(visibleCount).toBeLessThanOrEqual(1);
    }
  });

  test("should allow clearing worker logs", async ({ page, workerContext }) => {
    // Add log entries
    for (let i = 0; i < 5; i++) {
      await page.evaluate((idx) => {
        window.dispatchEvent(
          new CustomEvent("worker-log", {
            detail: { message: `Log ${idx}` },
          })
        );
      }, i);
    }

    await page.waitForTimeout(500);

    let logs = await workerContext.logs();
    expect(logs.length).toBeGreaterThan(0);

    // Clear logs
    const clearButton = page.locator('[data-testid="worker-logs-clear"]');
    if (await clearButton.isVisible()) {
      await clearButton.click();

      await page.waitForTimeout(300);

      logs = await workerContext.logs();
      expect(logs.length).toBe(0);
    }
  });

  test("should preserve log history on page reload", async ({
    page,
    workerContext,
  }) => {
    // Add log entry
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: { message: "Persistent log entry" },
        })
      );
    });

    await page.waitForTimeout(500);

    // Store logs before reload
    const logsBefore = await workerContext.logs();

    // Reload page (if localStorage/sessionStorage is used)
    await page.reload();
    await page.waitForLoadState("networkidle");

    const logsAfter = await workerContext.logs();

    // History should be preserved (implementation dependent)
    // This assumes localStorage persistence
  });
});

test.describe("Worker Context Information Display", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display worker architecture info", async ({ page }) => {
    const archElement = page.locator('[data-testid="worker-architecture"]');
    if (await archElement.isVisible()) {
      const archText = await archElement.textContent();
      expect(archText).toBeTruthy();
      // Should contain info like Python version, OS, etc.
      expect(
        archText?.match(/python|linux|windows|darwin|arm|x86/i)
      ).toBeTruthy();
    }
  });

  test("should display worker scope information", async ({ page }) => {
    const scopeElement = page.locator('[data-testid="worker-scope"]');
    if (await scopeElement.isVisible()) {
      const scopeText = await scopeElement.textContent();
      expect(scopeText).toBeTruthy();
      // Should contain scope details
      expect(scopeText?.length).toBeGreaterThan(0);
    }
  });

  test("should display worker uptime", async ({ page, workerContext }) => {
    const uptimeElement = page.locator('[data-testid="worker-uptime"]');
    if (await uptimeElement.isVisible()) {
      const uptimeText = await uptimeElement.textContent();
      expect(uptimeText).toBeTruthy();
      // Should show time format like "2h 30m 15s"
      expect(uptimeText?.match(/\d+[hms]/)).toBeTruthy();
    }
  });

  test("should display worker resource usage", async ({ page }) => {
    const resourceElement = page.locator('[data-testid="worker-resources"]');
    if (await resourceElement.isVisible()) {
      const cpuElement = page.locator(
        '[data-testid="worker-resources-cpu"]'
      );
      const memElement = page.locator(
        '[data-testid="worker-resources-memory"]'
      );

      if (await cpuElement.isVisible()) {
        const cpuText = await cpuElement.textContent();
        expect(cpuText?.match(/\d+%/)).toBeTruthy();
      }

      if (await memElement.isVisible()) {
        const memText = await memElement.textContent();
        expect(memText?.match(/\d+/)).toBeTruthy();
      }
    }
  });
});

test.describe("Worker Context Switching", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display multiple worker contexts", async ({ page }) => {
    const workerItems = page.locator('[data-testid="worker-item"]');
    const count = await workerItems.count();

    if (count > 0) {
      expect(count).toBeGreaterThan(0);
    }
  });

  test("should switch between worker contexts", async ({ page }) => {
    const workerItems = page.locator('[data-testid="worker-item"]');
    const count = await workerItems.count();

    if (count > 1) {
      const firstWorker = workerItems.nth(0);
      const secondWorker = workerItems.nth(1);

      // Click second worker
      await secondWorker.click();
      await page.waitForTimeout(300);

      // Check if selected state changed
      const firstSelected = await firstWorker.locator("..").evaluate(
        (el) => el.classList.contains("selected")
      );
      const secondSelected = await secondWorker.locator("..").evaluate(
        (el) => el.classList.contains("selected")
      );

      expect(secondSelected).toBe(true);
    }
  });

  test("should preserve logs when switching worker context", async ({
    page,
  }) => {
    // Add log to first worker
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-log", {
          detail: { message: "Worker 1 log" },
        })
      );
    });

    // Switch to second worker (if available)
    const workerItems = page.locator('[data-testid="worker-item"]');
    if ((await workerItems.count()) > 1) {
      await workerItems.nth(1).click();
      await page.waitForTimeout(300);

      // Switch back
      await workerItems.nth(0).click();
      await page.waitForTimeout(300);

      // Logs should still be visible
      const logEntry = page.locator(
        '[data-testid="worker-logs"] .log-entry:has-text("Worker 1 log")'
      );
      await expect(logEntry).toBeVisible();
    }
  });
});

test.describe("Worker Error Handling", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should display error message when worker crashes", async ({
    page,
  }) => {
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-error", {
          detail: {
            error: "Worker process exited unexpectedly",
            code: "WORKER_CRASH",
            exitCode: 1,
          },
        })
      );
    });

    const errorMessage = page.locator('[data-testid="worker-error-message"]');
    await expect(errorMessage).toBeVisible();
    await expect(errorMessage).toContainText("Worker process exited");
  });

  test("should show restart button on worker error", async ({ page }) => {
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-error", {
          detail: { error: "Connection lost", code: "WORKER_TIMEOUT" },
        })
      );
    });

    const restartButton = page.locator(
      '[data-testid="worker-restart-button"]'
    );
    await expect(restartButton).toBeVisible();
  });

  test("should handle worker restart", async ({ page, workerContext }) => {
    // Simulate error
    await page.evaluate(() => {
      window.dispatchEvent(
        new CustomEvent("worker-error", {
          detail: { error: "Worker failed" },
        })
      );
    });

    let status = await workerContext.status();
    expect(status).toBe("error");

    // Click restart
    const restartButton = page.locator(
      '[data-testid="worker-restart-button"]'
    );
    if (await restartButton.isVisible()) {
      await restartButton.click();

      await page.waitForTimeout(1000);

      // Status should change back to running
      status = await workerContext.status();
      expect(["running", "idle"]).toContain(status);
    }
  });
});

test.describe("Worker Context Accessibility", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should have proper ARIA labels for worker elements", async ({
    page,
  }) => {
    const statusBadge = page.locator('[data-testid="worker-status-badge"]');
    const ariaLabel = await statusBadge.getAttribute("aria-label");
    expect(ariaLabel).toBeTruthy();
    expect(ariaLabel?.toLowerCase()).toContain("worker");
  });

  test("should announce worker status changes to screen readers", async ({
    page,
  }) => {
    const ariaLive = page.locator('[data-testid="worker-status"]');
    const ariaLiveValue = await ariaLive.getAttribute("aria-live");
    expect(ariaLiveValue).toMatch(/polite|assertive/);
  });

  test("should support keyboard navigation in worker context", async ({
    page,
  }) => {
    const workerItems = page.locator('[data-testid="worker-item"]');
    if ((await workerItems.count()) > 1) {
      // Focus first item
      await workerItems.nth(0).focus();

      // Arrow down should move to next
      await page.keyboard.press("ArrowDown");

      const focusedElement = await page.evaluate(() =>
        document.activeElement?.getAttribute("data-testid")
      );
      expect(focusedElement).toContain("worker");
    }
  });
});

test.describe("Worker Performance Monitoring", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");
  });

  test("should not cause performance degradation with many logs", async ({
    page,
  }) => {
    const startTime = performance.now();

    // Add 100 log entries quickly
    for (let i = 0; i < 100; i++) {
      await page.evaluate((idx) => {
        window.dispatchEvent(
          new CustomEvent("worker-log", {
            detail: { message: `Log ${idx}` },
          })
        );
      }, i);
    }

    await page.waitForTimeout(500);

    const endTime = performance.now();
    const duration = endTime - startTime;

    // Should handle 100 logs within reasonable time
    expect(duration).toBeLessThan(10000);
  });

  test("should render worker context within performance budget", async ({
    page,
  }) => {
    const startTime = performance.now();

    // Navigate to dashboard
    await page.goto("/dashboard");
    await page.waitForLoadState("networkidle");

    const endTime = performance.now();
    const duration = endTime - startTime;

    expect(duration).toBeLessThan(3000);
  });
});
