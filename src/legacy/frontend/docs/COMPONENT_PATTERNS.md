# Frontend Component Patterns & Best Practices

**Phase 8C-9 | T117**  
**Created:** 2026-04-27  
**Status:** ✅ Complete

---

## Table of Contents

1. [Component Structure](#component-structure)
2. [Naming Conventions](#naming-conventions)
3. [TypeScript Patterns](#typescript-patterns)
4. [Hook Patterns](#hook-patterns)
5. [Testing Patterns](#testing-patterns)
6. [Accessibility Patterns](#accessibility-patterns)
7. [Performance Patterns](#performance-patterns)
8. [State Management](#state-management)

---

## Component Structure

### Directory Layout

```
src/
├── components/
│   ├── ui/                    # Reusable UI components
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   └── Badge.tsx
│   ├── layout/                # Layout components
│   │   ├── Sidebar.tsx
│   │   └── Header.tsx
│   └── shared/                # Shared components
│       ├── Modal.tsx
│       └── Toast.tsx
├── hooks/                     # Custom React hooks
│   ├── useApi.ts
│   ├── useLocation.ts
│   └── useKeyboardShortcuts.ts
├── utils/                     # Utility functions
└── store/                     # Global state (if Redux/Zustand)
```

### File Naming Rules

- **Components:** `PascalCase.tsx` (e.g., `Button.tsx`, `SidebarNav.tsx`)
- **Hooks:** `camelCase.ts` (e.g., `useApi.ts`, `useLocation.ts`)
- **Tests:** `{Name}.test.ts` or `{Name}.spec.ts`
- **Types:** `types.ts` or inline in component file
- **Styles:** `{Name}.css` or CSS modules `{Name}.module.css`

---

## Naming Conventions

### Component Props

```typescript
// ✅ Descriptive, semantic naming
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'danger'
  size: 'sm' | 'md' | 'lg'
  isLoading?: boolean
  isDisabled?: boolean
  onClick?: () => void
}

// ❌ Avoid unclear abbreviations
interface BtnProps {
  type: 'p' | 's' | 'd'
  sz: 'S' | 'M' | 'L'
}
```

### Hook Names

```typescript
// ✅ Hooks start with "use"
export const useApi = (url: string) => { ... }
export const useSidebarState = () => { ... }
export const useDebounce = (value: T, delay: number) => { ... }

// ❌ Avoid non-hook naming
export const fetchApi = (url: string) => { ... }
```

### Test IDs

```html
<!-- ✅ Kebab-case, descriptive -->
<button data-testid="sidebar-toggle-menu">Menu</button>
<span data-testid="nav-item-dashboard">Dashboard</span>
<div data-testid="user-settings-panel">

<!-- ❌ Avoid unclear IDs -->
<button data-testid="btn1">Menu</button>
<span data-testid="item">Dashboard</span>
```

---

## TypeScript Patterns

### Props Interface Pattern

```typescript
import { ReactNode } from 'react'

export interface CardProps {
  // UI props
  className?: string
  variant?: 'default' | 'elevated' | 'outlined'
  
  // Content props
  title?: string
  children: ReactNode
  
  // Behavior props
  onClick?: () => void
  onClose?: () => void
  
  // State props
  isLoading?: boolean
  isDisabled?: boolean
  error?: Error
}

export const Card: React.FC<CardProps> = ({
  className,
  variant = 'default',
  title,
  children,
  onClick,
  onClose,
  isLoading = false,
  isDisabled = false,
  error
}) => {
  return (
    <div className={`card card--${variant} ${className ?? ''}`}>
      {title && <h3>{title}</h3>}
      {children}
      {error && <p className="error">{error.message}</p>}
    </div>
  )
}
```

### Discriminated Union Pattern

```typescript
type Result<T> =
  | { status: 'loading'; data: null; error: null }
  | { status: 'success'; data: T; error: null }
  | { status: 'error'; data: null; error: Error }

export interface DataGridProps<T> {
  result: Result<T[]>
  onRetry?: () => void
}

export const DataGrid = <T,>({ result, onRetry }: DataGridProps<T>) => {
  switch (result.status) {
    case 'loading':
      return <LoadingSpinner />
    case 'success':
      return <Table data={result.data} />
    case 'error':
      return <ErrorMessage error={result.error} onRetry={onRetry} />
  }
}
```

---

## Hook Patterns

### Custom Hook Template

```typescript
import { useEffect, useState, useCallback } from 'react'

interface UseApiOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  headers?: Record<string, string>
  body?: unknown
  onSuccess?: (data: unknown) => void
  onError?: (error: Error) => void
}

export const useApi = (
  url: string,
  options: UseApiOptions = {}
) => {
  const [data, setData] = useState<unknown>(null)
  const [error, setError] = useState<Error | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const refetch = useCallback(async () => {
    setIsLoading(true)
    try {
      const response = await fetch(url, {
        method: options.method ?? 'GET',
        headers: options.headers,
        body: options.body ? JSON.stringify(options.body) : undefined
      })
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      
      const json = await response.json()
      setData(json)
      options.onSuccess?.(json)
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error')
      setError(error)
      options.onError?.(error)
    } finally {
      setIsLoading(false)
    }
  }, [url, options])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { data, error, isLoading, refetch }
}
```

### useLocalStorage Hook Pattern

```typescript
export const useLocalStorage = <T,>(key: string, initialValue: T) => {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(error)
      return initialValue
    }
  })

  const setValue = useCallback((value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      window.localStorage.setItem(key, JSON.stringify(valueToStore))
    } catch (error) {
      console.error(error)
    }
  }, [key, storedValue])

  return [storedValue, setValue] as const
}
```

---

## Testing Patterns

### Component Test Template

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button', () => {
  test('renders with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button', { name: /click me/i })).toBeInTheDocument()
  })

  test('calls onClick handler', () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click</Button>)
    
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  test('disables when isDisabled prop set', () => {
    render(<Button isDisabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })

  test('applies variant className', () => {
    render(<Button variant="primary">Click</Button>)
    expect(screen.getByRole('button')).toHaveClass('btn--primary')
  })
})
```

### Hook Test Template (Vitest)

```typescript
import { renderHook, act } from '@testing-library/react'
import { useApi } from './useApi'

describe('useApi', () => {
  test('fetches data on mount', async () => {
    const { result } = renderHook(() => useApi('/api/data'))
    
    expect(result.current.isLoading).toBe(true)
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 100))
    })
    
    expect(result.current.data).toBeDefined()
  })
})
```

---

## Accessibility Patterns

### ARIA Labels

```typescript
export const NavItem: React.FC<NavItemProps> = ({
  label,
  icon: Icon,
  isActive
}) => {
  return (
    <a
      href="#"
      aria-label={`Navigation item: ${label}`}
      aria-current={isActive ? 'page' : undefined}
      className={`nav-item ${isActive ? 'nav-item--active' : ''}`}
      data-testid={`nav-item-${label.toLowerCase()}`}
    >
      <Icon aria-hidden="true" size={24} />
      <span>{label}</span>
    </a>
  )
}
```

### Semantic HTML

```typescript
// ✅ Semantic HTML
export const Sidebar = ({ items }: SidebarProps) => {
  return (
    <nav aria-label="Main navigation">
      <ul>
        {items.map(item => (
          <li key={item.id}>
            <button onClick={() => navigate(item.path)}>
              {item.label}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  )
}

// ❌ Non-semantic
export const SidebarBad = ({ items }: SidebarProps) => {
  return (
    <div>
      {items.map(item => (
        <div key={item.id} onClick={() => navigate(item.path)}>
          {item.label}
        </div>
      ))}
    </div>
  )
}
```

---

## Performance Patterns

### Memoization

```typescript
import { memo, useMemo, useCallback } from 'react'

// ✅ Memoize expensive components
export const NavItem = memo(({ item, isActive }: NavItemProps) => {
  return (
    <a className={isActive ? 'active' : ''}>
      {item.label}
    </a>
  )
})

// ✅ Memoize expensive calculations
export const DataGrid = ({ items }: DataGridProps) => {
  const sortedItems = useMemo(
    () => items.sort((a, b) => a.name.localeCompare(b.name)),
    [items]
  )
  
  return <Table items={sortedItems} />
}

// ✅ Memoize callbacks
export const Search = ({ onSearch }: SearchProps) => {
  const debouncedSearch = useCallback(
    debounce((query: string) => onSearch(query), 300),
    [onSearch]
  )
  
  return <input onChange={e => debouncedSearch(e.target.value)} />
}
```

---

## State Management

### Local State

```typescript
// ✅ Use useState for component-level state
const [isOpen, setIsOpen] = useState(false)
const [selectedItem, setSelectedItem] = useState<Item | null>(null)
```

### Persistent State

```typescript
// ✅ Use localStorage hook for persistent state
const [theme, setTheme] = useLocalStorage('theme', 'light')
const [sidebarCollapsed, setSidebarCollapsed] = useLocalStorage('sidebar:collapsed', false)
```

### Global State

```typescript
// ✅ Use Context for truly global state
interface UserContextType {
  user: User | null
  logout: () => void
}

export const UserContext = createContext<UserContextType | undefined>(undefined)

export const useUser = () => {
  const context = useContext(UserContext)
  if (!context) throw new Error('useUser must be used within UserProvider')
  return context
}
```

---

## References

- Component Files: `src/frontend/src/components/`
- Hook Files: `src/frontend/src/hooks/`
- Test Files: `src/frontend/tests/e2e/`
- TypeScript Config: `src/frontend/tsconfig.app.json`
