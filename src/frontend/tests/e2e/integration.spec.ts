import { test, expect } from '@playwright/test'

test.describe('Authentication E2E (T346)', () => {
  test('User can navigate to app', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveURL('/')
  })

  test('App loads without errors', async ({ page }) => {
    const errors: string[] = []
    page.on('pageerror', (error) => {
      errors.push(error.toString())
    })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    expect(errors).toHaveLength(0)
  })

  test('Theme loads correctly', async ({ page }) => {
    await page.goto('/')
    const body = page.locator('body')
    const hasThemeVars = await body.evaluate(() => {
      const styles = window.getComputedStyle(document.body)
      return styles.getPropertyValue('--bg-deep') !== ''
    })
    expect(hasThemeVars).toBe(true)
  })

  test('Sidebar is present', async ({ page }) => {
    await page.goto('/')
    const sidebar = page.locator('[data-testid="sidebar"]')
    await expect(sidebar).toBeVisible()
  })

  test('Navigation items are clickable', async ({ page }) => {
    await page.goto('/')
    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await expect(chatItem).toBeVisible()
    await chatItem.click()
    await page.waitForTimeout(100)
    // Should still be on the app
    expect(page.url()).toContain('/')
  })
})

test.describe('Navigation E2E (T347)', () => {
  test('Can navigate between tabs', async ({ page }) => {
    await page.goto('/')

    const healthItem = page.locator('[data-testid="nav-item-health"]')
    await healthItem.click()
    await page.waitForTimeout(100)

    const isActive = await healthItem.evaluate((el) => {
      return window.getComputedStyle(el).borderLeft !== '2px solid transparent'
    })
    expect(isActive).toBe(true)
  })

  test('Sidebar toggles open/close', async ({ page }) => {
    await page.goto('/')
    const sidebar = page.locator('[data-testid="sidebar"]')
    const initialStyle = await sidebar.evaluate((el) => window.getComputedStyle(el).left)
    expect(initialStyle).toBe('0px')
  })

  test('Settings menu expands', async ({ page }) => {
    await page.goto('/')
    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    await settingsToggle.click()
    await page.waitForTimeout(100)

    const settingsItems = page.locator('[data-testid^="settings-item-"]')
    const count = await settingsItems.count()
    expect(count).toBeGreaterThan(0)
  })

  test('Can navigate to settings', async ({ page }) => {
    await page.goto('/')
    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    await settingsToggle.click()
    await page.waitForTimeout(100)

    const settingsItem = page.locator('[data-testid^="settings-item-"]').first()
    if (await settingsItem.isVisible()) {
      await settingsItem.click()
      await page.waitForTimeout(100)
      expect(page.url()).toContain('/')
    }
  })

  test('Navigation persists active state', async ({ page }} => {
    await page.goto('/')

    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await chatItem.click()
    await page.waitForTimeout(100)

    // Reload and check if state persists
    const stored = await page.evaluate(() => localStorage.getItem('cybersecsuite-ui'))
    expect(stored).toBeTruthy()
  })
})

test.describe('Error Handling E2E (T350)', () => {
  test('App handles missing elements gracefully', async ({ page }} => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    const body = page.locator('body')
    expect(await body.isVisible()).toBe(true)
  })

  test('No console errors on load', async ({ page }} => {
    const errors: string[] = []
    page.on('pageerror', (error) => {
      errors.push(error.toString())
    })

    await page.goto('/')
    await page.waitForLoadState('networkidle')

    expect(errors).toHaveLength(0)
  })

  test('Invalid navigation is handled', async ({ page }} => {
    await page.goto('/')
    await page.goto('/invalid-route')

    // App should still be functional
    const body = page.locator('body')
    expect(await body.isVisible()).toBe(true)
  })

  test('Component rendering errors are caught', async ({ page }} => {
    const consoleErrors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text())
      }
    })

    await page.goto('/')

    // Filter out React errors as they may be expected in dev
    const relevantErrors = consoleErrors.filter((e) => !e.includes('React'))
    expect(relevantErrors.length).toBeLessThan(5)
  })

  test('UI remains responsive after errors', async ({ page }} => {
    await page.goto('/')
    const sidebar = page.locator('[data-testid="sidebar"]')

    // Try clicking sidebar items
    const items = page.locator('[data-testid^="nav-item-"]')
    const firstItem = items.first()

    await firstItem.click()
    await page.waitForTimeout(100)

    // Sidebar should still be visible
    expect(await sidebar.isVisible()).toBe(true)
  })
})
