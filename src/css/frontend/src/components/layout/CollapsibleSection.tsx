import type { ReactNode } from 'react'
import { useState, useEffect } from 'react'

interface BackendOption {
  id: string
  name: string
  url?: string
}

interface CollapsibleSectionProps {
  id: string
  label: string
  icon: string
  defaultOpen?: boolean
  children: ReactNode
  showBackendDropdown?: boolean
  onBackendSelect?: (backend: BackendOption) => void
}

export default function CollapsibleSection({
  id,
  label,
  icon,
  defaultOpen = true,
  children,
  showBackendDropdown = false,
  onBackendSelect,
}: CollapsibleSectionProps) {
  const key = `sidebar-section-${id}`
  const backendKey = `selected-backend-${id}`
  const [isOpen, setIsOpen] = useState<boolean>(() => {
    const saved = localStorage.getItem(key)
    return saved !== null ? JSON.parse(saved) : defaultOpen
  })
  const [backends, setBackends] = useState<BackendOption[]>([])
  const [selectedBackend, setSelectedBackend] = useState<BackendOption | null>(() => {
    const saved = localStorage.getItem(backendKey)
    return saved ? JSON.parse(saved) : null
  })

  // Load backends from API
  useEffect(() => {
    if (!showBackendDropdown || backends.length > 0) {
      return
    }

    let mounted = true
    const fetchBackends = async () => {
      try {
        const response = await fetch('/api/backends', { signal: AbortSignal.timeout(5000) })
        if (response.ok && mounted) {
          const data = await response.json()
          setBackends(data.backends || [])
        }
      } catch {
        if (mounted) {
          console.warn('Failed to load backends')
          setBackends([])
        }
      }
    }

    fetchBackends()
    return () => {
      mounted = false
    }
  }, [showBackendDropdown, backends.length])

  // Persist state to localStorage
  const handleToggle = () => {
    const newState = !isOpen
    setIsOpen(newState)
    localStorage.setItem(`sidebar-section-${id}`, JSON.stringify(newState))
  }

  const handleBackendChange = (backend: BackendOption) => {
    setSelectedBackend(backend)
    localStorage.setItem(backendKey, JSON.stringify(backend))
    if (onBackendSelect) {
      onBackendSelect(backend)
    }
  }

  return (
    <div style={{ paddingTop: '8px' }}>
      <button
        onClick={handleToggle}
        data-test={`collapsible-${id}-header`}
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '8px 12px',
          background: 'transparent',
          border: 'none',
          fontSize: '10px',
          fontWeight: 700,
          color: 'var(--text-faint)',
          letterSpacing: '0.1em',
          textTransform: 'uppercase',
          cursor: 'pointer',
          transition: 'color 0.15s',
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.color = 'var(--text-primary)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.color = 'var(--text-faint)'
        }}
      >
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span>{icon}</span>
          <span>{label}</span>
        </span>
        <span
          style={{
            fontSize: '10px',
            transition: 'transform 0.2s',
            transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
          }}
        >
          ▾
        </span>
      </button>

      {showBackendDropdown && (
        <div
          style={{
            padding: '8px 12px',
            borderBottom: '1px solid var(--border)',
          }}
          data-test={`collapsible-${id}-backend-dropdown`}
        >
          <select
            value={selectedBackend?.id || ''}
            onChange={(e) => {
              const backend = backends.find((b) => b.id === e.target.value)
              if (backend) {
                handleBackendChange(backend)
              }
            }}
            style={{
              width: '100%',
              padding: '6px 8px',
              fontSize: '11px',
              background: 'var(--bg-input)',
              border: '1px solid var(--border)',
              borderRadius: '4px',
              color: 'var(--text-primary)',
              cursor: 'pointer',
            }}
          >
            <option value="">{backends.length === 0 ? 'Loading...' : 'Select backend'}</option>
            {backends.map((backend) => (
              <option key={backend.id} value={backend.id}>
                {backend.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {isOpen && (
        <div
          data-test={`collapsible-${id}-content`}
          style={{
            animation: 'fadeIn 0.15s ease-out',
            paddingLeft: '8px',
          }}
        >
          {children}
        </div>
      )}

      <style>{`
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
      `}</style>
    </div>
  )
}
