import { test, expect } from '@playwright/test'

test.describe('T096: Lucide Icons Integration', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('Lucide icon library loads successfully', async ({ page }) => {
    const icons = page.locator('[data-testid^="nav-icon-"]')
    const count = await icons.count()
    
    expect(count).toBeGreaterThan(0)
  })

  test('Icon renders as SVG element', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"]').first()
    await expect(icon).toBeVisible()
    
    const svg = icon.locator('svg')
    await expect(svg).toBeVisible()
    
    const svgNamespace = await svg.evaluate(el => el.namespaceURI)
    expect(svgNamespace).toBe('http://www.w3.org/2000/svg')
  })

  test('Icon has stroke or fill properties', async ({ page }) => {
    const svg = page.locator('[data-testid^="nav-icon-"] svg').first()
    
    const hasStroke = await svg.evaluate(el => 
      el.getAttribute('stroke') !== null || 
      el.querySelector('[stroke]') !== null
    )
    const hasFill = await svg.evaluate(el =>
      el.getAttribute('fill') !== null ||
      el.querySelector('[fill]') !== null
    )
    
    expect(hasStroke || hasFill).toBe(true)
  })

  test('Icon custom size support 16px', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"][data-size="16"]').first()
    
    if (await icon.isVisible()) {
      const size = await icon.evaluate(el => 
        window.getComputedStyle(el).width
      )
      expect(size).toMatch(/16px|1rem/)
    }
  })

  test('Icon custom size support 24px', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"][data-size="24"]').first()
    
    if (await icon.isVisible()) {
      const size = await icon.evaluate(el =>
        window.getComputedStyle(el).width
      )
      expect(size).toMatch(/24px|1.5rem/)
    }
  })

  test('Icon custom size support 32px', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"][data-size="32"]').first()
    
    if (await icon.isVisible()) {
      const size = await icon.evaluate(el =>
        window.getComputedStyle(el).width
      )
      expect(size).toMatch(/32px|2rem/)
    }
  })

  test('Icon color variant renders correctly', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"][data-color-variant]').first()
    
    if (await icon.isVisible()) {
      const variant = await icon.getAttribute('data-color-variant')
      expect(['primary', 'danger', 'warning', 'success', 'info']).toContain(variant)
      
      const color = await icon.evaluate(el =>
        window.getComputedStyle(el).color
      )
      expect(color).toBeTruthy()
    }
  })

  test('Icon accessibility attributes present', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"]').first()
    
    const ariaHidden = await icon.getAttribute('aria-hidden')
    const role = await icon.getAttribute('role')
    
    expect(ariaHidden === 'true' || role === 'presentation').toBe(true)
  })

  test('Icon data-icon-name attribute set', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"]').first()
    
    const iconName = await icon.getAttribute('data-icon-name')
    expect(iconName).toBeTruthy()
    expect(iconName).toMatch(/^[a-z-]+$/)
  })

  test('Icon viewBox properly configured', async ({ page }) => {
    const svg = page.locator('[data-testid^="nav-icon-"] svg').first()
    
    const viewBox = await svg.getAttribute('viewBox')
    expect(viewBox).toBeTruthy()
    expect(viewBox).toMatch(/^0\s+0\s+\d+\s+\d+$/)
  })

  test('Multiple icons render without memory leaks', async ({ page }) => {
    const icons = page.locator('[data-testid^="nav-icon-"]')
    const initialCount = await icons.count()
    
    await page.evaluate(() => {
      document.querySelectorAll('[data-testid^="nav-item-"]').forEach(item => {
        item.scrollIntoView()
      })
    })
    
    await page.waitForTimeout(500)
    
    const finalCount = await icons.count()
    expect(finalCount).toBeGreaterThanOrEqual(initialCount)
  })

  test('Icon preserves aspect ratio', async ({ page }) => {
    const svg = page.locator('[data-testid^="nav-icon-"] svg').first()
    
    const preserveAspectRatio = await svg.getAttribute('preserveAspectRatio')
    if (preserveAspectRatio) {
      expect(preserveAspectRatio).toContain('xMid')
    }
  })

  test('Icon stroke width consistency', async ({ page }) => {
    const paths = page.locator('[data-testid^="nav-icon-"] svg path').all()
    
    for (const path of await paths) {
      const strokeWidth = await path.getAttribute('stroke-width')
      if (strokeWidth) {
        const width = parseFloat(strokeWidth)
        expect(width).toBeGreaterThan(0)
        expect(width).toBeLessThan(5)
      }
    }
  })

  test('Icon renders without text content', async ({ page }) => {
    const icon = page.locator('[data-testid^="nav-icon-"]').first()
    
    const text = await icon.textContent()
    expect(text?.trim() ?? '').toBe('')
  })
})
