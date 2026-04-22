import { useState, useEffect } from 'react'

export interface ToastProps {
  message: string
  variant?: 'ok' | 'err' | 'info'
  onClose: () => void
}

export function Toast({ message, variant = 'info', onClose }: ToastProps) {
  useEffect(() => {
    const t = setTimeout(onClose, 3000)
    return () => clearTimeout(t)
  }, [onClose])

  const colors = {
    ok: 'var(--success)',
    err: 'var(--red)',
    info: 'var(--accent)',
  }

  return (
    <div style={{
      position: 'fixed',
      bottom: '20px',
      right: '20px',
      background: 'var(--surface)',
      border: `1px solid ${colors[variant]}`,
      borderRadius: 'var(--radius)',
      padding: '10px 16px',
      color: colors[variant],
      fontSize: '13px',
      zIndex: 1000,
      boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
    }}>
      {message}
    </div>
  )
}

export function useToast() {
  const [toast, setToast] = useState<{ message: string; variant: 'ok' | 'err' | 'info' } | null>(null)
  const show = (message: string, variant: 'ok' | 'err' | 'info' = 'info') => setToast({ message, variant })
  const close = () => setToast(null)
  return { toast, show, close }
}
