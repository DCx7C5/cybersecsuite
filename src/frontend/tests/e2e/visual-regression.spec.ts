import { test, expect, Page } from '@playwright/test'

/**
 * Visual Regression Tests - Phase 11.4
 * Fast path: Chromium only (local execution)
 * Full suite: Chromium + Firefox + WebKit (reserved for CI)
 * Threshold: maxDiffPixels=100, threshold=0.2%
 * Target: 12 baseline tests, ~60 seconds execution
 */

// Helper to navigate to a panel and wait for content
async function navigateToPanel(page: Page, panelName: string) {
  await page.goto('/')
  await page.waitForLoadState('networkidle')
  // Wait for sidebar to load
  await expect(page.locator('[id="shell"]')).toBeVisible()
}

test.describe('Visual Regression Tests', () => {
  test.beforeEach(async ({ page }) => {
    // Disable animations for consistent visual regression
    await page.addInitScript(() => {
      document.documentElement.style.scrollBehavior = 'auto'
      const style = document.createElement('style')
      style.textContent = `
        * {
          animation-duration: 0.01ms !important;
          animation-iteration-count: 1 !important;
          transition-duration: 0.01ms !important;
        }
      `
      document.head.appendChild(style)
    })
  })

  test('1. Homepage layout and shell', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await expect(page.locator('[id="shell"]')).toBeVisible()
    // Wait for sidebar and topbar to render
    await page.waitForTimeout(500)
    await expect(page).toHaveScreenshot('homepage-shell.png', {
      fullPage: false,
      mask: [page.locator('[id="main-content"]')],
    })
  })

  test('2. Sidebar navigation visible', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const sidebar = page.locator('aside, [role="navigation"]').first()
    await expect(sidebar).toBeVisible()
    await page.waitForTimeout(300)
    await expect(sidebar).toHaveScreenshot('sidebar-navigation.png')
  })

  test('3. Topbar with controls', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const topbar = page.locator('header, [role="banner"]').first()
    await expect(topbar).toBeVisible()
    await page.waitForTimeout(300)
    await expect(topbar).toHaveScreenshot('topbar-controls.png')
  })

  test('4. Chat panel interface', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Navigate to chat panel by clicking sidebar
    const chatLink = page.locator('a, button').filter({ hasText: /chat|agent/i }).first()
    if (await chatLink.isVisible()) {
      await chatLink.click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    const mainContent = page.locator('[id="main-content"]')
    await expect(mainContent).toBeVisible()
    await expect(mainContent).toHaveScreenshot('chat-panel-interface.png')
  })

  test('5. Marketplace panel cards', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Click marketplace tab if available
    const marketplaceLink = page.locator('a, button').filter({ hasText: /marketplace/i }).first()
    if (await marketplaceLink.isVisible()) {
      await marketplaceLink.click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    const mainContent = page.locator('[id="main-content"]')
    await expect(mainContent).toBeVisible()
    await expect(mainContent).toHaveScreenshot('marketplace-panel-cards.png')
  })

  test('6. Health/status indicators', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Navigate to health panel
    const healthLink = page.locator('a, button').filter({ hasText: /health|status/i }).first()
    if (await healthLink.isVisible()) {
      await healthLink.click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    const mainContent = page.locator('[id="main-content"]')
    await expect(mainContent).toBeVisible()
    await expect(mainContent).toHaveScreenshot('health-status-indicators.png')
  })

  test('7. Form controls and inputs', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Look for any form inputs
    const inputs = page.locator('input, textarea, select')
    if ((await inputs.count()) > 0) {
      const firstInput = inputs.first()
      await expect(firstInput).toBeVisible()
      const inputContainer = firstInput.locator('..').first()
      await expect(inputContainer).toHaveScreenshot('form-controls-inputs.png')
    } else {
      // Fallback to main content
      const mainContent = page.locator('[id="main-content"]')
      await expect(mainContent).toHaveScreenshot('form-controls-inputs.png')
    }
  })

  test('8. Buttons and interactive elements', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Look for buttons
    const buttons = page.locator('button')
    if ((await buttons.count()) > 0) {
      const buttonContainer = buttons.first().locator('..').first()
      await page.waitForTimeout(300)
      await expect(buttonContainer).toHaveScreenshot('buttons-interactive-elements.png')
    } else {
      const mainContent = page.locator('[id="main-content"]')
      await expect(mainContent).toHaveScreenshot('buttons-interactive-elements.png')
    }
  })

  test('9. Data tables and lists', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Navigate to a panel with data (e.g., investigations, findings)
    const dataLink = page.locator('a, button').filter({ hasText: /investigations|findings|cases|tasks/i }).first()
    if (await dataLink.isVisible()) {
      await dataLink.click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    const mainContent = page.locator('[id="main-content"]')
    await expect(mainContent).toBeVisible()
    await expect(mainContent).toHaveScreenshot('data-tables-lists.png')
  })

  test('10. Theme consistency (light mode)', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Try to set light theme if toggle exists
    const themeToggle = page.locator('[aria-label*="theme" i], [title*="theme" i]').first()
    if (await themeToggle.isVisible()) {
      const isLight = await page.locator('html').evaluate(() => 
        document.documentElement.classList.contains('light') ||
        document.documentElement.style.colorScheme === 'light'
      )
      if (!isLight) {
        await themeToggle.click()
        await page.waitForTimeout(500)
      }
    }
    const shell = page.locator('[id="shell"]')
    await expect(shell).toBeVisible()
    await expect(shell).toHaveScreenshot('theme-consistency-light.png')
  })

  test('11. Settings panel interface', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    // Navigate to settings
    const settingsLink = page.locator('a, button').filter({ hasText: /settings/i }).first()
    if (await settingsLink.isVisible()) {
      await settingsLink.click()
      await page.waitForLoadState('networkidle')
      await page.waitForTimeout(500)
    }
    const mainContent = page.locator('[id="main-content"]')
    await expect(mainContent).toBeVisible()
    await expect(mainContent).toHaveScreenshot('settings-panel-interface.png')
  })

  test('12. Status bar information', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const statusBar = page.locator('footer, [role="contentinfo"], [id*="status"]').first()
    if (await statusBar.isVisible()) {
      await page.waitForTimeout(300)
      await expect(statusBar).toHaveScreenshot('status-bar-information.png')
    } else {
      // Fallback to shell
      const shell = page.locator('[id="shell"]')
      await expect(shell).toHaveScreenshot('status-bar-information.png')
    }
  })
})
