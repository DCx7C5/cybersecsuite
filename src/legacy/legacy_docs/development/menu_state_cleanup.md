# Menu State & Cleanup Lifecycle

**Phase 8C-9 | T160**  
**Created:** 2026-04-27  
**Status:** ✅ Complete

---

## Overview

Proper state cleanup and lifecycle management prevents memory leaks, event listener accumulation, and stale closures. This document outlines the complete lifecycle for sidebar, menu, and navigation components.

---

## Component Lifecycle Phases

### 1. Initialization Phase

**On Component Mount:**

```typescript
useEffect(() => {
  // 1a. Load persistent state from localStorage
  const collapsedGroups = JSON.parse(
    localStorage.getItem('sidebar:collapsed-groups') ?? '[]'
  )
  const lastSelected = JSON.parse(
    localStorage.getItem('sidebar:last-selected') ?? 'null'
  )
  
  // 1b. Restore UI state
  setCollapsedGroups(new Set(collapsedGroups))
  setSelectedItem(lastSelected)
  
  // 1c. Apply theme-specific styling
  if (isDarkMode) {
    document.documentElement.classList.add('dark')
  }
  
  // 1d. Initialize keyboard listeners
  document.addEventListener('keydown', handleKeydown)
  window.addEventListener('resize', handleResize)
  
  // Cleanup function (see 3. Cleanup Phase)
  return () => {
    document.removeEventListener('keydown', handleKeydown)
    window.removeEventListener('resize', handleResize)
  }
}, [])
```

---

### 2. Runtime Phase

**State Updates During User Interaction:**

```typescript
// 2a. Track active route and sync sidebar
useEffect(() => {
  const currentPath = location.pathname
  
  // Find matching nav item and update selection
  const matching = navItems.find(item => item.path === currentPath)
  if (matching) {
    setSelectedItem({ groupId: matching.group, itemId: matching.id })
  }
}, [location.pathname])

// 2b. Persist group state on toggle (debounced)
const handleGroupToggle = useCallback((groupId: string) => {
  const newCollapsed = new Set(collapsedGroups)
  newCollapsed.has(groupId) ? newCollapsed.delete(groupId) : newCollapsed.add(groupId)
  
  setCollapsedGroups(newCollapsed)
  
  // Debounce persistence
  clearTimeout(persistenceTimer)
  persistenceTimer = setTimeout(() => {
    localStorage.setItem(
      'sidebar:collapsed-groups',
      JSON.stringify(Array.from(newCollapsed))
    )
  }, 500)
}, [collapsedGroups])

// 2c. Debounce search queries
const handleSearch = useCallback((query: string) => {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    setSearchQuery(query)
  }, 300)
}, [])
```

---

### 3. Cleanup Phase

**On Component Unmount:**

```typescript
useEffect(() => {
  return () => {
    // 3a. Remove event listeners
    document.removeEventListener('keydown', handleKeydown)
    window.removeEventListener('resize', handleResize)
    window.removeEventListener('popstate', handlePopstate)
    
    // 3b. Clear debounce timers
    clearTimeout(persistenceTimer)
    clearTimeout(searchTimer)
    clearTimeout(debounceTimer)
    
    // 3c. Clear animation frames
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId)
    }
    
    // 3d. Save dirty state
    if (hasDirtyState) {
      localStorage.setItem('sidebar:collapsed-groups', JSON.stringify(collapsedGroups))
      localStorage.setItem('sidebar:last-selected', JSON.stringify(selectedItem))
    }
    
    // 3e. Reset animations in progress
    if (isAnimating) {
      setIsAnimating(false)
    }
    
    // 3f. Close any open menus
    setMenuOpen(false)
    
    // 3g. Clear subscriptions
    unsubscribeFromStore?.()
  }
}, [])
```

---

## Memory Leak Prevention

### Event Listeners

```typescript
// ❌ BAD: Event listener leak
useEffect(() => {
  window.addEventListener('resize', handleResize)
  // Missing cleanup! Listener accumulates on every mount.
}, [])

// ✅ GOOD: Proper cleanup
useEffect(() => {
  const handler = () => { /* ... */ }
  window.addEventListener('resize', handler)
  
  return () => {
    window.removeEventListener('resize', handler)
  }
}, [])
```

### Timers

```typescript
// ❌ BAD: Timer leak
useEffect(() => {
  const timer = setTimeout(() => {
    setData(newData)
  }, 1000)
  // Missing cleanup! Timer runs after unmount.
}, [])

// ✅ GOOD: Clear timer on unmount
useEffect(() => {
  const timer = setTimeout(() => {
    setData(newData)
  }, 1000)
  
  return () => clearTimeout(timer)
}, [])
```

### Subscriptions

```typescript
// ✅ GOOD: Unsubscribe on cleanup
useEffect(() => {
  const subscription = observable.subscribe(value => {
    setState(value)
  })
  
  return () => subscription.unsubscribe()
}, [])
```

---

## Stale Closure Prevention

### Capturing Current Value

```typescript
// ❌ BAD: Stale closure
const [count, setCount] = useState(0)

useEffect(() => {
  const timer = setInterval(() => {
    console.log(count) // Always logs 0 (stale)
  }, 1000)
  
  return () => clearInterval(timer)
}, []) // Missing count dependency

// ✅ GOOD: useRef for non-reactive value
const countRef = useRef(count)

useEffect(() => {
  countRef.current = count
}, [count])

useEffect(() => {
  const timer = setInterval(() => {
    console.log(countRef.current) // Current value
  }, 1000)
  
  return () => clearInterval(timer)
}, [])

// ✅ GOOD: Proper dependency
useEffect(() => {
  const timer = setInterval(() => {
    console.log(count)
  }, 1000)
  
  return () => clearInterval(timer)
}, [count]) // Include count
```

---

## State Management Cleanup Checklist

### On Component Mount

- [ ] Load persistent state from localStorage
- [ ] Restore last selected item
- [ ] Apply theme styling
- [ ] Initialize keyboard event listeners
- [ ] Register window resize listeners
- [ ] Subscribe to global state (if using Redux/Zustand)
- [ ] Set up navigation observers
- [ ] Initialize animation frame for smooth transitions

### During Runtime

- [ ] Track location changes and update active item
- [ ] Debounce search queries (300ms)
- [ ] Persist state changes to localStorage (500ms debounce)
- [ ] Manage animation states
- [ ] Handle keyboard shortcuts
- [ ] Update menu focus on arrow keys

### On Component Unmount

- [ ] Remove all event listeners (keydown, resize, popstate, etc.)
- [ ] Clear all timers and intervals
- [ ] Cancel animation frames
- [ ] Unsubscribe from observables
- [ ] Save final state to localStorage
- [ ] Reset animation flags
- [ ] Close open menus
- [ ] Clear debounce/throttle timers

---

## Example: Complete Sidebar Lifecycle

```typescript
import { useEffect, useState, useRef, useCallback } from 'react'

export const Sidebar: React.FC<SidebarProps> = ({ navItems }) => {
  // State
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set())
  const [selectedItem, setSelectedItem] = useState<Item | null>(null)
  const [isAnimating, setIsAnimating] = useState(false)
  const [isMobile, setIsMobile] = useState(false)

  // Refs for cleanup
  const persistenceTimerRef = useRef<NodeJS.Timeout>()
  const searchTimerRef = useRef<NodeJS.Timeout>()
  const animationFrameRef = useRef<number>()

  // ========== INITIALIZATION ==========
  useEffect(() => {
    // Load persistent state
    const stored = localStorage.getItem('sidebar:collapsed-groups')
    const parsed = stored ? JSON.parse(stored) : []
    setCollapsedGroups(new Set(parsed))

    // Initialize resize listener
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768)
    }
    window.addEventListener('resize', handleResize)
    handleResize()

    // Initialize keyboard listener
    const handleKeydown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === 'b') {
        e.preventDefault()
        // Toggle sidebar
      }
    }
    document.addEventListener('keydown', handleKeydown)

    // ========== CLEANUP ==========
    return () => {
      window.removeEventListener('resize', handleResize)
      document.removeEventListener('keydown', handleKeydown)
      
      clearTimeout(persistenceTimerRef.current)
      clearTimeout(searchTimerRef.current)
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [])

  // ========== RUNTIME: Track route changes ==========
  useEffect(() => {
    const currentPath = location.pathname
    const matching = navItems.find(item => item.path === currentPath)
    if (matching) {
      setSelectedItem(matching)
    }
  }, [location.pathname, navItems])

  // ========== EVENT HANDLERS ==========
  const handleGroupToggle = useCallback((groupId: string) => {
    setIsAnimating(true)
    
    const newCollapsed = new Set(collapsedGroups)
    newCollapsed.has(groupId) 
      ? newCollapsed.delete(groupId) 
      : newCollapsed.add(groupId)
    
    setCollapsedGroups(newCollapsed)

    // Debounce persistence
    clearTimeout(persistenceTimerRef.current)
    persistenceTimerRef.current = setTimeout(() => {
      localStorage.setItem(
        'sidebar:collapsed-groups',
        JSON.stringify(Array.from(newCollapsed))
      )
      setIsAnimating(false)
    }, 300)
  }, [collapsedGroups])

  return (
    <nav data-testid="sidebar" className="sidebar">
      {navItems.map(item => (
        <button
          key={item.id}
          data-testid={`group-toggle-${item.id}`}
          aria-expanded={!collapsedGroups.has(item.id)}
          onClick={() => handleGroupToggle(item.id)}
        >
          {item.label}
        </button>
      ))}
    </nav>
  )
}
```

---

## Performance Optimization

### Debouncing

```typescript
// Debounce persistence (500ms)
const debounceRef = useRef<NodeJS.Timeout>()

const persistState = useCallback(() => {
  clearTimeout(debounceRef.current)
  debounceRef.current = setTimeout(() => {
    localStorage.setItem('state', JSON.stringify(state))
  }, 500)
}, [state])
```

### Throttling

```typescript
// Throttle resize handler (100ms)
const throttleRef = useRef<number | null>(null)

const handleResize = () => {
  if (throttleRef.current) return
  
  // Execute
  doSomething()
  
  throttleRef.current = window.setTimeout(() => {
    throttleRef.current = null
  }, 100)
}

window.addEventListener('resize', handleResize)
```

---

## Testing State Cleanup

```typescript
import { render, screen, waitFor } from '@testing-library/react'
import { vi } from 'vitest'

test('cleanup removes event listeners', async () => {
  const removeEventListenerSpy = vi.spyOn(window, 'removeEventListener')
  
  const { unmount } = render(<Sidebar />)
  
  unmount()
  
  await waitFor(() => {
    expect(removeEventListenerSpy).toHaveBeenCalledWith('resize', expect.any(Function))
    expect(removeEventListenerSpy).toHaveBeenCalledWith('keydown', expect.any(Function))
  })
  
  removeEventListenerSpy.mockRestore()
})

test('cleanup clears timers', async () => {
  const clearTimeoutSpy = vi.spyOn(global, 'clearTimeout')
  
  const { unmount } = render(<Sidebar />)
  
  unmount()
  
  await waitFor(() => {
    expect(clearTimeoutSpy).toHaveBeenCalled()
  })
  
  clearTimeoutSpy.mockRestore()
})
```

---

## Troubleshooting

### Warning: Can't perform a React state update on an unmounted component

**Cause:** Setting state after unmount (common in async handlers)

**Solution:**
```typescript
useEffect(() => {
  let isMounted = true
  
  fetchData().then(data => {
    if (isMounted) {
      setData(data)
    }
  })
  
  return () => {
    isMounted = false
  }
}, [])
```

### Memory Leak: Event listeners accumulate

**Cause:** Missing cleanup function in useEffect

**Solution:** Always return cleanup function that removes listener

### Stale Closure in event handlers

**Cause:** Dependency array missing required variables

**Solution:** Include all dependencies or use useRef for non-reactive values

---

## Summary

✅ Always cleanup on unmount  
✅ Remove event listeners  
✅ Clear timers and intervals  
✅ Cancel animation frames  
✅ Unsubscribe from observables  
✅ Test cleanup with vitest + React Testing Library  
✅ Use useRef for non-reactive values that need current reference  
✅ Use debounce/throttle for high-frequency events  

---

## References

- Component Lifecycle: `src/frontend/src/components/layout/Sidebar.tsx`
- Hooks: `src/frontend/src/hooks/`
- DataProvider: `src/frontend/src/store/DataProvider.tsx`
- Tests: `src/frontend/tests/e2e/`
