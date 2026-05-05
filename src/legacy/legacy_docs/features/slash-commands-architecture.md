# Slash & Mention Commands Architecture (2026-04-26)

**Feature:** Type `/` or `@` in Send Message prompt to trigger contextual command/mention menus.

**Phase:** Phase 7C+ (10–12 hours, T151–T165)

**Status:** Planning

---

## 1. Feature Overview

### User Experience

**Slash Commands (`/`)**
```
User types: "/ana"
↓
Menu appears with filtered commands:
  📊 /analyze       Analyze selected IOC
  ✍️  /summarize    Summarize text
  🔍 /extract       Extract IOCs
↓
User presses Tab or clicks
↓
Menu closes, command inserted: "Analyze the following IOC:"
↓
User completes text, presses Enter
↓
Command executed with context
```

**Mentions (`@`)**
```
User types: "@case:I"
↓
Menu appears with matching cases:
  INC-2024-001    Ransomware Attack
  INC-2024-005    Data Breach Investigation
↓
User selects or types full ID
↓
Menu closes, mention inserted: "@case:INC-2024-001"
↓
Message sent with context reference
```

### Core Behaviors

- **Trigger:** `/` or `@` followed by 1+ character (or immediately for manual trigger)
- **Search:** Filter commands by typed query (client-side for `/`, API for `@`)
- **Keyboard Navigation:** Arrow keys, Tab, Enter, Escape
- **Mouse:** Click to select, hover to highlight
- **Escape:** Close menu, preserve input
- **Enter/Tab:** Select highlighted item, insert into input
- **Backspace on empty filter:** Close menu

---

## 2. Data Models & Types

### TypeScript Definitions

**File:** `src/frontend/src/types/commands.ts`

```typescript
// Command definition
export interface Command {
  id: string                    // 'analyze', 'summarize', etc.
  label: string                 // "Analyze IOC"
  description: string           // "Analyze selected IOC (type auto-detected)"
  icon: string                  // 'lucide' icon name
  category: 'tools' | 'action' | 'nav' | 'help'
  template?: string             // "Analyze:\n{context}"
  requiresSelection?: boolean    // If true, user must have text selected
  shortcut?: string             // 'Ctrl+Shift+A' for display
  deprecated?: boolean
}

// Mention definition
export interface Mention {
  id: string                    // 'case', 'ioc', 'report', 'file', 'workspace'
  prefix: string                // 'case', 'ioc', 'report'
  label: string                 // "Investigation Case"
  placeholder: string           // "INC-2024-001"
  searchEndpoint: string        // '/api/search/cases?q='
  icon: string
  formatFn: (value: string) => string  // Format selected value
}

// Menu state
export interface MenuState {
  open: boolean
  type: 'command' | 'mention' | null
  query: string
  cursorPos: number
  selectedIndex: number
  items: (Command | Mention)[]
  loading?: boolean
  error?: string
}

// Command execution context
export interface CommandContext {
  selectedText?: string
  cursorPos: number
  currentMessage: string
  activeTab?: string
  workspace?: string
}

// Mention search result
export interface MentionResult {
  id: string
  label: string
  description?: string
  metadata?: Record<string, any>
}
```

---

## 3. Component Architecture

### 3.1 CommandMenu Component

**File:** `src/frontend/src/components/ui/CommandMenu.tsx`

```typescript
import { useEffect, useRef, useState } from 'react'
import { COMMANDS } from '@/config/commands'
import type { Command } from '@/types/commands'
import './CommandMenu.scss'

interface CommandMenuProps {
  query: string
  onSelect: (command: Command) => void
  onClose: () => void
  position: { top: number; left: number }
  selectedIndex: number
}

export default function CommandMenu({
  query,
  onSelect,
  onClose,
  position,
  selectedIndex,
}: CommandMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)
  const [filtered, setFiltered] = useState<Command[]>([])

  // Filter commands by query
  useEffect(() => {
    const search = query.toLowerCase()
    const results = COMMANDS.filter(cmd =>
      cmd.label.toLowerCase().includes(search) ||
      cmd.description.toLowerCase().includes(search) ||
      cmd.id.toLowerCase().startsWith(search)
    )
    setFiltered(results)
  }, [query])

  // Auto-scroll to selected item
  useEffect(() => {
    const selected = menuRef.current?.querySelector('[data-selected]')
    selected?.scrollIntoView({ block: 'nearest' })
  }, [selectedIndex])

  return (
    <div
      ref={menuRef}
      className="command-menu"
      style={{
        position: 'absolute',
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
      role="listbox"
    >
      {filtered.length === 0 ? (
        <div className="command-menu__empty">No commands found</div>
      ) : (
        filtered.map((cmd, idx) => (
          <div
            key={cmd.id}
            className={`command-menu__item ${
              idx === selectedIndex ? 'selected' : ''
            }`}
            data-selected={idx === selectedIndex ? true : undefined}
            onClick={() => onSelect(cmd)}
            role="option"
            aria-selected={idx === selectedIndex}
          >
            <span className="command-menu__icon">
              {/* Lucide icon here */}
            </span>
            <div className="command-menu__text">
              <div className="command-menu__label">/{cmd.id}</div>
              <div className="command-menu__desc">{cmd.description}</div>
            </div>
          </div>
        ))
      )}
    </div>
  )
}
```

### 3.2 MentionMenu Component

**File:** `src/frontend/src/components/ui/MentionMenu.tsx`

```typescript
import { useEffect, useRef, useState } from 'react'
import type { Mention, MentionResult } from '@/types/commands'
import './MentionMenu.scss'

interface MentionMenuProps {
  mention: Mention
  query: string
  onSelect: (result: MentionResult) => void
  onClose: () => void
  position: { top: number; left: number }
  selectedIndex: number
}

export default function MentionMenu({
  mention,
  query,
  onSelect,
  onClose,
  position,
  selectedIndex,
}: MentionMenuProps) {
  const menuRef = useRef<HTMLDivElement>(null)
  const [results, setResults] = useState<MentionResult[]>([])
  const [loading, setLoading] = useState(false)

  // Debounced API search
  useEffect(() => {
    if (!query) {
      setResults([])
      return
    }

    const timer = setTimeout(async () => {
      setLoading(true)
      try {
        const response = await fetch(
          `${mention.searchEndpoint}${encodeURIComponent(query)}`
        )
        const data = await response.json()
        setResults(data.results || [])
      } catch (err) {
        console.error('Mention search error:', err)
        setResults([])
      } finally {
        setLoading(false)
      }
    }, 300) // 300ms debounce

    return () => clearTimeout(timer)
  }, [query, mention])

  return (
    <div
      ref={menuRef}
      className="mention-menu"
      style={{
        position: 'absolute',
        top: `${position.top}px`,
        left: `${position.left}px`,
      }}
      role="listbox"
    >
      {loading ? (
        <div className="mention-menu__loading">Searching...</div>
      ) : results.length === 0 ? (
        <div className="mention-menu__empty">
          No {mention.label.toLowerCase()} found
        </div>
      ) : (
        results.map((result, idx) => (
          <div
            key={result.id}
            className={`mention-menu__item ${
              idx === selectedIndex ? 'selected' : ''
            }`}
            onClick={() => onSelect(result)}
            role="option"
            aria-selected={idx === selectedIndex}
          >
            <div className="mention-menu__label">{result.label}</div>
            {result.description && (
              <div className="mention-menu__desc">{result.description}</div>
            )}
          </div>
        ))
      )}
    </div>
  )
}
```

### 3.3 Custom Hook: useCommandMenu

**File:** `src/frontend/src/hooks/useCommandMenu.ts`

```typescript
import { useEffect, useRef, useState } from 'react'
import { useEventListener } from '@/hooks/useEventListener'
import type { Command, Mention, MenuState } from '@/types/commands'

interface UseCommandMenuProps {
  inputRef: React.RefObject<HTMLInputElement>
  onCommand?: (command: Command, context: string) => void
  onMention?: (mention: string) => void
}

export function useCommandMenu({
  inputRef,
  onCommand,
  onMention,
}: UseCommandMenuProps) {
  const [menuState, setMenuState] = useState<MenuState>({
    open: false,
    type: null,
    query: '',
    cursorPos: 0,
    selectedIndex: 0,
    items: [],
  })

  // Track input changes
  const handleInput = (e: React.FormEvent<HTMLInputElement>) => {
    const input = e.currentTarget
    const text = input.value
    const pos = input.selectionStart || 0

    // Check for / or @ at cursor position
    if (pos > 0) {
      const lastCharBefore = text[pos - 1]

      // Slash command trigger
      if (lastCharBefore === '/') {
        const queryStart = pos
        const query = text.slice(queryStart).split(/\s/)[0]
        setMenuState(prev => ({
          ...prev,
          open: true,
          type: 'command',
          query,
          cursorPos: pos,
          selectedIndex: 0,
        }))
      }
      // Mention trigger
      else if (lastCharBefore === '@') {
        const queryStart = pos
        const query = text.slice(queryStart).split(/\s/)[0]
        setMenuState(prev => ({
          ...prev,
          open: true,
          type: 'mention',
          query,
          cursorPos: pos,
          selectedIndex: 0,
        }))
      }
      // Close menu if no trigger
      else if (menuState.open && !['/'].includes(lastCharBefore)) {
        setMenuState(prev => ({ ...prev, open: false, type: null }))
      }
    }
  }

  // Handle keyboard navigation
  useEventListener('keydown', (e: KeyboardEvent) => {
    if (!menuState.open) return

    switch (e.key) {
      case 'ArrowUp':
        e.preventDefault()
        setMenuState(prev => ({
          ...prev,
          selectedIndex: Math.max(0, prev.selectedIndex - 1),
        }))
        break

      case 'ArrowDown':
        e.preventDefault()
        setMenuState(prev => ({
          ...prev,
          selectedIndex: Math.min(
            prev.items.length - 1,
            prev.selectedIndex + 1
          ),
        }))
        break

      case 'Enter':
      case 'Tab':
        e.preventDefault()
        const selected = menuState.items[menuState.selectedIndex]
        if (selected) {
          // Handle selection
          handleSelectItem(selected)
        }
        break

      case 'Escape':
        e.preventDefault()
        setMenuState(prev => ({ ...prev, open: false, type: null }))
        break
    }
  })

  const handleSelectItem = (item: Command | Mention) => {
    // Execute command or insert mention
    setMenuState(prev => ({ ...prev, open: false, type: null }))
  }

  return {
    menuState,
    handleInput,
    closeMenu: () =>
      setMenuState(prev => ({ ...prev, open: false, type: null })),
  }
}
```

---

## 4. Integration with SendMessagePrompt

**File:** `src/frontend/src/components/layout/SendMessagePrompt.tsx` (MODIFIED)

```typescript
import { useRef, useState } from 'react'
import { useUIStore } from '@/store/uiStore'
import Button from '@/components/ui/Button'
import CommandMenu from '@/components/ui/CommandMenu'
import MentionMenu from '@/components/ui/MentionMenu'
import { useCommandMenu } from '@/hooks/useCommandMenu'
import type { Command, Mention, MentionResult } from '@/types/commands'

export default function SendMessagePrompt() {
  const inputRef = useRef<HTMLInputElement>(null)
  const [message, setMessage] = useState('')
  const { setActiveTab } = useUIStore()

  const { menuState, handleInput, closeMenu } = useCommandMenu({
    inputRef,
    onCommand: executeCommand,
    onMention: insertMention,
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setMessage(e.currentTarget.value)
    handleInput(e as any)
  }

  const handleSelectCommand = (command: Command) => {
    executeCommand(command, message)
  }

  const executeCommand = (command: Command, currentMessage: string) => {
    // Replace command trigger with template
    let expanded = command.template || `${command.label}:\n`

    // Inject context if available
    if (command.requiresSelection && currentMessage) {
      expanded = expanded.replace('{context}', currentMessage)
    }

    setMessage(expanded)
    closeMenu()

    // Handle special commands
    if (command.id === 'open-panel') {
      // Command contains panel name
      const panel = currentMessage.split(':')[1]?.trim()
      if (panel) {
        setActiveTab(panel as any)
      }
    }
  }

  const handleSelectMention = (result: MentionResult) => {
    insertMention(`@${result.id}:${result.label}`)
  }

  const insertMention = (mentionText: string) => {
    const cursorPos = inputRef.current?.selectionStart || 0

    // Find the @ position
    const beforeText = message.slice(0, cursorPos)
    const lastAtPos = beforeText.lastIndexOf('@')

    if (lastAtPos !== -1) {
      // Replace from @ to cursor
      const newMessage =
        message.slice(0, lastAtPos) + mentionText + message.slice(cursorPos)
      setMessage(newMessage)
    }

    closeMenu()
  }

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault()
        if (!message.trim()) return

        setActiveTab('chat')
        window.dispatchEvent(
          new CustomEvent('send-message', { detail: { text: message } })
        )
        setMessage('')
      }}
      style={{ padding: '12px', position: 'relative' }}
    >
      <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="💬 Type / for commands, @ for mentions..."
          value={message}
          onChange={handleChange}
          data-test="send-message-input"
          style={{
            flex: 1,
            padding: '8px 12px',
            borderRadius: '6px',
            border: '1px solid var(--border)',
            background: 'var(--bg-elevated)',
            color: 'var(--text-primary)',
            fontSize: '13px',
            outline: 'none',
            transition: 'border-color 0.2s',
          }}
          onFocus={(e) => {
            e.currentTarget.style.borderColor = 'var(--accent)'
          }}
          onBlur={(e) => {
            e.currentTarget.style.borderColor = 'var(--border)'
            closeMenu()
          }}
        />
        <Button
          variant="primary"
          type="submit"
          disabled={!message.trim()}
          data-test="send-message-button"
        >
          Send
        </Button>
      </div>

      {/* Command Menu */}
      {menuState.open && menuState.type === 'command' && inputRef.current && (
        <CommandMenu
          query={menuState.query}
          onSelect={handleSelectCommand}
          onClose={closeMenu}
          position={calculateMenuPosition(inputRef.current, menuState.cursorPos)}
          selectedIndex={menuState.selectedIndex}
        />
      )}

      {/* Mention Menu */}
      {menuState.open && menuState.type === 'mention' && inputRef.current && (
        <MentionMenu
          mention={{ id: 'case', prefix: 'case', label: 'Case' } as Mention}
          query={menuState.query}
          onSelect={handleSelectMention}
          onClose={closeMenu}
          position={calculateMenuPosition(inputRef.current, menuState.cursorPos)}
          selectedIndex={menuState.selectedIndex}
        />
      )}
    </form>
  )
}

function calculateMenuPosition(
  inputEl: HTMLInputElement,
  cursorPos: number
): { top: number; left: number } {
  const rect = inputEl.getBoundingClientRect()
  const canvas = document.createElement('canvas')
  const ctx = canvas.getContext('2d')!
  ctx.font = window.getComputedStyle(inputEl).font

  const textBeforeCursor = inputEl.value.slice(0, cursorPos)
  const cursorX = ctx.measureText(textBeforeCursor).width

  return {
    top: rect.bottom + 8,
    left: rect.left + cursorX,
  }
}
```

---

## 5. Testing Strategy

### E2E Tests (Playwright)

**File:** `tests/e2e/slash-mentions.spec.ts`

```typescript
import { test, expect } from '@playwright/test'

test('slash command menu appears on /', async ({ page }) => {
  await page.goto('http://localhost:3000')

  // Type / in input
  const input = page.locator('[data-test="send-message-input"]')
  await input.focus()
  await input.type('/')

  // Menu should appear
  const menu = page.locator('.command-menu')
  await expect(menu).toBeVisible()

  // Should show commands
  const items = page.locator('.command-menu__item')
  const count = await items.count()
  expect(count).toBeGreaterThan(0)
})

test('keyboard navigation in command menu', async ({ page }) => {
  await page.goto('http://localhost:3000')

  const input = page.locator('[data-test="send-message-input"]')
  await input.focus()
  await input.type('/')

  // Press arrow down
  await page.keyboard.press('ArrowDown')

  // Second item should be selected
  const selected = page.locator('.command-menu__item.selected')
  await expect(selected).toBeVisible()
})

test('escape closes menu and preserves input', async ({ page }) => {
  await page.goto('http://localhost:3000')

  const input = page.locator('[data-test="send-message-input"]')
  await input.focus()
  await input.type('test /ana')

  // Menu appears
  await expect(page.locator('.command-menu')).toBeVisible()

  // Press Escape
  await page.keyboard.press('Escape')

  // Menu closes
  await expect(page.locator('.command-menu')).not.toBeVisible()

  // Input preserved
  const value = await input.inputValue()
  expect(value).toBe('test /ana')
})
```

---

## 6. Styling (SCSS)

**File:** `src/frontend/src/components/ui/CommandMenu.scss`

```scss
.command-menu {
  min-width: 300px;
  max-width: 400px;
  max-height: 400px;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow-y: auto;
  animation: fadeIn 0.1s ease-out;

  @keyframes fadeIn {
    from {
      opacity: 0;
      transform: translateY(-4px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 8px 12px;
    cursor: pointer;
    border-left: 3px solid transparent;
    transition: background-color 0.15s;

    &:hover,
    &.selected {
      background-color: var(--bg-hover);
      border-left-color: var(--accent);
    }
  }

  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    flex-shrink: 0;
    color: var(--text-muted);
  }

  &__text {
    min-width: 0;
    flex: 1;
  }

  &__label {
    font-size: 12px;
    font-weight: 500;
    color: var(--text-primary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  &__desc {
    font-size: 11px;
    color: var(--text-muted);
    margin-top: 2px;
  }

  &__empty {
    padding: 16px 12px;
    text-align: center;
    color: var(--text-muted);
    font-size: 12px;
  }
}
```

---

**Created:** 2026-04-26  
**Phase:** Phase 7C+  
**Status:** Planning  
**Next Todo:** T151 (Create CommandMenu component)
