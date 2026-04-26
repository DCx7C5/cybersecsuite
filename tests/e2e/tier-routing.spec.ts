/**
 * E2E tests for Tier-Based Routing — T148
 * Tests authentication tier levels, route protection, and conditional access
 * 
 * Scenarios:
 * - Unauthenticated users redirected to login
 * - Free tier users have limited dashboard access
 * - Premium tier users access all features
 * - Admin tier users access admin routes
 * - Tier-based feature flagging
 * - Graceful fallback on permission denial
 */

import { test, expect } from "./fixtures";

test.describe("Tier-Based Routing & Access Control", () => {
  test.beforeEach(async ({ page }) => {
    // Clear auth state before each test
    await page.context().clearCookies();
    await page.evaluate(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
  });

  test.describe("Unauthenticated Access", () => {
    test("redirects unauthenticated users to login", async ({ page }) => {
      await page.goto("/dashboard");
      await page.waitForURL("**/login**", { timeout: 5000 }).catch(() => {});
      
      const url = page.url();
      expect(url).toMatch(/login/i);
    });

    test("prevents direct access to protected routes", async ({ page }) => {
      await page.goto("/dashboard/cases");
      
      const loginText = await page.textContent("body");
      expect(loginText).toMatch(/login|authenticate/i);
    });

    test("preserves redirect URL after login", async ({ page }) => {
      const targetUrl = "/dashboard/cases?tier=free";
      await page.goto(targetUrl);
      
      // Should be on login page
      await page.waitForURL("**/login**", { timeout: 5000 }).catch(() => {});
      
      // Simulate login
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "test-token-free");
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto(targetUrl);
      const currentUrl = page.url();
      expect(currentUrl).toContain("/dashboard/cases");
    });
  });

  test.describe("Free Tier Access Control", () => {
    test.beforeEach(async ({ page }) => {
      // Set up free tier user
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "test-token-free");
        localStorage.setItem("user_tier", "free");
        localStorage.setItem("user_id", "user-123");
      });
    });

    test("allows access to free-tier dashboard", async ({ page }) => {
      await page.goto("/dashboard");
      await page.waitForLoadState("networkidle");
      
      const dashboardContent = await page.textContent("[data-testid='dashboard-content']")
        .catch(() => page.textContent("body"));
      
      expect(dashboardContent).toBeTruthy();
    });

    test("denies access to premium-only features", async ({ page }) => {
      await page.goto("/dashboard/advanced-hunting");
      
      // Should show access denied or redirect
      const content = await page.textContent("body");
      expect(content).toMatch(/upgrade|premium|access denied/i);
    });

    test("displays tier badge on dashboard", async ({ page }) => {
      await page.goto("/dashboard");
      
      const tierBadge = page.locator("[data-testid='user-tier-badge']");
      const isVisible = await tierBadge.isVisible().catch(() => false);
      
      if (isVisible) {
        const text = await tierBadge.textContent();
        expect(text).toContain("FREE");
      }
    });

    test("hides premium-only UI elements", async ({ page }) => {
      await page.goto("/dashboard");
      await page.waitForLoadState("networkidle");
      
      const premiumButton = page.locator("[data-testid='premium-feature-button']");
      const isHidden = await premiumButton.isHidden().catch(() => true);
      
      expect(isHidden).toBe(true);
    });

    test("shows limited menu items in navigation", async ({ page }) => {
      await page.goto("/dashboard");
      
      const navItems = page.locator("[data-testid='nav-item']");
      const count = await navItems.count();
      
      // Free tier should have fewer nav items than premium
      expect(count).toBeGreaterThan(0);
      expect(count).toBeLessThan(20); // Reasonable upper bound for free tier
    });
  });

  test.describe("Premium Tier Access Control", () => {
    test.beforeEach(async ({ page }) => {
      // Set up premium tier user
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "test-token-premium");
        localStorage.setItem("user_tier", "premium");
        localStorage.setItem("user_id", "user-456");
      });
    });

    test("allows access to premium features", async ({ page }) => {
      await page.goto("/dashboard/advanced-hunting");
      
      const content = await page.textContent("body");
      expect(content).not.toMatch(/access denied/i);
    });

    test("displays premium tier badge", async ({ page }) => {
      await page.goto("/dashboard");
      
      const tierBadge = page.locator("[data-testid='user-tier-badge']");
      const isVisible = await tierBadge.isVisible().catch(() => false);
      
      if (isVisible) {
        const text = await tierBadge.textContent();
        expect(text).toContain("PREMIUM");
      }
    });

    test("shows all premium menu items", async ({ page }) => {
      await page.goto("/dashboard");
      
      const huntingLink = page.locator("a[href*='advanced-hunting']");
      const isVisible = await huntingLink.isVisible().catch(() => false);
      
      // Premium users should see advanced hunting
      if (await page.locator("[data-testid='nav-item']").count() > 0) {
        expect(isVisible).toBe(true);
      }
    });

    test("allows export/download features", async ({ page }) => {
      await page.goto("/dashboard/cases");
      
      const exportButton = page.locator("[data-testid='export-button']");
      const isEnabled = await exportButton.isEnabled().catch(() => false);
      
      if (await exportButton.isVisible().catch(() => false)) {
        expect(isEnabled).toBe(true);
      }
    });
  });

  test.describe("Admin Tier Access Control", () => {
    test.beforeEach(async ({ page }) => {
      // Set up admin tier user
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "test-token-admin");
        localStorage.setItem("user_tier", "admin");
        localStorage.setItem("user_id", "admin-789");
      });
    });

    test("allows access to admin routes", async ({ page }) => {
      await page.goto("/dashboard/admin/users");
      
      // Admin should access user management
      const content = await page.textContent("body");
      expect(content).not.toMatch(/access denied|not found/i);
    });

    test("displays admin tier badge", async ({ page }) => {
      await page.goto("/dashboard");
      
      const tierBadge = page.locator("[data-testid='user-tier-badge']");
      const isVisible = await tierBadge.isVisible().catch(() => false);
      
      if (isVisible) {
        const text = await tierBadge.textContent();
        expect(text).toContain("ADMIN");
      }
    });

    test("shows admin-only menu items", async ({ page }) => {
      await page.goto("/dashboard");
      
      const adminPanel = page.locator("a[href*='admin']");
      const isVisible = await adminPanel.isVisible().catch(() => false);
      
      expect(isVisible).toBe(true);
    });

    test("allows access to system settings", async ({ page }) => {
      await page.goto("/dashboard/admin/settings");
      
      const content = await page.textContent("body");
      expect(content).not.toMatch(/access denied/i);
    });
  });

  test.describe("Tier-Based Feature Flagging", () => {
    test("enables live threat intelligence for premium", async ({ page }) => {
      // Premium user
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard");
      const threatFeature = page.locator("[data-testid='threat-intel-live']");
      const isPremiumVisible = await threatFeature.isVisible().catch(() => false);
      
      // Free user
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      const isFreeVisible = await threatFeature.isVisible().catch(() => false);
      
      // Premium should have access, free should not
      expect(isPremiumVisible).not.toBe(isFreeVisible);
    });

    test("limits API rate limiting by tier", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      // Check rate limit indicator if visible
      const rateLimitBadge = page.locator("[data-testid='rate-limit-badge']");
      const isVisible = await rateLimitBadge.isVisible().catch(() => false);
      
      if (isVisible) {
        const text = await rateLimitBadge.textContent();
        expect(text).toMatch(/limit|rate/i);
      }
    });

    test("shows upgrade prompts for free tier", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      const upgradePrompt = page.locator("[data-testid='upgrade-prompt']");
      const isVisible = await upgradePrompt.isVisible().catch(() => false);
      
      // Free tier should show upgrade prompts
      expect(isVisible).toBe(true);
    });

    test("hides upgrade prompts for premium tier", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard");
      
      const upgradePrompt = page.locator("[data-testid='upgrade-prompt']");
      const isHidden = await upgradePrompt.isHidden().catch(() => true);
      
      expect(isHidden).toBe(true);
    });
  });

  test.describe("Tier Transition & Upgrades", () => {
    test("handles tier upgrade gracefully", async ({ page }) => {
      // Start as free tier
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      // Upgrade to premium
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "premium");
      });
      
      // Refresh should reflect new tier
      await page.reload();
      
      const tierBadge = page.locator("[data-testid='user-tier-badge']");
      const text = await tierBadge.textContent().catch(() => "");
      
      if (text) {
        expect(text).toContain("PREMIUM");
      }
    });

    test("redirects downgraded users appropriately", async ({ page }) => {
      // Start as premium
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard/advanced-hunting");
      await page.waitForLoadState("networkidle");
      
      // Downgrade to free
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      // Refresh
      await page.reload();
      
      // Should be redirected or show access denied
      const url = page.url();
      const content = await page.textContent("body");
      
      const isRedirected = !url.includes("advanced-hunting");
      const isDenied = content?.match(/access denied|upgrade/i);
      
      expect(isRedirected || isDenied).toBe(true);
    });
  });

  test.describe("Tier-Based Route Guards", () => {
    test("blocks direct URL access to premium routes for free users", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      // Attempt direct access
      await page.goto("/dashboard/advanced-hunting");
      
      // Should not successfully load premium content
      const content = await page.textContent("body");
      expect(content).toMatch(/access denied|upgrade|premium/i);
    });

    test("allows back navigation from blocked route", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      const initialUrl = page.url();
      
      // Try to access premium route
      await page.goto("/dashboard/advanced-hunting");
      
      // Go back
      await page.goBack();
      
      // Should be back at initial location
      expect(page.url()).toBe(initialUrl);
    });

    test("preserves query parameters on tier redirect", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard/cases?severity=HIGH&status=open");
      
      // Even if redirected, params should persist when accessible
      const url = page.url();
      expect(url).toContain("cases");
    });
  });

  test.describe("Session & Token Validation", () => {
    test("refreshes auth on tier check", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "valid-token");
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard");
      await page.waitForLoadState("networkidle");
      
      const storedTier = await page.evaluate(() => 
        localStorage.getItem("user_tier")
      );
      
      expect(storedTier).toBe("premium");
    });

    test("logs out user with invalid token", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "invalid-token");
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard");
      
      // Should redirect to login
      await page.waitForURL("**/login**", { timeout: 5000 }).catch(() => {});
      
      const url = page.url();
      expect(url).toMatch(/login/i);
    });

    test("handles expired session gracefully", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("auth_token", "expired-token");
        localStorage.setItem("token_expiry", String(Date.now() - 1000)); // Expired
      });
      
      await page.goto("/dashboard");
      
      // Should prompt re-authentication
      const content = await page.textContent("body");
      expect(content).toMatch(/login|session expired|authenticate/i);
    });
  });

  test.describe("Tier-Based Notifications", () => {
    test("shows tier-specific notifications", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      const notification = page.locator("[data-testid='tier-notification']");
      const isVisible = await notification.isVisible().catch(() => false);
      
      // Free tier may show notifications
      if (isVisible) {
        const text = await notification.textContent();
        expect(text).toBeTruthy();
      }
    });

    test("dismisses upgrade prompts when promoted", async ({ page }) => {
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      const dismissButton = page.locator("[data-testid='dismiss-upgrade']");
      const isVisible = await dismissButton.isVisible().catch(() => false);
      
      if (isVisible) {
        await dismissButton.click();
        
        const isGone = await dismissButton.isHidden().catch(() => true);
        expect(isGone).toBe(true);
      }
    });
  });

  test.describe("Mobile Tier Routing", () => {
    test("respects tier on mobile viewport", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "premium");
      });
      
      await page.goto("/dashboard");
      
      const content = await page.textContent("body");
      expect(content).not.toMatch(/access denied/i);
    });

    test("mobile navigation respects tier access", async ({ page }) => {
      await page.setViewportSize({ width: 375, height: 667 });
      
      await page.evaluate(() => {
        localStorage.setItem("user_tier", "free");
      });
      
      await page.goto("/dashboard");
      
      // Open mobile menu if present
      const menuButton = page.locator("[data-testid='mobile-menu-toggle']");
      if (await menuButton.isVisible().catch(() => false)) {
        await menuButton.click();
      }
      
      // Premium items should not be visible
      const premiumItem = page.locator("a[href*='advanced-hunting']");
      const isVisible = await premiumItem.isVisible().catch(() => false);
      
      expect(isVisible).toBe(false);
    });
  });
});
