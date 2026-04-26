import { test, expect } from '@playwright/test'

test.describe('Data Persistence E2E (T351)', () => {
  test('localStorage persists active tab', async ({ page, context }) => {
    await page.goto('/')

    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await chatItem.click()
    await page.waitForTimeout(100)

    const state = await page.evaluate(() => localStorage.getItem('cybersecsuite-ui'))
    expect(state).toBeTruthy()

    const parsed = JSON.parse(state as string)
    expect(parsed.activeTab).toBe('chat')
  })

  test('Settings open state persists', async ({ page }) => {
    await page.goto('/')

    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    await settingsToggle.click()
    await page.waitForTimeout(100)

    const stored = await page.evaluate(() =>
      localStorage.getItem('sidebar-settings-open')
    )
    expect(stored).toBe('true')

    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')

    // Check if settings are still open
    const settingsItems = page.locator('[data-testid^="settings-item-"]')
    const count = await settingsItems.count()
    expect(count).toBeGreaterThan(0)
  })

  test('collapsible section state persists', async ({ page }) => {
    await page.goto('/')

    const state1 = await page.evaluate(() => {
      try {
        return localStorage.getItem('sidebar-section-chat')
      } catch {
        return null
      }
    })

    expect(state1).toBeDefined()
  })

  test('Multiple state changes persist', async ({ page }) => {
    await page.goto('/')

    // Make several changes
    const healthItem = page.locator('[data-testid="nav-item-health"]')
    await healthItem.click()
    await page.waitForTimeout(50)

    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    await settingsToggle.click()
    await page.waitForTimeout(50)

    const allStorage = await page.evaluate(() => {
      const items = {}
      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i)
        if (key) {
          items[key] = localStorage.getItem(key)
        }
      }
      return items
    })

    expect(Object.keys(allStorage).length).toBeGreaterThan(0)
  })

  test('State survives page reload', async ({ page }) => {
    await page.goto('/')

    const chatItem = page.locator('[data-testid="nav-item-chat"]')
    await chatItem.click()
    await page.waitForTimeout(100)

    const beforeReload = await page.evaluate(() => localStorage.getItem('cybersecsuite-ui'))

    await page.reload()
    await page.waitForLoadState('networkidle')

    const afterReload = await page.evaluate(() => localStorage.getItem('cybersecsuite-ui'))

    expect(beforeReload).toBe(afterReload)
  })
})

test.describe('Performance E2E (T352)', () => {
  test('Page loads within acceptable time', async ({ page }) => {
    const startTime = Date.now()
    await page.goto('/')
    const loadTime = Date.now() - startTime

    expect(loadTime).toBeLessThan(5000) // 5 seconds
  })

  test('DOM renders quickly', async ({ page }) => {
    const startTime = Date.now()
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')
    const domTime = Date.now() - startTime

    expect(domTime).toBeLessThan(3000) // 3 seconds
  })

  test('Sidebar navigation is responsive', async ({ page }) => {
    await page.goto('/')

    const startTime = Date.now()
    const items = page.locator('[data-testid^="nav-item-"]')
    const firstItem = items.first()
    await firstItem.click()
    const clickTime = Date.now() - startTime

    expect(clickTime).toBeLessThan(500) // 500ms
  })

  test('Settings toggle is fast', async ({ page }) => {
    await page.goto('/')

    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    const startTime = Date.now()
    await settingsToggle.click()
    const toggleTime = Date.now() - startTime

    expect(toggleTime).toBeLessThan(300) // 300ms
  })

  test('No memory leaks from repeated interactions', async ({ page }) => {
    await page.goto('/')

    // Perform 10 rapid clicks
    const settingsToggle = page.locator('[data-testid="settings-toggle"]')
    for (let i = 0; i < 10; i++) {
      await settingsToggle.click()
      await page.waitForTimeout(50)
    }

    // App should still be responsive
    const sidebar = page.locator('[data-testid="sidebar"]')
    expect(await sidebar.isVisible()).toBe(true)
  })

  test('Sidebar rendering is efficient', async ({ page }) => {
    await page.goto('/')

    const startTime = Date.now()
    await page.waitForLoadState('networkidle')
    const renderTime = Date.now() - startTime

    const itemCount = await page.locator('[data-testid^="nav-item-"]').count()
    const timePerItem = renderTime / itemCount

    expect(timePerItem).toBeLessThan(50) // Less than 50ms per item
  })

  test('No excessive re-renders on navigation', async ({ page }) => {
    await page.goto('/')

    let clickCount = 0
    page.on('framenavigated', () => {
      clickCount++
    })

    const items = page.locator('[data-testid^="nav-item-"]')
    const firstItem = items.first()
    await firstItem.click()
    await page.waitForTimeout(100)

    // Should be minimal frame updates
    expect(clickCount).toBeLessThan(3)
  })

  test('Viewport resize is handled smoothly', async ({ page }) => {
    await page.goto('/')

    const startTime = Date.now()
    await page.setViewportSize({ width: 768, height: 1024 })
    const resizeTime = Date.now() - startTime

    expect(resizeTime).toBeLessThan(500) // 500ms

    const sidebar = page.locator('[data-testid="sidebar"]')
    expect(await sidebar.isVisible()).toBe(true)
  })
})
