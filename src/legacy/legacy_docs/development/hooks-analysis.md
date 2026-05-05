# React Hooks Analysis: AHS Admin Panel → CyberSecSuite

**Date:** 2026-04-26  
**Status:** Reference analysis for Phase 7C/7D implementation

## Overview

Reviewed 25 hooks from AHS Admin Panel frontend. Identified **8 high-priority hooks** for CyberSecSuite, categorized by implementation phase and use case.

---

## 🎯 High-Priority Hooks (Recommended for Implementation)

### Tier 1: Critical for Phase 7C (Sidebar UX + Responsive Design)

#### 1. **useStorage** / **useLocalStorage**
**Priority:** ⭐⭐⭐⭐⭐  
**Status:** Partially reimplemented (Zustand persist middleware)  
**Use case:** Collapsible section state, favorites, user preferences

```typescript
// Better than Zustand for simple storage without full state machine
const [favorites, setFavorites, removeFavorites] = useLocalStorage('favorites', [])
```

**Why reimplied:**
- Already handled by Zustand `persist` middleware
- But useful for lightweight state (search history, quick toggles, panel sizes)

**Implementation:** Ready to use (8 lines TypeScript)

---

#### 2. **useBreakPoint** (Responsive Design)
**Priority:** ⭐⭐⭐⭐⭐  
**Status:** Not in CyberSecSuite  
**Use case:** T088 (Responsive sidebar behavior)

```typescript
const screenSize = useBreakPoint() // 'xs' | 'sm' | 'md' | 'lg' | 'xl'

// In Sidebar.tsx:
return screenSize === 'xs' ? <MobileNav /> : <DesktopNav />
```

**Why needed:**
- Sidebar should collapse on mobile (<768px)
- Send Message prompt positioning differs by breakpoint
- Solves T088 directly

**Implementation:** ~30 lines, no dependencies

---

#### 3. **useEventListener**
**Priority:** ⭐⭐⭐⭐⭐  
**Status:** Not in CyberSecSuite  
**Use case:** Global keyboard shortcuts (⌘K search), click-outside detection

```typescript
// In T078 (Search sidebar):
useEventListener('keydown', (e) => {
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    setSearchOpen(true)
  }
})
```

**Why needed:**
- ⌘K search pattern (T078) requires global event listener
- Close dropdowns on outside click
- Prevents memory leaks (removes listeners on unmount)

**Implementation:** ~30 lines, uses refs for callback stability

---

#### 4. **useIntersectionObserver**
**Priority:** ⭐⭐⭐⭐  
**Status:** Not in CyberSecSuite  
**Use case:** Lazy loading panels, infinite scroll in search results

```typescript
// In Chat panel when it's off-screen:
const isVisible = useIntersectionObserver(chatRef)
// Only fetch messages when visible
```

**Why needed:**
- 33 panels should lazy-load when first visible (performance)
- Follows React Router lazy() pattern (T106)

**Implementation:** ~25 lines, browser native API

---

### Tier 2: Useful for Phase 7D (React Router) + Advanced Features

#### 5. **useList** (Array State Management)
**Priority:** ⭐⭐⭐⭐  
**Status:** Not in CyberSecSuite  
**Use case:** T076 (Favorites/pinning), T079 (Workspace context breadcrumb), T099 (Live badges)

```typescript
// Manage favorite items with add/remove/reorder
const [favorites, { addItem, removeItem, reorderItems }] = useList([])

// Drag-to-reorder favorites:
const favoriteId = 'iocs'
removeItem(favoriteId)
addItem({ id: favoriteId, label: 'IOCs' })
```

**Why needed:**
- Favorites system (T076) requires add/remove/reorder operations
- Type-safe list operations with callbacks
- Clean API for both UI and localStorage

**Implementation:** ~50 lines, fully generic

---

#### 6. **useAsync** (Promise State Management)
**Priority:** ⭐⭐⭐⭐  
**Status:** Partially (useApiQuery exists, but useAsync is more general)  
**Use case:** T076–T080 (Dynamic badge counts, A2A status polling)

```typescript
// Poll A2A task status every 5 seconds
const { loading, error, value: taskStatus } = useAsync(
  () => fetch('/api/a2a-status').then(r => r.json()),
  [taskStatus]
)

// Render badge: {taskStatus?.pending_count}
```

**Why needed:**
- More flexible than React Query for simple polling
- Handles loading/error/value states cleanly
- Useful for live badges (T077, T099)

**Implementation:** ~25 lines, good alternative to useQuery

---

#### 7. **useDragResizeHeight** (Panel Resizing)
**Priority:** ⭐⭐⭐  
**Status:** Not in CyberSecSuite  
**Use case:** T079 (Workspace context breadcrumb), collapsible panel sizing

```typescript
// Make sidebar resizable by dragging
const { onMouseDown } = useDragResizeHeight(
  sidebarRef,
  (height) => setSidebarHeight(height),
  (height) => setStoredHeight(height) // Persist
)

// In JSX:
<div ref={sidebarRef} onMouseDown={onMouseDown} style={{ cursor: 'row-resize' }} />
```

**Why needed:**
- Users can resize sidebar/panels by dragging
- Persists to localStorage between sessions
- Solves UX polish (nice-to-have)

**Implementation:** ~60 lines, composable with useEventListener

---

### Tier 3: Not Recommended (Pre-existing alternatives in CyberSecSuite)

#### ❌ useApiFetch
**Status:** SKIP — CyberSecSuite uses React Query (better)  
**Reason:** useApiQuery is more powerful, handles caching/deduplication

#### ❌ useAuthentication
**Status:** SKIP — Uses backend auth (Flask-Login)  
**Reason:** Auth state managed server-side, not frontend

#### ❌ useTimeout
**Status:** SKIP — Use native setTimeout + useEffect  
**Reason:** Zustand can manage delays cleanly

---

## 📋 Implementation Roadmap

### Phase 7C (Sidebar UX) — T070–T100
Add to `/src/frontend/src/hooks/`:
1. ✅ useBreakPoint.ts (Priority 1) — needed for T088
2. ✅ useEventListener.ts (Priority 1) — needed for T078 (⌘K search)
3. ✅ useLocalStorage.ts (Priority 1) — needed for favorites/quick toggles
4. ✅ useIntersectionObserver.ts (Priority 2) — needed for lazy panel loading

**Time:** ~2 hours (write + test + integrate)

### Phase 7D (React Router) — T101–T110
Use new hooks in:
1. Sidebar.tsx — useBreakPoint for mobile collapse
2. Search.tsx — useEventListener for ⌘K
3. PanelWrapper.tsx — useIntersectionObserver for lazy load
4. CollapsibleSection.tsx — useLocalStorage for toggle state

**Time:** ~1 hour (integration only)

### Phase 1 (QoL Core) — T002–T015
Unrelated (different focus)

---

## Code Examples

### Example 1: Responsive Sidebar with useBreakPoint
```typescript
// src/frontend/src/components/layout/Sidebar.tsx
import { useBreakPoint } from '../hooks/useBreakPoint'

export function Sidebar() {
  const screenSize = useBreakPoint()
  const [isCollapsed, setIsCollapsed] = useUIStore(state => [state.sidebarCollapsed, state.setSidebarCollapsed])
  
  // Auto-collapse on mobile
  useEffect(() => {
    if (screenSize === 'xs' || screenSize === 'sm') {
      setIsCollapsed(true)
    }
  }, [screenSize])
  
  return (
    <nav className={isCollapsed ? 'collapsed' : 'expanded'}>
      {/* ... */}
    </nav>
  )
}
```

### Example 2: ⌘K Search with useEventListener
```typescript
// src/frontend/src/components/layout/SearchBar.tsx
import { useEventListener } from '../hooks/useEventListener'

export function SearchBar() {
  const [isOpen, setIsOpen] = useState(false)
  
  useEventListener('keydown', (e: Event) => {
    const ke = e as KeyboardEvent
    if ((ke.metaKey || ke.ctrlKey) && ke.key === 'k') {
      ke.preventDefault()
      setIsOpen(!isOpen)
    }
  })
  
  return (
    <>
      <input 
        placeholder="Search (⌘K)"
        value={isOpen ? '' : ''}
      />
      {/* Search results */}
    </>
  )
}
```

### Example 3: Favorites with useList + useLocalStorage
```typescript
// src/frontend/src/hooks/useFavorites.ts
import { useList } from './useList'
import { useLocalStorage } from './useLocalStorage'

export function useFavorites() {
  const [stored, setStored] = useLocalStorage('favorites', [])
  const [favorites, ops] = useList(stored)
  
  useEffect(() => {
    setStored(favorites) // Persist on change
  }, [favorites])
  
  return { favorites, ...ops }
}

// In Sidebar:
const { favorites, addItem, removeItem } = useFavorites()
// Show favorites at top of sidebar
```

### Example 4: Lazy-load Panels with useIntersectionObserver
```typescript
// src/frontend/src/components/PanelWrapper.tsx
import { useIntersectionObserver } from '../hooks/useIntersectionObserver'

export function LazyPanel({ PanelComponent, panelId }) {
  const ref = useRef<HTMLDivElement>(null)
  const isVisible = useIntersectionObserver(ref)
  const [loaded, setLoaded] = useState(false)
  
  useEffect(() => {
    if (isVisible && !loaded) {
      setLoaded(true) // Trigger lazy load
    }
  }, [isVisible])
  
  return (
    <div ref={ref}>
      {loaded ? <PanelComponent /> : <Spinner />}
    </div>
  )
}
```

---

## Integration Checklist

- [ ] Copy hooks to `src/frontend/src/hooks/`
- [ ] Update `src/frontend/src/hooks/index.ts` with exports
- [ ] Write unit tests for each hook (~50 lines per hook)
- [ ] Update `docs/development/frontend.md` with hook usage guide
- [ ] Integrate into Phase 7C components (T070–T075)
- [ ] Verify with Playwright E2E tests (T091–T100)

---

## Test Requirements

Each hook must have Playwright tests:

1. **useBreakPoint**: Test screen resize, verify state updates
2. **useEventListener**: Test ⌘K press, verify search opens
3. **useLocalStorage**: Test localStorage persistence
4. **useIntersectionObserver**: Test viewport visibility detection
5. **useList**: Test add/remove/reorder operations
6. **useAsync**: Test loading/error/value states

---

## Risk Assessment

| Hook | Risk | Mitigation |
|------|------|-----------|
| useBreakPoint | Resize spam | Debounce on resize event |
| useEventListener | Memory leaks | Always remove listener on unmount ✅ |
| useLocalStorage | Quota exceeded | Handle QuotaExceededError |
| useIntersectionObserver | Performance | Set `threshold: 0.1` to reduce callbacks |
| useList | Reconciliation bugs | Test with React DevTools |
| useAsync | Race conditions | Implement AbortController in T101–T108 |

---

## Decision Log

**Why not use zustand-persist everywhere?**
- Zustand is great for large state machines (activeTab, theme)
- But lightweight hooks are better for simple key-value pairs (favorites, search history)
- useLocalStorage + useList provides better ergonomics

**Why not use React Query for polling?**
- React Query is designed for server data (caching, deduplication)
- useAsync is simpler for client-side polling (A2A status, badges)
- Can coexist: React Query for data, useAsync for status

**Why useBreakPoint instead of Tailwind CSS?**
- Tailwind handles styling breakpoints (great!)
- But useBreakPoint handles behavior breakpoints (mobile collapse, conditional UI)
- Both work well together

---

## References

- Source: `/home/daen/Projects/ahs-admin-panel/frontend/js/hooks/`
- React 19 best practices: Use `use()` for promise unwrapping (not applicable here, but noted)
- TypeScript strict mode: All hooks are fully typed
