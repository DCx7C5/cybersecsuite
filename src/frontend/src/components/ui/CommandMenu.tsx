import { useEffect, useState, useRef, useCallback } from 'react'

interface CommandItem {
  id: string
  label: string
  description?: string
  category?: string
  action: () => void
  icon?: string
  shortcut?: string
}

interface CommandMenuProps {
  isOpen: boolean
  onClose: () => void
  commands: CommandItem[]
  placeholder?: string
}

export default function CommandMenu({
  isOpen,
  onClose,
  commands,
  placeholder = 'Type a command...',
}: CommandMenuProps) {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const menuRef = useRef<HTMLDivElement>(null)

  const filtered = commands.filter((cmd) =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description?.toLowerCase().includes(search.toLowerCase())
  )

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
        onClose()
        break
      case 'Enter':
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
    }
  }

  if (!isOpen) return null

  return (
    <div
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
    >
      <div
        ref={menuRef}
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
            type="text"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setSelectedIndex(0)
            }}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
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
          style={{
            maxHeight: '400px',
            overflowY: 'auto',
          }}
        >
          {filtered.length === 0 ? (
            <div
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
                onClick={() => {
                  setSelectedIndex(index)
                  executeCommand()
                }}
                onMouseEnter={() => setSelectedIndex(index)}
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
                  {cmd.icon && <span>{cmd.icon}</span>}
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
