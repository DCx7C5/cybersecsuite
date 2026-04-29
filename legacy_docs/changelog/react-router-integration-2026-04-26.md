# React Router Integration (2026-04-26)

**Status:** Planned for Phase 7D (T101–T110)  
**Effort:** 4–5 hours  
**React Version:** Strict 19.2.5 + React Router v7

## Motivation

Current frontend uses Zustand `activeTab` state for navigation. This approach:
- ✗ Breaks browser back/forward buttons
- ✗ No deep linking (can't share "Cases panel" via URL)
- ✗ State lost on page reload (unless stored in localStorage)
- ✗ Violates web platform expectations

React Router v7 enables:
- ✅ URL-driven navigation (?tab=cases, ?tab=iocs&case=42)
- ✅ Browser back/forward buttons work intuitively
- ✅ Deep linking (share specific panel + context)
- ✅ SEO-friendly URLs
- ✅ Lazy route loading for 33 panels
- ✅ Aligns with React 19 + TanStack ecosystem

## Implementation Plan (T101–T110)

### T101: Install React Router v7
- Add `react-router-dom@7` to package.json
- Run `npm install`
- Verify React 19.2.5 compatibility
- **Test:** `npm run dev` starts without errors

### T102: Create Router Configuration
```typescript
// src/frontend/src/router/index.ts
export const router = createBrowserRouter([
  {
    path: '/',
    element: <RootLayout />,
    children: [
      { path: '?tab=chat', element: <Suspense><ChatPanel /></Suspense> },
      { path: '?tab=health', element: <Suspense><HealthPanel /></Suspense> },
      // ... 33 panels
    ],
  },
])
```
- Use `React.lazy()` for all 33 panels
- Define route boundaries with Suspense
- **Test:** Router initializes, root path loads

### T103: Convert activeTab → URL Params
- Replace `useUIStore()` in App.tsx with `useLocation()`
- Extract `tab` param: `const tab = new URLSearchParams(location.search).get('tab') || 'chat'`
- Update Zustand store (activeTab still exists, but sourced from URL)
- **Test:** Navigating to `?tab=health` loads Health panel

### T104: Update Sidebar Navigation
```typescript
// Instead of: onClick={() => setActiveTab('cases')}
// Use: <Link to="?tab=cases">Cases</Link>
```
- Replace all nav item clicks with `<Link>` components
- Highlight active link based on URL
- **Test:** Clicking nav items updates URL and panel

### T105: Update Topbar Breadcrumb
- Use `useLocation()` to extract current panel
- Display dynamic breadcrumb from URL params
- Show context (e.g., "FORENSICS / IOCs" from ?tab=iocs)
- **Test:** Breadcrumb updates when navigating

### T106: Lazy Route Loading
- All 33 panel components use `React.lazy()`
- Router code-splits each panel ~2–6 kB chunk
- Show Spinner during lazy load
- **Test:** Panels load on demand, spinner displays on slow network

### T107: Browser Back/Forward Support
- Test back button from Chat → Health → Chat
- Verify forward button returns to Health
- **Test:** Navigation history works correctly

### T108: Deep Linking & State Restoration
```
URLs:
- /app?tab=chat → Chat panel
- /app?tab=iocs&case=42 → IOCs panel, Case #42 selected
- /app?tab=opensearch&query=APT-28 → OpenObserve, search pre-filled
```
- Parse URL params to restore context
- **Test:** Sharing deep link loads correct panel + state

### T109: Update E2E Tests
- Convert tab click tests to URL navigation tests
- Test all 33 routes routable via URL
- Test back/forward buttons
- Test deep linking
- **Playwright:** 15+ new tests covering router

### T110: Document Router Setup
Add to `docs/development/frontend.md`:
```markdown
## React Router v7 Architecture

### URL Schemes
- `/app?tab=<panelId>` — navigate to panel
- `/app?tab=<panelId>&context=<value>` — deep link with state

### Migration from activeTab
Old: `setActiveTab('cases')`
New: `navigate('?tab=cases')`

### Lazy Loading
All 33 panels lazy-loaded. First panel (chat) eager-loaded.

### Browser Buttons
Back/forward buttons supported. Deep links shareable.
```

## Strict React 19 Practices (Already in Use)

- ✅ `React 19.2.5` (strict, no 18.x)
- ✅ `createRoot()` (not ReactDOM.render)
- ✅ React Compiler compatible (uses memo granularly)
- ✅ Suspense + lazy() for code splitting
- ✅ `useTransition()` for non-blocking updates
- ✅ React 19 actions pattern ready (for forms)

## Testing Requirements

**All T101–T110 must pass Playwright:**
- Router initializes on page load
- URL changes on navigation
- Deep links restore context
- Back/forward buttons work
- All 33 panels routable
- Lazy loading displays spinner

## Risk Assessment

**Low Risk:** React Router v7 is stable, widely adopted  
**Integration Risk:** activeTab → URL migration straightforward  
**Testing:** Requires 15+ new E2E tests (covered by T109)

## Timeline

- **T101:** 30 min (install)
- **T102:** 1 hour (router config)
- **T103:** 1 hour (activeTab → URL migration)
- **T104–T105:** 1 hour (sidebar + topbar)
- **T106–T108:** 1.5 hours (lazy loading, deep links)
- **T109:** 1 hour (tests)
- **T110:** 30 min (docs)

**Total:** 4–5 hours

---

## Related PRs / Commits

- Phase 7C (Sidebar UX) — will depend on Phase 7D for routing
- docs/development/frontend.md — will be updated with router guide
- tests/e2e/router.spec.ts — new test file for router verification
