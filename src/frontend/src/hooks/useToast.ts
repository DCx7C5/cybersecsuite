import { useState } from 'react'

export function useToast() {
  const [toast, setToast] = useState<{ message: string; variant: 'ok' | 'err' | 'info' } | null>(null)
  const show = (message: string, variant: 'ok' | 'err' | 'info' = 'info') => setToast({ message, variant })
  const close = () => setToast(null)
  return { toast, show, close }
}
