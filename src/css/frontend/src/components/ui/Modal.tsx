import * as Dialog from '@radix-ui/react-dialog'
import type { ReactNode } from 'react'
import Button from './Button'

export default function Modal({
  open,
  onClose,
  title,
  children,
}: {
  open: boolean
  onClose: () => void
  title: string
  children: ReactNode
}) {
  return (
    <Dialog.Root open={open} onOpenChange={(o) => !o && onClose()}>
      <Dialog.Portal>
        <Dialog.Overlay style={{
          position: 'fixed', inset: 0,
          background: 'rgba(0,0,0,0.6)',
          zIndex: 100,
        }} />
        <Dialog.Content style={{
          position: 'fixed', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          background: 'var(--surface)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius-lg)',
          padding: '24px',
          minWidth: '480px',
          maxWidth: '90vw',
          maxHeight: '90vh',
          overflow: 'auto',
          zIndex: 101,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
            <Dialog.Title style={{ fontWeight: 600, fontSize: '15px', color: 'var(--text-primary)', margin: 0 }}>
              {title}
            </Dialog.Title>
            <Button variant="ghost" onClick={onClose} style={{ padding: '4px 8px' }}>✕</Button>
          </div>
          {children}
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
