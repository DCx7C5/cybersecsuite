import { test, expect } from '@playwright/test'

test.describe('T093: Navigation Items', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('NavItem renders with label and icon', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    await expect(navItem).toBeVisible()
    
    const label = navItem.locator('text=/Dashboard|Chat|Tables/')
    await expect(label).toBeVisible()
  })

  test('NavItem icon renders with Lucide icon', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    const icon = navItem.locator('[data-testid^="nav-icon-"]')
    await expect(icon).toBeVisible()
    
    const svg = icon.locator('svg')
    await expect(svg).toBeVisible()
  })

  test('NavItem click handler triggers navigation', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-chat"]').first()
    
    await navItem.click()
    await page.waitForLoadState('networkidle')
    
    const currentUrl = page.url()
    expect(currentUrl).toContain('chat')
  })

  test('NavItem active state styling applied', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    
    await navItem.click()
    await page.waitForTimeout(200)
    
    const activeState = await navItem.getAttribute('data-active')
    expect(activeState).toBe('true')
    
    const bgClass = await navItem.getAttribute('class')
    expect(bgClass).toContain('bg-')
  })

  test('NavItem badge displays count correctly', async ({ page }) => {
    const badge = page.locator('[data-testid^="nav-badge-"]').first()
    
    if (await badge.isVisible()) {
      const count = await badge.textContent()
      expect(count).toMatch(/^\d+$/)
      
      const variant = await badge.getAttribute('data-variant')
      expect(['primary', 'danger', 'info']).toContain(variant)
    }
  })

  test('NavItem nested children visibility toggle', async ({ page }) => {
    const parentItem = page.locator('[data-testid="group-toggle-settings"]').first()
    
    if (await parentItem.isVisible()) {
      const isExpanded = await parentItem.getAttribute('aria-expanded')
      expect(['true', 'false']).toContain(isExpanded)
      
      const children = page.locator('[data-testid="group-toggle-settings"] ~ [data-testid^="nav-item-"]')
      if (isExpanded === 'true') {
        const count = await children.count()
        expect(count).toBeGreaterThan(0)
      }
    }
  })

  test('NavItem renders with aria-label', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    const ariaLabel = await navItem.getAttribute('aria-label')
    
    expect(ariaLabel).toBeTruthy()
    expect(ariaLabel).toContain('Navigation item')
  })

  test('NavItem current page indicator for active route', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    await navItem.click()
    await page.waitForTimeout(200)
    
    const ariaCurrent = await navItem.getAttribute('aria-current')
    if (ariaCurrent) {
      expect(ariaCurrent).toBe('page')
    }
  })

  test('NavItem keyboard navigation focus visible', async ({ page }) => {
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    
    await navItem.focus()
    const focused = await navItem.evaluate(el => document.activeElement === el)
    expect(focused).toBe(true)
    
    const outline = await navItem.evaluate(el => 
      window.getComputedStyle(el).outline
    )
    expect(outline).toBeTruthy()
  })

  test('NavItem badge color variant applies styling', async ({ page }) => {
    const badge = page.locator('[data-testid^="nav-badge-danger"]').first()
    
    if (await badge.isVisible()) {
      const classes = await badge.getAttribute('class')
      expect(classes).toMatch(/red|danger|error/)
    }
  })

  test('Multiple NavItems render without interference', async ({ page }) => {
    const navItems = page.locator('[data-testid^="nav-item-"]')
    const count = await navItems.count()
    
    expect(count).toBeGreaterThan(1)
    
    for (let i = 0; i < Math.min(count, 3); i++) {
      const item = navItems.nth(i)
      await expect(item).toBeVisible()
    }
  })
})
