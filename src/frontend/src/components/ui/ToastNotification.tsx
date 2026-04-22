import { createContext, useContext, useState, useCallback, ReactNode } from 'react'
import { Toast, type ToastProps, type ToastVariant } from './Toast'

interface ToastMessage extends Omit<ToastProps, 'id'> {
  id: string
}

interface ToastContextValue {
  toasts: ToastMessage[]
  showToast: (props: Omit<ToastProps, 'id' | 'onClose'>) => string
  hideToast: (id: string) => void
  clearAll: () => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

/**
 * ToastProvider component that manages multiple toast notifications.
 * 
 * Usage:
 * ```tsx
 * <ToastProvider>
 *   <App />
 * </ToastProvider>
 * ```
 */
export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([])

  const showToast = useCallback(
    (props: Omit<ToastProps, 'id' | 'onClose'>): string => {
      const id = Math.random().toString(36).substring(2, 9)
      setToasts((prev) => [
        ...prev,
        {
          id,
          ...props,
        },
      ])
      return id
    },
    []
  )

  const hideToast = useCallback((id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id))
  }, [])

  const clearAll = useCallback(() => {
    setToasts([])
  }, [])

  const value: ToastContextValue = { toasts, showToast, hideToast, clearAll }

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div
        style={{
          position: 'fixed',
          bottom: 'var(--spacing-lg)',
          right: 'var(--spacing-lg)',
          zIndex: 1000,
          display: 'flex',
          flexDirection: 'column',
          gap: 'var(--spacing-sm)',
          maxWidth: '100%',
          pointerEvents: 'none',
        }}
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            style={{
              pointerEvents: 'auto',
              animation: 'slideInUp 0.3s ease-out',
            }}
          >
            <Toast
              {...toast}
              onClose={() => hideToast(toast.id)}
            />
          </div>
        ))}
      </div>
      <style>{`
        @keyframes slideInUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </ToastContext.Provider>
  )
}

/**
 * Hook to use toast notifications from anywhere in the app.
 * 
 * Usage:
 * ```tsx
 * const { showToast } = useToast()
 * showToast({ message: 'Success!', variant: 'success' })
 * showToast({
 *   message: 'Something failed',
 *   variant: 'error',
 *   action: { label: 'Retry', onClick: () => retry() }
 * })
 * ```
 */
export function useToast(): Omit<ToastContextValue, 'toasts'> {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return {
    showToast: context.showToast,
    hideToast: context.hideToast,
    clearAll: context.clearAll,
  }
}

/**
 * Helper to show an error toast with optional action.
 */
export function useErrorToast() {
  const { showToast } = useToast()
  return (message: string, action?: { label: string; onClick: () => void }) => {
    showToast({
      message,
      variant: 'error',
      duration: 5000,
      action,
    })
  }
}

/**
 * Helper to show a success toast.
 */
export function useSuccessToast() {
  const { showToast } = useToast()
  return (message: string) => {
    showToast({
      message,
      variant: 'success',
      duration: 3000,
    })
  }
}

/**
 * Helper to show a warning toast.
 */
export function useWarningToast() {
  const { showToast } = useToast()
  return (message: string) => {
    showToast({
      message,
      variant: 'warning',
      duration: 4000,
    })
  }
}
