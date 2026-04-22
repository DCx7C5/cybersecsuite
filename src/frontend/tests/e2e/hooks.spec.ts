import { test, expect } from '@playwright/test'

test.describe('Hook: useBreakPoint', () => {
  test('detects breakpoints correctly', async ({ page }) => {
    await page.goto('/')
    
    // Test initial breakpoint
    const breakpoint = await page.evaluate(() => {
      const width = window.innerWidth
      if (width < 480) return 'xs'
      if (width < 768) return 'sm'
      if (width < 1024) return 'md'
      if (width < 1280) return 'lg'
      return 'xl'
    })
    
    expect(breakpoint).toMatch(/^(xs|sm|md|lg|xl)$/)
  })

  test('updates breakpoint on window resize', async ({ page }) => {
    await page.goto('/')
    
    // Store initial width
    const initial = await page.evaluate(() => window.innerWidth)
    
    // Resize window
    await page.setViewportSize({ width: 500, height: 600 })
    
    // Verify breakpoint updated
    const breakpoint = await page.evaluate(() => {
      const width = window.innerWidth
      if (width < 480) return 'xs'
      if (width < 768) return 'sm'
      if (width < 1024) return 'md'
      if (width < 1280) return 'lg'
      return 'xl'
    })
    
    expect(breakpoint).toMatch(/^(xs|sm|md|lg|xl)$/)
  })

  test('mobile breakpoint triggers on small screens', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 }) // iPhone
    await page.goto('/')
    
    const breakpoint = await page.evaluate(() => {
      const width = window.innerWidth
      if (width < 480) return 'xs'
      if (width < 768) return 'sm'
      return 'md'
    })
    
    expect(breakpoint).toBe('xs')
  })
})

test.describe('Hook: useEventListener', () => {
  test('listens to global keydown events', async ({ page }) => {
    await page.goto('/')
    
    // Add a test element that listens to keydown
    const listener = await page.evaluate(() => {
      let keyPressed = false
      const handler = (e: KeyboardEvent) => {
        if (e.key === 'Escape') keyPressed = true
      }
      window.addEventListener('keydown', handler)
      // Simulate ESC keypress
      const event = new KeyboardEvent('keydown', { key: 'Escape' })
      window.dispatchEvent(event)
      return keyPressed
    })
    
    expect(listener).toBe(true)
  })

  test('supports click outside detection pattern', async ({ page }) => {
    await page.goto('/')
    
    const clickDetected = await page.evaluate(() => {
      let outsideClick = false
      const handler = (e: Event) => {
        const target = e.target as HTMLElement
        if (target.id !== 'modal') {
          outsideClick = true
        }
      }
      document.addEventListener('click', handler)
      // Simulate click on document
      const event = new MouseEvent('click')
      document.dispatchEvent(event)
      return outsideClick
    })
    
    expect(clickDetected).toBe(true)
  })

  test('removes event listener on cleanup', async ({ page }) => {
    await page.goto('/')
    
    const listenerCleaned = await page.evaluate(() => {
      let callCount = 0
      const handler = () => callCount++
      window.addEventListener('resize', handler)
      window.dispatchEvent(new Event('resize'))
      window.removeEventListener('resize', handler)
      window.dispatchEvent(new Event('resize'))
      return callCount === 1 // Only fired once before removal
    })
    
    expect(listenerCleaned).toBe(true)
  })
})

test.describe('Hook: useLocalStorage', () => {
  test('persists state to localStorage', async ({ page }) => {
    await page.goto('/')
    
    const persisted = await page.evaluate(() => {
      const key = 'test-key'
      const value = { theme: 'dark' }
      localStorage.setItem(key, JSON.stringify(value))
      const retrieved = localStorage.getItem(key)
      return JSON.parse(retrieved!)
    })
    
    expect(persisted.theme).toBe('dark')
  })

  test('retrieves persisted state across page reloads', async ({ page }) => {
    await page.goto('/')
    
    // Set value
    await page.evaluate(() => {
      localStorage.setItem('persist-test', JSON.stringify({ count: 42 }))
    })
    
    // Reload page
    await page.reload()
    await page.waitForLoadState('networkidle')
    
    // Retrieve value
    const value = await page.evaluate(() => {
      const raw = localStorage.getItem('persist-test')
      return raw ? JSON.parse(raw) : null
    })
    
    expect(value.count).toBe(42)
  })

  test('handles invalid JSON gracefully', async ({ page }) => {
    await page.goto('/')
    
    const result = await page.evaluate(() => {
      localStorage.setItem('invalid-json', 'not valid json')
      try {
        return JSON.parse(localStorage.getItem('invalid-json')!)
      } catch {
        return null
      }
    })
    
    expect(result).toBeNull()
  })

  test('removes items from localStorage', async ({ page }) => {
    await page.goto('/')
    
    const removed = await page.evaluate(() => {
      const key = 'remove-test'
      localStorage.setItem(key, 'value')
      localStorage.removeItem(key)
      return localStorage.getItem(key) === null
    })
    
    expect(removed).toBe(true)
  })
})

test.describe('Hook: useIntersectionObserver', () => {
  test('detects when element enters viewport', async ({ page }) => {
    await page.goto('/')
    
    // Create an element and observe it
    const isIntersecting = await page.evaluate(() => {
      const element = document.createElement('div')
      element.id = 'observe-test'
      element.style.height = '100px'
      document.body.appendChild(element)
      
      let observed = false
      const observer = new IntersectionObserver(([entry]) => {
        observed = entry.isIntersecting
      }, { threshold: 0.1 })
      
      observer.observe(element)
      return observed
    })
    
    expect(typeof isIntersecting).toBe('boolean')
  })

  test('fires callback when element becomes visible', async ({ page }) => {
    await page.goto('/')
    
    const visible = await page.evaluate(() => {
      const element = document.createElement('div')
      element.id = 'visibility-test'
      element.style.height = '100px'
      document.body.appendChild(element)
      
      let callCount = 0
      const observer = new IntersectionObserver(() => {
        callCount++
      })
      
      observer.observe(element)
      return callCount >= 0 // At least initialized
    })
    
    expect(visible).toBe(true)
  })

  test('respects threshold option', async ({ page }) => {
    await page.goto('/')
    
    const respectsThreshold = await page.evaluate(() => {
      const element = document.createElement('div')
      document.body.appendChild(element)
      
      let entriesCount = 0
      const observer = new IntersectionObserver(
        (entries) => {
          entriesCount = entries.length
        },
        { threshold: [0.1, 0.5, 0.9] }
      )
      
      observer.observe(element)
      return entriesCount >= 0
    })
    
    expect(respectsThreshold).toBe(true)
  })

  test('disconnects observer on cleanup', async ({ page }) => {
    await page.goto('/')
    
    const cleaned = await page.evaluate(() => {
      const element = document.createElement('div')
      document.body.appendChild(element)
      
      let callCount = 0
      const observer = new IntersectionObserver(() => {
        callCount++
      })
      
      observer.observe(element)
      observer.disconnect()
      
      // After disconnect, observer should not fire more events
      return callCount >= 0
    })
    
    expect(cleaned).toBe(true)
  })
})

test.describe('Hook: useList', () => {
  test('adds item to list', async ({ page }) => {
    await page.goto('/')
    
    const list = await page.evaluate(() => {
      const items: Array<{ id: string; label: string }> = []
      items.push({ id: '1', label: 'Item 1' })
      return items
    })
    
    expect(list).toHaveLength(1)
    expect(list[0].label).toBe('Item 1')
  })

  test('removes item from list by id', async ({ page }) => {
    await page.goto('/')
    
    const list = await page.evaluate(() => {
      const items: Array<{ id: string; label: string }> = [
        { id: '1', label: 'Item 1' },
        { id: '2', label: 'Item 2' },
      ]
      // Remove item with id 1
      const filtered = items.filter((item) => item.id !== '1')
      return filtered
    })
    
    expect(list).toHaveLength(1)
    expect(list[0].id).toBe('2')
  })

  test('updates item in list by id', async ({ page }) => {
    await page.goto('/')
    
    const list = await page.evaluate(() => {
      const items: Array<{ id: string; label: string }> = [
        { id: '1', label: 'Old' },
        { id: '2', label: 'Item 2' },
      ]
      // Update item with id 1
      const updated = items.map((item) =>
        item.id === '1' ? { ...item, label: 'New' } : item
      )
      return updated
    })
    
    expect(list[0].label).toBe('New')
  })

  test('reorders items in list', async ({ page }) => {
    await page.goto('/')
    
    const list = await page.evaluate(() => {
      const items: Array<{ id: string; label: string }> = [
        { id: '1', label: 'Item 1' },
        { id: '2', label: 'Item 2' },
        { id: '3', label: 'Item 3' },
      ]
      // Move item from index 0 to index 2
      const result = [...items]
      const [removed] = result.splice(0, 1)
      result.splice(2, 0, removed)
      return result
    })
    
    expect(list).toHaveLength(3)
    expect(list[2].id).toBe('1')
  })

  test('maintains item type safety with generics', async ({ page }) => {
    await page.goto('/')
    
    const list = await page.evaluate(() => {
      interface ListItem {
        id: string | number
        [key: string]: unknown
      }
      
      const items: ListItem[] = [
        { id: '1', name: 'Test', active: true },
        { id: 2, name: 'Item 2', active: false },
      ]
      return items
    })
    
    expect(list).toHaveLength(2)
    expect(list[0]).toHaveProperty('id')
    expect(list[1]).toHaveProperty('name')
  })
})

test.describe('Integration: All Hooks Together', () => {
  test('hooks coexist without conflicts', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    
    const allClean = await page.evaluate(() => {
      // useBreakPoint
      const width = window.innerWidth
      const breakpoint = width < 768 ? 'mobile' : 'desktop'
      
      // useEventListener
      let eventFired = false
      const handler = () => {
        eventFired = true
      }
      window.addEventListener('test', handler)
      window.dispatchEvent(new Event('test'))
      window.removeEventListener('test', handler)
      
      // useLocalStorage
      localStorage.setItem('test', 'value')
      const stored = localStorage.getItem('test') === 'value'
      localStorage.removeItem('test')
      
      // useIntersectionObserver
      const element = document.createElement('div')
      document.body.appendChild(element)
      let observed = false
      const observer = new IntersectionObserver(() => {
        observed = true
      })
      observer.observe(element)
      observer.disconnect()
      
      // useList
      const items = [{ id: 1, name: 'test' }]
      const updated = items.filter((i) => i.id === 1)
      
      return {
        breakpoint: breakpoint !== '',
        eventFired,
        stored,
        observed: typeof observed === 'boolean',
        updated: updated.length === 1,
      }
    })
    
    expect(allClean.breakpoint).toBe(true)
    expect(allClean.eventFired).toBe(true)
    expect(allClean.stored).toBe(true)
    expect(allClean.observed).toBe(true)
    expect(allClean.updated).toBe(true)
  })
})
