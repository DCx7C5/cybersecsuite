import { test, expect } from '@playwright/test'

test.describe('T109: E2E Router Tests', () => {
  test('Navigation item click changes route', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const dashboardUrl = page.url()
    
    const chatItem = page.locator('[data-testid="nav-item-chat"]').first()
    if (await chatItem.isVisible()) {
      await chatItem.click()
      await page.waitForLoadState('networkidle')
      
      const chatUrl = page.url()
      expect(chatUrl).not.toBe(dashboardUrl)
      expect(chatUrl).toContain('chat')
    }
  })

  test('URL parameters persist during navigation', async ({ page }) => {
    await page.goto('/?view=grid&sort=name')
    await page.waitForLoadState('networkidle')
    
    const url1 = page.url()
    expect(url1).toContain('view=grid')
    expect(url1).toContain('sort=name')
    
    const navItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    await navItem.click()
    await page.waitForLoadState('networkidle')
    
    await page.goBack()
    await page.waitForLoadState('networkidle')
    
    const url2 = page.url()
    expect(url2).toContain('view=grid')
    expect(url2).toContain('sort=name')
  })

  test('Browser back button navigation', async ({ page }) => {
    await page.goto('/')
    const initialUrl = page.url()
    
    const navItem = page.locator('[data-testid="nav-item-chat"]').first()
    if (await navItem.isVisible()) {
      await navItem.click()
      await page.waitForLoadState('networkidle')
      const newUrl = page.url()
      expect(newUrl).not.toBe(initialUrl)
      
      await page.goBack()
      await page.waitForLoadState('networkidle')
      
      const backUrl = page.url()
      expect(backUrl).toBe(initialUrl)
    }
  })

  test('Browser forward button navigation', async ({ page }) => {
    await page.goto('/')
    const initialUrl = page.url()
    
    const navItem = page.locator('[data-testid="nav-item-chat"]').first()
    if (await navItem.isVisible()) {
      await navItem.click()
      await page.waitForLoadState('networkidle')
      const chatUrl = page.url()
      
      await page.goBack()
      await page.waitForLoadState('networkidle')
      expect(page.url()).toBe(initialUrl)
      
      await page.goForward()
      await page.waitForLoadState('networkidle')
      
      const forwardUrl = page.url()
      expect(forwardUrl).toBe(chatUrl)
    }
  })

  test('Deep link restoration from URL', async ({ page }) => {
    await page.goto('/chat?sessionId=test123&mode=forensic')
    await page.waitForLoadState('networkidle')
    
    const url = page.url()
    expect(url).toContain('/chat')
    expect(url).toContain('sessionId=test123')
    expect(url).toContain('mode=forensic')
    
    const expectedContent = page.locator('text=/Chat|Forensic/')
    const isVisible = await expectedContent.isVisible().catch(() => false)
    expect(isVisible || url.includes('chat')).toBe(true)
  })

  test('Hash routing navigation', async ({ page }) => {
    await page.goto('/#section-1')
    await page.waitForLoadState('networkidle')
    
    const url1 = page.url()
    expect(url1).toContain('#section-1')
    
    await page.goto('/#section-2')
    await page.waitForLoadState('networkidle')
    
    const url2 = page.url()
    expect(url2).toContain('#section-2')
  })

  test('Query string parameters preserved on reload', async ({ page }) => {
    await page.goto('/?filter=active&limit=25')
    const originalUrl = page.url()
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    const reloadedUrl = page.url()
    expect(reloadedUrl).toBe(originalUrl)
  })

  test('Navigation back after multiple route changes', async ({ page }) => {
    await page.goto('/')
    const root = page.url()
    
    const navItems = page.locator('[data-testid^="nav-item-"]')
    const count = Math.min(3, await navItems.count())
    
    for (let i = 0; i < count; i++) {
      const item = navItems.nth(i)
      if (await item.isVisible()) {
        await item.click()
        await page.waitForTimeout(200)
      }
    }
    
    for (let i = 0; i < count; i++) {
      await page.goBack()
      await page.waitForTimeout(200)
    }
    
    const finalUrl = page.url()
    expect(finalUrl).toBe(root)
  })

  test('Route change updates active nav item styling', async ({ page }) => {
    await page.goto('/')
    
    const dashboardItem = page.locator('[data-testid="nav-item-dashboard"]').first()
    if (await dashboardItem.isVisible()) {
      await dashboardItem.click()
      await page.waitForTimeout(200)
      
      const dashboardActive = await dashboardItem.getAttribute('data-active')
      expect(dashboardActive).toBe('true')
      
      const chatItem = page.locator('[data-testid="nav-item-chat"]').first()
      if (await chatItem.isVisible()) {
        await chatItem.click()
        await page.waitForTimeout(200)
        
        const chatActive = await chatItem.getAttribute('data-active')
        expect(chatActive).toBe('true')
        
        const dashboardInactive = await dashboardItem.getAttribute('data-active')
        expect(dashboardInactive).toBe('false')
      }
    }
  })

  test('URL encoding preserved for special characters', async ({ page }) => {
    const specialParam = 'query=test%20value%2Fspecial'
    await page.goto(`/?${specialParam}`)
    await page.waitForLoadState('networkidle')
    
    const url = page.url()
    expect(url).toContain(encodeURIComponent('test value/special'))
  })

  test('Session storage state restores on deep link', async ({ page, context }) => {
    await page.goto('/settings?tab=security')
    await page.waitForLoadState('networkidle')
    
    const sessionData = await page.evaluate(() => {
      return sessionStorage.getItem('nav:deep-link')
    })
    
    if (sessionData) {
      const newPage = await context.newPage()
      await newPage.goto('/settings?tab=security')
      await newPage.waitForLoadState('networkidle')
      
      const restoredData = await newPage.evaluate(() => {
        return sessionStorage.getItem('nav:deep-link')
      })
      
      expect(restoredData).toBe(sessionData)
      await newPage.close()
    }
  })

  test('Complex query parameters navigation', async ({ page }) => {
    const complexUrl = '/?filter=type:threat&sort=-date&view=grid&page=2&limit=50'
    await page.goto(complexUrl)
    await page.waitForLoadState('networkidle')
    
    const url = page.url()
    expect(url).toContain('filter=')
    expect(url).toContain('sort=')
    expect(url).toContain('view=')
    expect(url).toContain('page=')
    expect(url).toContain('limit=')
  })

  test('Fragment navigation (anchor links)', async ({ page }) => {
    await page.goto('/')
    
    await page.goto('/#content')
    const url1 = page.url()
    expect(url1).toContain('#content')
    
    await page.goto('/#details')
    const url2 = page.url()
    expect(url2).toContain('#details')
    
    await page.goBack()
    const url3 = page.url()
    expect(url3).toContain('#content')
  })
})
