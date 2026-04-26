import { useEffect, useState, useCallback } from 'react'

interface CommandItem {
  id: string
  label: string
  description?: string
  category?: string
  action: () => void
  icon?: string
  shortcut?: string
}

export function useCommandMenu(commands: CommandItem[] = []) {
  const [isOpen, setIsOpen] = useState(false)

  const openMenu = useCallback(() => setIsOpen(true), [])
  const closeMenu = useCallback(() => setIsOpen(false), [])
  const toggleMenu = useCallback(() => setIsOpen((prev) => !prev), [])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Check for Cmd+K (Mac) or Ctrl+K (Windows/Linux)
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        toggleMenu()
      }
      // Check for '/' key to open menu
      if (e.key === '/' && !isOpen) {
        const target = e.target as HTMLElement
        const isInput =
          target.tagName === 'INPUT' ||
          target.tagName === 'TEXTAREA' ||
          (target as HTMLElement).contentEditable === 'true'
        if (!isInput) {
          e.preventDefault()
          setIsOpen(true)
        }
      }
      // ESC to close
      if (e.key === 'Escape' && isOpen) {
        closeMenu()
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, toggleMenu, closeMenu])

  return {
    isOpen,
    openMenu,
    closeMenu,
    toggleMenu,
  }
}
