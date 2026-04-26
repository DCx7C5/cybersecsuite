import { useEffect, useRef, useCallback } from 'react'

export interface KeyboardShortcut {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
  handler: (e: KeyboardEvent) => void
  description?: string
}

/**
 * Hook for registering keyboard shortcuts for menu navigation and actions
 * Supports combinations with Ctrl, Shift, Alt, and Meta (Cmd) keys
 */
export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]): void {
  const handlersRef = useRef<Map<string, KeyboardShortcut>>(new Map())

  useEffect(() => {
    const getShortcutKey = (shortcut: KeyboardShortcut): string => {
      const modifiers = [
        shortcut.ctrl && 'ctrl',
        shortcut.shift && 'shift',
        shortcut.alt && 'alt',
        shortcut.meta && 'meta',
      ]
        .filter(Boolean)
        .join('+')
      return modifiers ? `${modifiers}+${shortcut.key.toLowerCase()}` : shortcut.key.toLowerCase()
    }

    shortcuts.forEach((shortcut) => {
      handlersRef.current.set(getShortcutKey(shortcut), shortcut)
    })

    const handleKeyDown = (e: KeyboardEvent) => {
      const modifiers = [
        e.ctrlKey && 'ctrl',
        e.shiftKey && 'shift',
        e.altKey && 'alt',
        e.metaKey && 'meta',
      ]
        .filter(Boolean)
        .join('+')

      const shortcutKey = modifiers
        ? `${modifiers}+${e.key.toLowerCase()}`
        : e.key.toLowerCase()

      const shortcut = handlersRef.current.get(shortcutKey)
      if (shortcut) {
        e.preventDefault()
        shortcut.handler(e)
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [shortcuts])
}

/**
 * Hook for menu keyboard navigation (arrow keys, Enter, Escape)
 */
export function useMenuKeyboard(options: {
  onNavigate?: (direction: 'up' | 'down' | 'left' | 'right') => void
  onSelect?: () => void
  onEscape?: () => void
}): { handleKeyDown: (e: KeyboardEvent) => void } {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      switch (e.key) {
        case 'ArrowUp':
          e.preventDefault()
          options.onNavigate?.('up')
          break
        case 'ArrowDown':
          e.preventDefault()
          options.onNavigate?.('down')
          break
        case 'ArrowLeft':
          e.preventDefault()
          options.onNavigate?.('left')
          break
        case 'ArrowRight':
          e.preventDefault()
          options.onNavigate?.('right')
          break
        case 'Enter':
          e.preventDefault()
          options.onSelect?.()
          break
        case 'Escape':
          e.preventDefault()
          options.onEscape?.()
          break
      }
    },
    [options]
  )

  return { handleKeyDown }
}

/**
 * Common keyboard shortcuts for CyberSecSuite
 */
export const COMMON_SHORTCUTS = {
  SEARCH: { key: 'k', ctrl: true } as const,
  FOCUS_SIDEBAR: { key: '[', ctrl: true } as const,
  FOCUS_CONTENT: { key: ']', ctrl: true } as const,
  TOGGLE_SIDEBAR: { key: 'b', alt: true } as const,
  GO_HOME: { key: 'h', alt: true } as const,
  OPEN_SETTINGS: { key: ',', ctrl: true } as const,
  NEXT_TAB: { key: 'Tab', ctrl: true } as const,
  PREV_TAB: { key: 'Tab', ctrl: true, shift: true } as const,
} as const

/**
 * Hook for common CyberSecSuite shortcuts
 */
export function useCommonShortcuts(handlers: Partial<Record<keyof typeof COMMON_SHORTCUTS, (e: KeyboardEvent) => void>>): void {
  const shortcuts: KeyboardShortcut[] = []

  if (handlers.SEARCH) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.SEARCH,
      handler: handlers.SEARCH,
      description: 'Open search',
    })
  }

  if (handlers.FOCUS_SIDEBAR) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.FOCUS_SIDEBAR,
      handler: handlers.FOCUS_SIDEBAR,
      description: 'Focus sidebar',
    })
  }

  if (handlers.FOCUS_CONTENT) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.FOCUS_CONTENT,
      handler: handlers.FOCUS_CONTENT,
      description: 'Focus content',
    })
  }

  if (handlers.TOGGLE_SIDEBAR) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.TOGGLE_SIDEBAR,
      handler: handlers.TOGGLE_SIDEBAR,
      description: 'Toggle sidebar',
    })
  }

  if (handlers.GO_HOME) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.GO_HOME,
      handler: handlers.GO_HOME,
      description: 'Go to home',
    })
  }

  if (handlers.OPEN_SETTINGS) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.OPEN_SETTINGS,
      handler: handlers.OPEN_SETTINGS,
      description: 'Open settings',
    })
  }

  if (handlers.NEXT_TAB) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.NEXT_TAB,
      handler: handlers.NEXT_TAB,
      description: 'Next tab',
    })
  }

  if (handlers.PREV_TAB) {
    shortcuts.push({
      ...COMMON_SHORTCUTS.PREV_TAB,
      handler: handlers.PREV_TAB,
      description: 'Previous tab',
    })
  }

  useKeyboardShortcuts(shortcuts)
}
