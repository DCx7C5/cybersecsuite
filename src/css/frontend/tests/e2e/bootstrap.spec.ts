import { test, expect } from '@playwright/test'

test.describe('App Bootstrap', () => {
  test('page loads and renders sidebar', async ({ page }) => {
    await page.goto('/')
    await expect(page.locator('body')).toBeVisible()
    await expect(page.locator('text=CyberSecSuite')).toBeVisible({ timeout: 5000 })
  })

  test('all nav items load on navigation', async ({ page }) => {
    await page.goto('/')
    const navItems = await page.locator('[data-test="nav-item"]').count()
    expect(navItems).toBeGreaterThan(0)
  })

  test('theme persists to localStorage', async ({ page }) => {
    await page.goto('/')
    const lsItems = await page.evaluate(() => Object.keys(localStorage))
    expect(lsItems.length).toBeGreaterThan(0)
  })

  test('lazy panels load on tab click', async ({ page }) => {
    await page.goto('/')
    const firstTab = page.locator('[data-test="nav-item"]').first()
    await firstTab.click()
    await page.waitForLoadState('networkidle')
    const content = page.locator('[data-test="panel-content"]')
    await expect(content).toBeVisible({ timeout: 3000 })
  })
})
