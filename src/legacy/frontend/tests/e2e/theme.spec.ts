import { test, expect } from '@playwright/test'

test.describe('Theme Switching', () => {
  test('switches between 3 themes and persists to localStorage', async ({ page }) => {
    await page.goto('/')
    const themes = ['blue', 'purple', 'red']

    for (const theme of themes) {
      await page.locator('[data-test="theme-switcher"]').click()
      await page.locator(`[data-test="theme-${theme}"]`).click()
      await page.waitForTimeout(300)

      const bodyClass = await page.locator('body').getAttribute('class')
      expect(bodyClass).toContain(`theme-${theme}`)

      const lsTheme = await page.evaluate(() => localStorage.getItem('theme'))
      expect(lsTheme).toBe(theme)
    }
  })

  test('theme persists across page reload', async ({ page }) => {
    await page.goto('/')
    await page.locator('[data-test="theme-switcher"]').click()
    await page.locator('[data-test="theme-purple"]').click()
    await page.reload()

    const bodyClass = await page.locator('body').getAttribute('class')
    expect(bodyClass).toContain('theme-purple')
  })
})
