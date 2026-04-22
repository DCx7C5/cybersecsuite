import { cn } from '@/lib/cn'
import type { ReactNode } from 'react'

const variants = {
  ok: { background: 'var(--success-glow)', color: 'var(--success)', border: '1px solid var(--success)' },
  err: { background: 'var(--red-glow)', color: 'var(--red)', border: '1px solid var(--red)' },
  warn: { background: 'var(--amber-glow)', color: 'var(--amber)', border: '1px solid var(--amber)' },
  info: { background: 'var(--accent-glow)', color: 'var(--accent)', border: '1px solid var(--accent)' },
  muted: { background: 'var(--surface-2)', color: 'var(--text-muted)', border: '1px solid var(--border)' },
} as const

type Variant = keyof typeof variants

export default function Badge({ variant = 'info', children, className }: {
  variant?: Variant
  children: ReactNode
  className?: string
}) {
  return (
    <span
      className={cn(className)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        padding: '2px 8px',
        borderRadius: 'var(--radius)',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.02em',
        ...variants[variant],
      }}
    >
      {children}
    </span>
  )
}
