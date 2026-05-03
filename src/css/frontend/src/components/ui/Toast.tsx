import { useEffect, useRef } from 'react'

export type ToastVariant = 'success' | 'error' | 'warning' | 'info'

export interface ToastProps {
  message: string
  variant?: ToastVariant
  onClose?: () => void
  duration?: number
  id?: string
  action?: {
    label: string
    onClick: () => void
  }
}

const VARIANT_COLORS: Record<ToastVariant, { bg: string; border: string; text: string }> = {
  success: {
    bg: 'rgba(34, 197, 94, 0.1)',
    border: 'var(--success)',
    text: 'var(--success)',
  },
  error: {
    bg: 'rgba(239, 68, 68, 0.1)',
    border: 'var(--red)',
    text: 'var(--red)',
  },
  warning: {
    bg: 'rgba(234, 179, 8, 0.1)',
    border: 'var(--warning)',
    text: 'var(--warning)',
  },
  info: {
    bg: 'rgba(59, 130, 246, 0.1)',
    border: 'var(--accent)',
    text: 'var(--accent)',
  },
}

const VARIANT_ICONS: Record<ToastVariant, string> = {
  success: '✓',
  error: '✕',
  warning: '⚠',
  info: 'ℹ',
}

/**
 * Toast notification component with support for multiple variants.
 * 
 * Features:
 * - Multiple notification types (success, error, warning, info)
 * - Auto-dismiss with configurable duration
 * - Custom action button support
 * - Stacked notifications
 */
export function Toast({
  message,
  variant = 'info',
  onClose,
  duration = 4000,
  id,
  action,
}: ToastProps) {
  const timerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)

  useEffect(() => {
    if (duration && duration > 0) {
      timerRef.current = setTimeout(() => {
        onClose?.()
      }, duration)
    }

    return () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    }
  }, [duration, onClose])

  const colors = VARIANT_COLORS[variant]
  const icon = VARIANT_ICONS[variant]

  return (
    <div
      key={id}
      style={{
        position: 'fixed',
        bottom: 'var(--spacing-lg)',
        right: 'var(--spacing-lg)',
        maxWidth: '400px',
        background: colors.bg,
        border: `2px solid ${colors.border}`,
        borderRadius: 'var(--radius)',
        padding: 'var(--spacing-md)',
        color: colors.text,
        fontSize: '14px',
        fontWeight: '500',
        zIndex: 1000,
        boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--spacing-sm)',
        animation: 'slideInUp 0.3s ease-out',
      }}
    >
      <span style={{ fontSize: '18px', flexShrink: 0 }}>{icon}</span>
      <span style={{ flex: 1 }}>{message}</span>
      {action && (
        <button
          onClick={() => {
            action.onClick()
            onClose?.()
          }}
          style={{
            background: 'transparent',
            border: `1px solid ${colors.text}`,
            color: colors.text,
            padding: '4px 8px',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold',
            whiteSpace: 'nowrap',
            flexShrink: 0,
          }}
        >
          {action.label}
        </button>
      )}
      <button
        onClick={onClose}
        style={{
          background: 'transparent',
          border: 'none',
          color: colors.text,
          cursor: 'pointer',
          fontSize: '18px',
          flexShrink: 0,
          opacity: 0.6,
          transition: 'opacity 0.2s',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.opacity = '1')}
        onMouseLeave={(e) => (e.currentTarget.style.opacity = '0.6')}
      >
        ✕
      </button>
    </div>
  )
}

export interface ToastContextValue {
  showToast: (props: Omit<ToastProps, 'id'>) => string
  hideToast: (id: string) => void
  clearAll: () => void
}

/**
 * Hook for managing toast notifications from anywhere in the app.
 * 
 * Usage:
 * ```tsx
 * const { showToast } = useToast()
 * showToast({ message: 'Success!', variant: 'success' })
 * ```
 */
export function useToast(): ToastContextValue {
  // This will be provided by ToastProvider context
  // For now, return a stub that logs to console
  return {
    showToast: (props) => {
      console.log('Toast:', props)
      return Math.random().toString()
    },
    hideToast: (id) => {
      console.log('Hide toast:', id)
    },
    clearAll: () => {
      console.log('Clear all toasts')
    },
  }
}

