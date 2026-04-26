import { useEffect, useState, useRef, useCallback } from 'react'

interface CommandItem {
  id: string
  label: string
  description?: string
  category?: string
  action: () => void
  icon?: string
  shortcut?: string
  ariaLabel?: string
}

interface CommandMenuProps {
  isOpen: boolean
  onClose: () => void
  commands: CommandItem[]
  placeholder?: string
  ariaLabel?: string
  ariaLabelledBy?: string
}

export default function CommandMenu({
  isOpen,
  onClose,
  commands,
  placeholder = 'Type a command...',
  ariaLabel = 'Command menu',
  ariaLabelledBy,
}: CommandMenuProps) {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)
  const listboxRef = useRef<HTMLDivElement>(null)

  const filtered = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description?.toLowerCase().includes(search.toLowerCase())
  )

  // Announce selected item to screen readers
  useEffect(() => {
    if (filtered.length > 0 && listboxRef.current) {
      const selectedItem = listboxRef.current.children[selectedIndex] as HTMLElement
      if (selectedItem) {
        selectedItem.scrollIntoView({ block: 'nearest' })
      }
    }
  }, [selectedIndex, filtered.length])

  // Announce filter results to screen readers
  const resultCount = filtered.length
  const resultsAriaLabel = resultCount === 0 
    ? 'No commands found'
    : `${resultCount} command${resultCount !== 1 ? 's' : ''} found`

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus()
      setSearch('')
      setSelectedIndex(0)
    }
  }, [isOpen])

  const executeCommand = useCallback(() => {
    if (filtered[selectedIndex]) {
      filtered[selectedIndex].action()
      onClose()
    }
  }, [filtered, selectedIndex, onClose])

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'Escape':
        e.preventDefault()
        onClose()
        break
      case 'Enter':
        e.preventDefault()
        executeCommand()
        break
      case 'ArrowDown':
        e.preventDefault()
        setSelectedIndex((i) => (i + 1) % filtered.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setSelectedIndex((i) => (i - 1 + filtered.length) % filtered.length)
        break
      case 'Home':
        e.preventDefault()
        setSelectedIndex(0)
        break
      case 'End':
        e.preventDefault()
        setSelectedIndex(Math.max(0, filtered.length - 1))
        break
      case 'Tab':
        e.preventDefault()
        if (e.shiftKey) {
          setSelectedIndex((i) => (i - 1 + filtered.length) % filtered.length)
        } else {
          setSelectedIndex((i) => (i + 1) % filtered.length)
        }
        break
    }
  }

  if (!isOpen) return null

  return (
    <div
      role="presentation"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0, 0, 0, 0.5)',
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '100px',
        zIndex: 1000,
      }}
      onClick={onClose}
      onKeyDown={(e) => {
        if (e.key === 'Escape') {
          e.stopPropagation()
          onClose()
        }
      }}
    >
      <div
        ref={menuRef}
        role="dialog"
        aria-modal="true"
        aria-label={ariaLabel}
        aria-labelledBy={ariaLabelledBy}
        style={{
          width: '100%',
          maxWidth: '600px',
          background: 'var(--bg-deep)',
          border: '1px solid var(--border)',
          borderRadius: '8px',
          boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
          overflow: 'hidden',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        <div style={{ padding: '12px 16px', borderBottom: '1px solid var(--border)' }}>
          <input
            ref={inputRef}
            type="search"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            aria-label={placeholder}
            aria-describedby="command-menu-results"
            aria-controls="command-menu-listbox"
            autoComplete="off"
            spellCheck="false"
            style={{
              width: '100%',
              padding: '8px 12px',
              fontSize: '14px',
              background: 'transparent',
              border: 'none',
              color: 'var(--text-primary)',
              outline: 'none',
            }}
          />
        </div>

        <div
          id="command-menu-results"
          role="status"
          aria-live="polite"
          aria-atomic="true"
          style={{
            position: 'absolute',
            left: '-10000px',
            width: '1px',
            height: '1px',
            overflow: 'hidden',
          }}
        >
          {resultsAriaLabel}
        </div>

        <div
          id="command-menu-listbox"
          ref={listboxRef}
          role="listbox"
          aria-label="Available commands"
          style={{
            maxHeight: '400px',
            overflowY: 'auto',
          }}
        >
          {filtered.length === 0 ? (
            <div
              role="option"
              aria-disabled="true"
              style={{
                padding: '32px 16px',
                textAlign: 'center',
                color: 'var(--text-faint)',
                fontSize: '13px',
              }}
            >
              No commands found
            </div>
          ) : (
            filtered.map((cmd, index) => (
              <button
                key={cmd.id}
                role="option"
                aria-selected={index === selectedIndex}
                onClick={() => {
                  setSelectedIndex(index)
                  executeCommand()
                }}
                onMouseEnter={() => setSelectedIndex(index)}
                aria-label={cmd.ariaLabel || cmd.label}
                title={cmd.description}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  textAlign: 'left',
                  border: 'none',
                  background:
                    index === selectedIndex
                      ? 'var(--accent-glow)'
                      : 'transparent',
                  color: index === selectedIndex ? 'var(--accent)' : 'var(--text-primary)',
                  fontSize: '13px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  transition: 'all 0.15s',
                  borderLeft:
                    index === selectedIndex ? '2px solid var(--accent)' : '2px solid transparent',
                }}
              >
                <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  {cmd.icon && (
                    <span aria-hidden="true" style={{ fontSize: '16px' }}>
                      {cmd.icon}
                    </span>
                  )}
                  <div>
                    <div style={{ fontWeight: 500 }}>{cmd.label}</div>
                    {cmd.description && (
                      <div
                        style={{
                          fontSize: '11px',
                          color: 'var(--text-muted)',
                          marginTop: '2px',
                        }}
                      >
                        {cmd.description}
                      </div>
                    )}
                  </div>
                </span>
                {cmd.shortcut && (
                  <span
                    aria-label={`keyboard shortcut: ${cmd.shortcut}`}
                    style={{
                      fontSize: '11px',
                      color: 'var(--text-faint)',
                      background: 'var(--bg-input)',
                      padding: '2px 6px',
                      borderRadius: '3px',
                      marginLeft: '8px',
                    }}
                  >
                    {cmd.shortcut}
                  </span>
                )}
              </button>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
