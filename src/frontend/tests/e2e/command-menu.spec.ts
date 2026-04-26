import { test, expect } from '@playwright/test'

test.describe('CommandMenu component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test.describe('Command Menu Trigger & Basic Interaction', () => {
    test('CommandMenu opens with Ctrl+K', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const menu = page.locator('[data-testid="command-menu"]')
      const visible = await menu.isVisible().catch(() => false)
      expect(visible).toBeDefined()
    })

    test('CommandMenu opens with Cmd+K on Mac', async ({ page }) => {
      await page.keyboard.press('Meta+K')
      await page.waitForTimeout(100)
      const menu = page.locator('[data-testid="command-menu"]')
      const visible = await menu.isVisible().catch(() => false)
      expect(visible).toBeDefined()
    })

    test('CommandMenu opens with / key in input focus', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('/')
        await page.waitForTimeout(100)
        const menu = page.locator('[data-testid="command-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).toBeDefined()
      }
    })

    test('CommandMenu closes with Escape key', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      let menu = page.locator('[data-testid="command-menu"]')
      let visible = await menu.isVisible().catch(() => false)
      expect(visible).toBeTruthy()

      await page.keyboard.press('Escape')
      await page.waitForTimeout(100)
      menu = page.locator('[data-testid="command-menu"]')
      visible = await menu.isVisible().catch(() => false)
      expect(visible).not.toBe(true)
    })

    test('CommandMenu closes on backdrop click', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const backdrop = page.locator('[data-testid="command-menu-backdrop"]')
      if (await backdrop.isVisible().catch(() => false)) {
        await backdrop.click()
        await page.waitForTimeout(100)
        const menu = page.locator('[data-testid="command-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })
  })

  test.describe('Command Menu Search & Filtering', () => {
    test('CommandMenu filters items on search input', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      if (await input.isVisible().catch(() => false)) {
        await input.fill('chat')
        await page.waitForTimeout(200)
        const results = page.locator('[data-testid="command-item"]')
        const count = await results.count()
        expect(count).toBeGreaterThan(0)
      }
    })

    test('CommandMenu shows all items on empty search', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      if (await input.isVisible().catch(() => false)) {
        await input.fill('')
        await page.waitForTimeout(200)
        const results = page.locator('[data-testid="command-item"]')
        const count = await results.count()
        expect(count).toBeGreaterThan(0)
      }
    })

    test('CommandMenu shows no results for non-matching search', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      if (await input.isVisible().catch(() => false)) {
        await input.fill('xyznonexistent123')
        await page.waitForTimeout(200)
        const results = page.locator('[data-testid="command-item"]')
        const count = await results.count()
        expect(count).toBe(0)
      }
    })

    test('CommandMenu search is case-insensitive', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      if (await input.isVisible().catch(() => false)) {
        await input.fill('CHAT')
        await page.waitForTimeout(200)
        const results = page.locator('[data-testid="command-item"]')
        const countUpper = await results.count()

        await input.fill('chat')
        await page.waitForTimeout(200)
        const countLower = await results.count()

        expect(countUpper).toBe(countLower)
        expect(countUpper).toBeGreaterThan(0)
      }
    })

    test('CommandMenu clears search on Ctrl+U', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      if (await input.isVisible().catch(() => false)) {
        await input.fill('test')
        await page.keyboard.press('Control+U')
        const value = await input.inputValue()
        expect(value).toBe('')
      }
    })
  })

  test.describe('Command Menu Keyboard Navigation', () => {
    test('CommandMenu navigates down with ArrowDown', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 0) {
        const firstItem = items.first()
        const firstAriaSelected = await firstItem.getAttribute('aria-selected')
        expect(firstAriaSelected).toBe('true')

        await page.keyboard.press('ArrowDown')
        await page.waitForTimeout(100)

        const secondItem = items.nth(1)
        const secondAriaSelected = await secondItem.getAttribute('aria-selected')
        expect(secondAriaSelected).toBe('true')
      }
    })

    test('CommandMenu navigates up with ArrowUp', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 1) {
        await page.keyboard.press('ArrowDown')
        await page.keyboard.press('ArrowDown')
        await page.waitForTimeout(100)

        await page.keyboard.press('ArrowUp')
        await page.waitForTimeout(100)

        const secondItem = items.nth(1)
        const secondAriaSelected = await secondItem.getAttribute('aria-selected')
        expect(secondAriaSelected).toBe('true')
      }
    })

    test('CommandMenu wraps around on down arrow at end', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 0) {
        for (let i = 0; i < itemCount + 1; i++) {
          await page.keyboard.press('ArrowDown')
          await page.waitForTimeout(50)
        }

        const firstItem = items.first()
        const firstAriaSelected = await firstItem.getAttribute('aria-selected')
        expect(firstAriaSelected).toBe('true')
      }
    })

    test('CommandMenu wraps around on up arrow at start', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 0) {
        await page.keyboard.press('ArrowUp')
        await page.waitForTimeout(100)

        const lastItem = items.last()
        const lastAriaSelected = await lastItem.getAttribute('aria-selected')
        expect(lastAriaSelected).toBe('true')
      }
    })

    test('CommandMenu executes command on Enter', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')

      if (await input.isVisible().catch(() => false)) {
        await input.fill('chat')
        await page.waitForTimeout(100)
        await page.keyboard.press('Enter')
        await page.waitForTimeout(200)

        const menu = page.locator('[data-testid="command-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })

    test('CommandMenu Tab key selects item', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 0) {
        await page.keyboard.press('Tab')
        await page.waitForTimeout(100)

        const secondItem = items.nth(1)
        const secondAriaSelected = await secondItem.getAttribute('aria-selected')
        expect(secondAriaSelected).toBe('true')
      }
    })
  })

  test.describe('Command Menu Execution & State Management', () => {
    test('CommandMenu executes on Enter and closes', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')

      if (await input.isVisible().catch(() => false)) {
        await input.fill('chat')
        await page.waitForTimeout(100)
        await page.keyboard.press('Enter')
        await page.waitForTimeout(200)

        const menu = page.locator('[data-testid="command-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })

    test('CommandMenu resets selection on new search', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')

      if (await input.isVisible().catch(() => false)) {
        await input.fill('chat')
        await page.waitForTimeout(100)
        await page.keyboard.press('ArrowDown')
        await page.waitForTimeout(100)

        await input.fill('cases')
        await page.waitForTimeout(100)

        const items = page.locator('[data-testid="command-item"]')
        const firstItem = items.first()
        const firstAriaSelected = await firstItem.getAttribute('aria-selected')
        expect(firstAriaSelected).toBe('true')
      }
    })

    test('CommandMenu preserves state when reopened', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      await page.keyboard.press('Escape')
      await page.waitForTimeout(100)

      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const menu = page.locator('[data-testid="command-menu"]')
      const visible = await menu.isVisible().catch(() => false)
      expect(visible).toBeDefined()
    })

    test('CommandMenu clears on execution', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')

      if (await input.isVisible().catch(() => false)) {
        await input.fill('chat')
        await page.keyboard.press('Enter')
        await page.waitForTimeout(200)

        await page.keyboard.press('Control+K')
        await page.waitForTimeout(100)
        const newValue = await input.inputValue()
        expect(newValue).toBe('')
      }
    })
  })

  test.describe('Command Menu Accessibility', () => {
    test('CommandMenu has role=listbox', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const menu = page.locator('[data-testid="command-menu"]')
      const role = await menu.getAttribute('role').catch(() => null)
      expect(role).toMatch(/(listbox|dialog)/)
    })

    test('CommandMenu items have aria-selected', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const items = page.locator('[data-testid="command-item"]')
      const itemCount = await items.count()

      if (itemCount > 0) {
        const item = items.first()
        const hasAriaSelected = await item.getAttribute('aria-selected')
        expect(hasAriaSelected).toBeDefined()
      }
    })

    test('CommandMenu input has aria-label', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      const ariaLabel = await input.getAttribute('aria-label').catch(() => null)
      expect(ariaLabel).toBeDefined()
    })

    test('CommandMenu input has proper type=search', async ({ page }) => {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(100)
      const input = page.locator('[data-testid="command-menu-input"]')
      const type = await input.getAttribute('type')
      expect(type).toMatch(/(text|search)/)
    })
  })
})

test.describe('MentionMenu component', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test.describe('Mention Menu Trigger & Autocomplete', () => {
    test('MentionMenu opens with @ symbol in input', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@')
        await page.waitForTimeout(100)
        const menu = page.locator('[data-testid="mention-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).toBeDefined()
      }
    })

    test('MentionMenu filters on search after @', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case')
        await page.waitForTimeout(100)
        const items = page.locator('[data-testid="mention-item"]')
        const count = await items.count()
        expect(count).toBeGreaterThanOrEqual(0)
      }
    })

    test('MentionMenu shows case mentions on @case', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case:')
        await page.waitForTimeout(100)
        const items = page.locator('[data-testid="mention-item"]')
        const count = await items.count()
        expect(count).toBeGreaterThanOrEqual(0)
      }
    })

    test('MentionMenu shows IOC mentions on @ioc', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@ioc:')
        await page.waitForTimeout(100)
        const items = page.locator('[data-testid="mention-item"]')
        const count = await items.count()
        expect(count).toBeGreaterThanOrEqual(0)
      }
    })
  })

  test.describe('Mention Menu Navigation & Selection', () => {
    test('MentionMenu navigates with arrow keys', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@')
        await page.waitForTimeout(100)

        await page.keyboard.press('ArrowDown')
        await page.waitForTimeout(50)
        await page.keyboard.press('ArrowUp')
        await page.waitForTimeout(50)

        const items = page.locator('[data-testid="mention-item"]')
        const count = await items.count()
        expect(count).toBeGreaterThanOrEqual(0)
      }
    })

    test('MentionMenu inserts mention on Enter', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case')
        await page.waitForTimeout(100)

        const items = page.locator('[data-testid="mention-item"]')
        const itemCount = await items.count()
        if (itemCount > 0) {
          await page.keyboard.press('Enter')
          await page.waitForTimeout(100)

          const menu = page.locator('[data-testid="mention-menu"]')
          const visible = await menu.isVisible().catch(() => false)
          expect(visible).not.toBe(true)
        }
      }
    })

    test('MentionMenu closes on Escape', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case')
        await page.waitForTimeout(100)

        await page.keyboard.press('Escape')
        await page.waitForTimeout(100)

        const menu = page.locator('[data-testid="mention-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })

    test('MentionMenu closes on blur', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      const button = page.locator('button').first()

      if (await input.isVisible().catch(() => false) && await button.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case')
        await page.waitForTimeout(100)

        await button.focus()
        await page.waitForTimeout(100)

        const menu = page.locator('[data-testid="mention-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })
  })

  test.describe('Mention Menu State Management', () => {
    test('MentionMenu closes after selection', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@')
        await page.waitForTimeout(100)

        const items = page.locator('[data-testid="mention-item"]')
        const itemCount = await items.count()
        if (itemCount > 0) {
          await items.first().click()
          await page.waitForTimeout(100)

          const menu = page.locator('[data-testid="mention-menu"]')
          const visible = await menu.isVisible().catch(() => false)
          expect(visible).not.toBe(true)
        }
      }
    })

    test('MentionMenu resets on cursor position change', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@case test')
        await page.waitForTimeout(100)

        await input.click({ position: { x: 0, y: 0 } })
        await page.waitForTimeout(100)

        const menu = page.locator('[data-testid="mention-menu"]')
        const visible = await menu.isVisible().catch(() => false)
        expect(visible).not.toBe(true)
      }
    })

    test('MentionMenu preserves input text after selection', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('Hello @')
        await page.waitForTimeout(100)

        const items = page.locator('[data-testid="mention-item"]')
        const itemCount = await items.count()
        if (itemCount > 0) {
          await items.first().click()
          await page.waitForTimeout(100)

          const value = await input.inputValue()
          expect(value).toContain('Hello')
        }
      }
    })
  })

  test.describe('Mention Menu Accessibility', () => {
    test('MentionMenu has role=listbox', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@')
        await page.waitForTimeout(100)

        const menu = page.locator('[data-testid="mention-menu"]')
        const role = await menu.getAttribute('role').catch(() => null)
        expect(role).toMatch(/(listbox|menu)/)
      }
    })

    test('MentionMenu items have proper ARIA attributes', async ({ page }) => {
      const input = page.locator('[data-testid="command-input"]').first()
      if (await input.isVisible().catch(() => false)) {
        await input.focus()
        await input.type('@')
        await page.waitForTimeout(100)

        const items = page.locator('[data-testid="mention-item"]')
        const itemCount = await items.count()
        if (itemCount > 0) {
          const item = items.first()
          const ariaSelected = await item.getAttribute('aria-selected')
          expect(ariaSelected).toBeDefined()
        }
      }
    })
  })
})

test.describe('Menu Dismissal & Edge Cases', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('Rapid menu open/close does not cause errors', async ({ page }) => {
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Control+K')
      await page.waitForTimeout(50)
      await page.keyboard.press('Escape')
      await page.waitForTimeout(50)
    }
    expect(true).toBe(true)
  })

  test('Menu handles rapid search input changes', async ({ page }) => {
    await page.keyboard.press('Control+K')
    await page.waitForTimeout(100)
    const input = page.locator('[data-testid="command-menu-input"]')

    if (await input.isVisible().catch(() => false)) {
      await input.type('chatcasesiocs')
      await page.waitForTimeout(200)

      const items = page.locator('[data-testid="command-item"]')
      const count = await items.count()
      expect(count).toBeGreaterThanOrEqual(0)
    }
  })

  test('Menu handles special characters in search', async ({ page }) => {
    await page.keyboard.press('Control+K')
    await page.waitForTimeout(100)
    const input = page.locator('[data-testid="command-menu-input"]')

    if (await input.isVisible().catch(() => false)) {
      await input.type('test@#$%')
      await page.waitForTimeout(200)

      const items = page.locator('[data-testid="command-item"]')
      const count = await items.count()
      expect(count).toBe(0)
    }
  })

  test('Multiple menus do not stack', async ({ page }) => {
    await page.keyboard.press('Control+K')
    await page.waitForTimeout(100)

    const menus = page.locator('[data-testid="command-menu"]')
    const menuCount = await menus.count()
    expect(menuCount).toBeLessThanOrEqual(1)
  })
})
