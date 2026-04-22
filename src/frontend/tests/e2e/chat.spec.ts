import { test, expect } from '@playwright/test'

test.describe('Chat Panel SSE', () => {
  test('sends message and receives SSE tokens', async ({ page }) => {
    await page.goto('/')
    await page.locator('[data-test="nav-item"][data-tab="chat"]').click()
    await page.waitForSelector('[data-test="chat-input"]', { timeout: 5000 })

    const input = page.locator('[data-test="chat-input"]')
    await input.fill('Hello')
    await page.locator('[data-test="chat-send"]').click()

    const message = page.locator('[data-test="assistant-message"]').first()
    await expect(message).toBeVisible({ timeout: 10000 })
  })

  test('error boundary handles malformed SSE', async ({ page }) => {
    await page.route('/sse/agent-run/*', route => {
      route.abort('failed')
    })
    await page.goto('/')
    await page.locator('[data-test="nav-item"][data-tab="chat"]').click()
    const errorUI = page.locator('[data-test="error-message"]')
    await expect(errorUI).toBeVisible({ timeout: 5000 })
  })
})
