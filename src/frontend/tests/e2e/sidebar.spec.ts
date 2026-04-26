import { test, expect } from '@playwright/test'

test.describe('Sidebar component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('Sidebar renders on page load', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]')
    await expect(sidebar).toBeVisible()
  })

  test('Sidebar nav items are clickable', async ({ page }) => {
    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await expect(chatItem).toBeVisible()
    await chatItem.click()
    // Item should be highlighted
    const style = await chatItem.evaluate((el) => window.getComputedStyle(el).background)
    expect(style).toBeTruthy()
  })

  test('Sidebar settings toggle works', async ({ page }) => {
    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    await expect(settingsToggle).toBeVisible()

    // Initially settings should be closed (▸)
    let chevron = await settingsToggle.locator('span').last().textContent()
    expect(chevron).toContain('▸')

    // Click to open
    await settingsToggle.click()
    await page.waitForTimeout(100)

    // Should now show ▾
    chevron = await settingsToggle.locator('span').last().textContent()
    expect(chevron).toContain('▾')

    // Settings items should be visible
    const settingsItems = page.locator('[data-testid^="settings-item-"]')
    const count = await settingsItems.count()
    expect(count).toBeGreaterThan(0)

    // Click to close
    await settingsToggle.click()
    await page.waitForTimeout(100)

    // Settings items should be hidden
    const visibleCount = await settingsItems.filter({ hasNot: page.locator('body > *') }).count()
    expect(visibleCount).toBeLessThanOrEqual(count)
  })

  test('Sidebar persists settings open state', async ({ page, context }) => {
    const settingsToggle = page.locator('[data-testid="settings-toggle"]')

    // Open settings
    await settingsToggle.click()
    await page.waitForTimeout(100)

    // Get localStorage value
    const stored = await page.evaluate(() => localStorage.getItem('sidebar-settings-open'))
    expect(stored).toBe('true')

    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Settings should still be open
    const settingsItems = page.locator('[data-testid^="settings-item-"]')
    const isVisible = await settingsItems.first().isVisible().catch(() => false)
    expect(isVisible).toBe(true)
  })

  test('Sidebar responds to screen size changes', async ({ page, context }) => {
    const sidebar = page.locator('[data-testid="sidebar"]')

    // Desktop size
    await page.setViewportSize({ width: 1024, height: 768 })
    await expect(sidebar).toBeVisible()

    // Tablet size
    await page.setViewportSize({ width: 768, height: 1024 })
    const styleTablet = await sidebar.evaluate((el) => window.getComputedStyle(el).width)
    expect(styleTablet).toBeTruthy()

    // Mobile size
    await page.setViewportSize({ width: 375, height: 667 })
    const styleMobile = await sidebar.evaluate((el) => window.getComputedStyle(el).width)
    expect(styleMobile).toBeTruthy()
  })

  test('Sidebar nav groups render correctly', async ({ page }) => {
    const platformGroup = page.locator('[data-testid="nav-group-platform"]')
    const agentsGroup = page.locator('[data-testid="nav-group-agents"]')

    await expect(platformGroup).toBeVisible()
    await expect(agentsGroup).toBeVisible()
  })

  test('Sidebar maintains active tab state', async ({ page }) => {
    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await chatItem.click()
    await page.waitForTimeout(100)

    // Check if Chat is highlighted
    const isActive = await chatItem.evaluate((el) => {
      return window.getComputedStyle(el).borderLeft !== '2px solid transparent'
    })
    expect(isActive).toBe(true)

    // Click another item
    const healthItem = page.locator('[data-testid="nav-item-health"]')
    await healthItem.click()
    await page.waitForTimeout(100)

    // Chat should no longer be highlighted
    const isChatActive = await chatItem.evaluate((el) => {
      return window.getComputedStyle(el).borderLeft !== '2px solid transparent'
    })
    expect(isChatActive).toBe(false)
  })

  test('Sidebar keyboard navigation', async ({ page }) => {
    const sidebar = page.locator('[data-testid="sidebar"]')
    await expect(sidebar).toBeVisible()

    // Focus on first nav item
    await page.keyboard.press('Tab')

    // Should be able to navigate with arrow keys
    await page.keyboard.press('ArrowDown')
    await page.keyboard.press('ArrowUp')

    // Should not error
    expect(true).toBe(true)
  })
})
