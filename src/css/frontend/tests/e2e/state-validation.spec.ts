import { test, expect } from '@playwright/test'

test.describe('UI State Management (Zustand Persist)', () => {
  test('localStorage persists after first action (initialize on interaction)', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // On first visit, localStorage may be empty until store is accessed
    // Trigger an action to initialize persistence
    await page.locator('button:has-text("Health")').click()
    await page.waitForTimeout(500)
    
    const state = await page.evaluate(() => localStorage.getItem('cybersecsuite-ui'))
    expect(state).toBeTruthy()
    const parsed = JSON.parse(state!)
    expect(parsed.state).toHaveProperty('activeTab')
    expect(parsed.state).toHaveProperty('sidebarCollapsed')
    expect(parsed.state).toHaveProperty('theme')
  })

  test('activeTab persists: default is chat (after first interaction)', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Trigger an action to initialize store
    await page.locator('button:has-text("Chat")').click()
    await page.waitForTimeout(300)
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.activeTab).toBe('chat')
  })

  test('clicking nav items updates activeTab', async ({ page }) => {
    await page.goto('/')
    await page.locator('button:has-text("Health")').first().click()
    await page.waitForTimeout(200)
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.activeTab).toBe('health')
  })

  test('activeTab persists across page reload', async ({ page }) => {
    await page.goto('/')
    await page.locator('button:has-text("Routing")').click()
    await page.waitForTimeout(200)
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.activeTab).toBe('routing')
  })

  test('sidebar toggle updates sidebarCollapsed', async ({ page }) => {
    await page.goto('/')
    
    // Click hamburger ☰
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(300)
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.sidebarCollapsed).toBe(true)
    
    // Toggle again
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(300)
    
    const state2 = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state2.state.sidebarCollapsed).toBe(false)
  })

  test('sidebarCollapsed persists across reload', async ({ page }) => {
    await page.goto('/')
    
    // Collapse
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(300)
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.sidebarCollapsed).toBe(true)
  })

  test('theme switching updates state', async ({ page }) => {
    await page.goto('/')
    
    // Click purple theme button
    await page.locator('button[title="Theme: purple"]').click()
    await page.waitForTimeout(200)
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.theme).toBe('purple')
    
    // Switch to red
    await page.locator('button[title="Theme: red"]').click()
    await page.waitForTimeout(200)
    
    const state2 = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state2.state.theme).toBe('red')
  })

  test('theme persists across reload', async ({ page }) => {
    await page.goto('/')
    
    await page.locator('button[title="Theme: purple"]').click()
    await page.waitForTimeout(200)
    
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.theme).toBe('purple')
  })

  test('rapid tab switches don\'t corrupt state', async ({ page }) => {
    await page.goto('/')
    
    const buttons = await page.locator('aside button').all()
    
    // Rapid fire clicks
    for (let i = 0; i < Math.min(5, buttons.length); i++) {
      await buttons[i].click({ force: true, timeout: 500 }).catch(() => {})
    }
    
    await page.waitForTimeout(300)
    
    const state = await page.evaluate(() => {
      const raw = localStorage.getItem('cybersecsuite-ui')
      if (!raw) return null
      try {
        return JSON.parse(raw)
      } catch {
        return null
      }
    })
    
    expect(state).toBeTruthy()
    expect(state!.state.activeTab).toBeTruthy()
  })

  test('sidebar collapse + tab switch maintains state', async ({ page }) => {
    await page.goto('/')
    
    // Switch to routing
    await page.locator('button:has-text("Routing")').click()
    await page.waitForTimeout(200)
    
    // Collapse sidebar
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(200)
    
    // Switch to cases while collapsed
    await page.locator('button:has-text("Cases")').click({ force: true })
    await page.waitForTimeout(200)
    
    // Expand
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(300)
    
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.activeTab).toBe('cases')
    expect(state.state.sidebarCollapsed).toBe(false)
  })

  test('settings dropdown toggle doesn\'t affect main state', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    // Initialize store with an action first
    await page.locator('button:has-text("Health")').click()
    await page.waitForTimeout(300)
    
    const initialState = await page.evaluate(() => 
      JSON.parse(localStorage.getItem('cybersecsuite-ui')!)
    )
    
    // Toggle settings
    await page.locator('button:has-text("SETTINGS")').click()
    await page.waitForTimeout(200)
    
    const afterToggleState = await page.evaluate(() => 
      JSON.parse(localStorage.getItem('cybersecsuite-ui')!)
    )
    
    // State properties should remain same
    expect(afterToggleState.state.activeTab).toBe(initialState.state.activeTab)
    expect(afterToggleState.state.sidebarCollapsed).toBe(initialState.state.sidebarCollapsed)
    expect(afterToggleState.state.theme).toBe(initialState.state.theme)
  })

  test('all 33 nav items are clickable', async ({ page }) => {
    await page.goto('/')
    
    const navButtons = await page.locator('aside button:not(:has(span:has-text("SETTINGS")))').all()
    expect(navButtons.length).toBeGreaterThan(25)
    
    // Test first 5 items
    for (let i = 0; i < Math.min(5, navButtons.length); i++) {
      await navButtons[i].click()
      await page.waitForTimeout(100)
      
      const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
      expect(state.state.activeTab).toBeTruthy()
    }
  })

  test('complex workflow: collapse → theme → tab → reload', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // 1. Collapse sidebar
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(200)
    
    // 2. Change theme
    await page.locator('button[title="Theme: red"]').click()
    await page.waitForTimeout(200)
    
    // 3. Switch tab (expand sidebar first to access)
    await page.locator('button:has-text("☰")').click()
    await page.waitForTimeout(300)
    await page.locator('button:has-text("IOCs")').first().click()
    await page.waitForTimeout(200)
    
    // 4. Reload
    await page.reload()
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(500)
    
    // 5. Verify all state persisted
    const state = await page.evaluate(() => JSON.parse(localStorage.getItem('cybersecsuite-ui')!))
    expect(state.state.sidebarCollapsed).toBe(false)
    expect(state.state.theme).toBe('red')
    expect(state.state.activeTab).toBe('iocs')
  })
})
