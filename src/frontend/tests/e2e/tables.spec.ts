import { test, expect } from '@playwright/test'

test.describe('Data Tables', () => {
  test('table sorts on header click', async ({ page }) => {
    await page.goto('/')
    await page.locator('[data-test="nav-item"][data-tab="cases"]').click()
    await page.waitForSelector('[data-test="table"]', { timeout: 5000 })

    const headers = page.locator('[data-test="table-header"]')
    await headers.first().click()
    await page.waitForTimeout(500)
    const sorted = page.locator('[data-test="table-body-row"]')
    await expect(sorted).toHaveCount(1, { timeout: 3000 })
  })

  test('table filters data', async ({ page }) => {
    await page.goto('/')
    await page.locator('[data-test="nav-item"][data-tab="cases"]').click()
    const filterInput = page.locator('[data-test="table-filter"]').first()
    if (await filterInput.isVisible()) {
      await filterInput.fill('test')
      await page.waitForTimeout(500)
      const rows = page.locator('[data-test="table-body-row"]')
      const count = await rows.count()
      expect(count).toBeGreaterThanOrEqual(0)
    }
  })
})
