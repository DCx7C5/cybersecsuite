# Sidebar Strategy & Architecture Documentation

**Phase 8C-9 | sidebar-strategy-docs**  
**Created:** 2026-04-27  
**Status:** ✅ Complete

---

## Overview

The sidebar component is the primary navigation interface for CyberSecSuite frontend. It provides:
- Collapsible navigation groups with hierarchical organization
- Quick-access settings and configuration
- State persistence via localStorage
- Full keyboard accessibility and shortcuts
- Responsive design with icon-based indicators

---

## Core Architecture

### Component Hierarchy

```
Sidebar (layout)
├── NavGroup
│   ├── NavItem (with icon)
│   └── NavSubItem (nested)
├── SettingsGroup
│   ├── SettingItem
│   └── SettingCheckbox
└── SearchBar (optional)
```

### State Management

**Local State:**
- Collapsed groups: `Map<groupId, boolean>`
- Selected item: `{groupId, itemId}`
- Search filter: `string`

**Persistent State (localStorage):**
- `sidebar:collapsed-groups` — JSON array of group IDs
- `sidebar:last-selected` — Last active nav item
- `sidebar:search-query` — Search filter state (if applicable)

**Global State (optional DataProvider):**
- User preferences for sidebar width
- Theme-specific sidebar styling
- Menu animation preferences

---

## Navigation Item Architecture

### NavItem Component Contract

```typescript
interface NavItem {
  id: string
  label: string
  icon: LucideIcon
  href?: string
  onClick?: () => void
  badge?: {
    count: number
    variant: 'primary' | 'danger' | 'info'
  }
  children?: NavItem[]
  testId?: string
}
```

### Item Rendering Rules

1. **Icon Rendering:** All items use Lucide icons
2. **Badge Logic:** Display count with color-coded variants
3. **Nesting:** Max 2 levels deep
4. **Active State:** Applied via `data-active` attribute and CSS class
5. **Accessibility:** aria-labels and semantic HTML

---

## Test Coverage Strategy

### T093: Navigation Items Test Suite
- Focus: NavItem rendering, click handlers, badge display
- Icon rendering with Lucide
- Click event propagation
- Active state styling
- Badge count display with variants
- Nested item visibility

### T096: Lucide Icons Integration Test
- Focus: Icon imports, rendering, custom sizing
- Icon library loading
- Icon prop validation
- Custom size support (16px, 24px, 32px)
- Icon color variants
- SVG accessibility

### T109: E2E Router Tests
- Focus: Navigation routing, deep linking, history management
- Click nav item → route change
- URL parameters persistence
- Browser back/forward navigation
- Deep link restoration
- Hash routing support

---

## Component Patterns & Guidelines

### Naming Conventions

- Components: PascalCase
- Hooks: camelCase with use prefix
- Constants: UPPER_SNAKE_CASE
- test IDs: kebab-case

### Data Attributes for Testing

```html
<a data-testid="nav-item-{id}" data-active="{true|false}">
<span data-testid="nav-icon-{id}" data-icon-name="{lucideName}">
<span data-testid="nav-badge-{id}" data-variant="{variant}">
<button data-testid="group-toggle-{id}" aria-expanded="{true|false}">
```

### Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Alt+B | Toggle sidebar |
| ↑/↓ | Navigate items |
| ← | Collapse group |
| → | Expand group |
| Enter | Select item |
| Escape | Close sidebar |

---

## State Cleanup & Lifecycle (T160)

**Initialization Phase:**
1. Load collapsed groups from localStorage
2. Restore last selected item
3. Apply theme-specific styling
4. Initialize keyboard listeners

**Runtime Phase:**
1. Track active route and update selected item
2. Persist group state on toggle
3. Debounce search queries (300ms)

**Cleanup Phase:**
1. Remove event listeners on component unmount
2. Clear selection state if navigating away
3. Save dirty state (if using DataProvider)
4. Reset animations in progress

---

## Integration Points

### DataProvider Context (T114 - Optional)

```typescript
interface SidebarContextType {
  collapsedGroups: Set<string>
  selectedItem: {groupId: string; itemId: string} | null
  toggleGroup: (groupId: string) => void
  selectItem: (groupId: string, itemId: string) => void
  isMobile: boolean
}

export const useSidebar = () => {
  const context = useContext(SidebarContext)
  if (!context) throw new Error('useSidebar must be used within SidebarProvider')
  return context
}
```

---

## Accessibility Compliance

**WCAG 2.1 Level AA**

✅ Keyboard Navigation (arrows, Enter, Escape, focus management)
✅ Screen Reader Support (ARIA labels, semantic HTML)
✅ Visual Accessibility (3:1 contrast, icon+text, visible focus)

---

## References

- Component: `src/frontend/src/components/layout/Sidebar.tsx`
- Hooks: `src/frontend/src/hooks/useKeyboardShortcuts.ts`
- Tests: `src/frontend/tests/e2e/sidebar.spec.ts`
- Styles: `src/frontend/src/index.css`
