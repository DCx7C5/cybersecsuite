import { test, expect } from '@playwright/test'

test.describe('Error Boundaries', () => {
  test('error boundary catches malformed API response', async ({ page }) => {
    await page.route('/api/**', route => {
      route.abort('failed')
    })
    await page.goto('/')
    const errorUI = page.locator('[data-test="error-boundary"]')
    await expect(errorUI).toBeVisible({ timeout: 5000 })
  })

  test('app recovers after error', async ({ page }) => {
    await page.goto('/')
    await page.route('/api/**', route => {
      route.abort('failed')
    })
    await page.locator('[data-test="nav-item"]').first().click()
    const errorMsg = page.locator('[data-test="error-message"]')
    await expect(errorMsg).toBeVisible({ timeout: 3000 })

    await page.unroute('/api/**')
    await page.reload()
    const content = page.locator('body')
    await expect(content).toBeVisible()
  })
})
