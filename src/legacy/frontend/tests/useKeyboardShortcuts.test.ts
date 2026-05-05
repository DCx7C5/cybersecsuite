import { describe, it, expect, beforeEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import {
  useKeyboardShortcuts,
  useMenuKeyboard,
  useCommonShortcuts,
  COMMON_SHORTCUTS,
} from '../../hooks/useKeyboardShortcuts'

describe('Keyboard Shortcuts - t159: Menu Navigation Shortcuts', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should register keyboard shortcuts', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 'k', ctrl: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })

  it('should support shift modifier', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 'K', shift: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 'K', shiftKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })

  it('should support alt modifier', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 'b', alt: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 'b', altKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })

  it('should support meta modifier', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 's', meta: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 's', metaKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })

  it('should support combined modifiers', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 's', ctrl: true, shift: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 's', ctrlKey: true, shiftKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })

  it('should prevent default behavior', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 'k', ctrl: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    const preventDefaultSpy = vi.spyOn(event, 'preventDefault')

    act(() => {
      window.dispatchEvent(event)
    })

    expect(preventDefaultSpy).toHaveBeenCalled()
  })

  it('should distinguish between different shortcuts', () => {
    const handler1 = vi.fn()
    const handler2 = vi.fn()
    const shortcuts = [
      { key: 'a', ctrl: true, handler: handler1 },
      { key: 'b', ctrl: true, handler: handler2 },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event1 = new KeyboardEvent('keydown', { key: 'a', ctrlKey: true })
    act(() => {
      window.dispatchEvent(event1)
    })
    expect(handler1).toHaveBeenCalled()
    expect(handler2).not.toHaveBeenCalled()
  })

  it('should handle case-insensitive keys', () => {
    const handler = vi.fn()
    const shortcuts = [
      { key: 'K', ctrl: true, handler },
    ]

    renderHook(() => useKeyboardShortcuts(shortcuts))

    const event = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    act(() => {
      window.dispatchEvent(event)
    })

    expect(handler).toHaveBeenCalled()
  })
})

describe('Menu Keyboard Navigation', () => {
  it('should handle arrow navigation', () => {
    const onNavigate = vi.fn()
    const { result } = renderHook(() => useMenuKeyboard({ onNavigate }))

    const upEvent = new KeyboardEvent('keydown', { key: 'ArrowUp' })
    result.current.handleKeyDown(upEvent)
    expect(onNavigate).toHaveBeenCalledWith('up')

    const downEvent = new KeyboardEvent('keydown', { key: 'ArrowDown' })
    result.current.handleKeyDown(downEvent)
    expect(onNavigate).toHaveBeenCalledWith('down')

    const leftEvent = new KeyboardEvent('keydown', { key: 'ArrowLeft' })
    result.current.handleKeyDown(leftEvent)
    expect(onNavigate).toHaveBeenCalledWith('left')

    const rightEvent = new KeyboardEvent('keydown', { key: 'ArrowRight' })
    result.current.handleKeyDown(rightEvent)
    expect(onNavigate).toHaveBeenCalledWith('right')
  })

  it('should handle Enter for selection', () => {
    const onSelect = vi.fn()
    const { result } = renderHook(() => useMenuKeyboard({ onSelect }))

    const event = new KeyboardEvent('keydown', { key: 'Enter' })
    result.current.handleKeyDown(event)
    expect(onSelect).toHaveBeenCalled()
  })

  it('should handle Escape to close', () => {
    const onEscape = vi.fn()
    const { result } = renderHook(() => useMenuKeyboard({ onEscape }))

    const event = new KeyboardEvent('keydown', { key: 'Escape' })
    result.current.handleKeyDown(event)
    expect(onEscape).toHaveBeenCalled()
  })

  it('should prevent default key behavior', () => {
    const { result } = renderHook(() => useMenuKeyboard({ onNavigate: vi.fn() }))

    const event = new KeyboardEvent('keydown', { key: 'ArrowUp' })
    const preventDefaultSpy = vi.spyOn(event, 'preventDefault')

    result.current.handleKeyDown(event)
    expect(preventDefaultSpy).toHaveBeenCalled()
  })
})

describe('Common Shortcuts', () => {
  it('should provide predefined common shortcuts', () => {
    expect(COMMON_SHORTCUTS.SEARCH).toBeDefined()
    expect(COMMON_SHORTCUTS.TOGGLE_SIDEBAR).toBeDefined()
    expect(COMMON_SHORTCUTS.OPEN_SETTINGS).toBeDefined()
  })

  it('should use common shortcuts hook', () => {
    const handlers = {
      SEARCH: vi.fn(),
      OPEN_SETTINGS: vi.fn(),
    }

    renderHook(() => useCommonShortcuts(handlers))

    const searchEvent = new KeyboardEvent('keydown', { key: 'k', ctrlKey: true })
    act(() => {
      window.dispatchEvent(searchEvent)
    })

    expect(handlers.SEARCH).toHaveBeenCalled()
  })

  it('should support partial handler registration', () => {
    const handlers = {
      SEARCH: vi.fn(),
    }

    expect(() => {
      renderHook(() => useCommonShortcuts(handlers))
    }).not.toThrow()
  })
})
