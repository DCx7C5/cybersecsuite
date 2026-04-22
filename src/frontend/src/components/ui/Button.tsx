import { cn } from '@/lib/cn'
import type { ButtonHTMLAttributes } from 'react'

const styles = {
  primary: {
    background: 'var(--accent)',
    color: '#fff',
    border: 'none',
  },
  ghost: {
    background: 'transparent',
    color: 'var(--text-primary)',
    border: '1px solid var(--border)',
  },
  danger: {
    background: 'var(--red-glow)',
    color: 'var(--red)',
    border: '1px solid var(--red)',
  },
  secondary: {
    background: 'var(--surface-2)',
    color: 'var(--text-primary)',
    border: '1px solid var(--border)',
  },
} as const

type Variant = keyof typeof styles

export default function Button({
  variant = 'primary',
  className,
  children,
  style,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant }) {
  return (
    <button
      className={cn(className)}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 14px',
        borderRadius: 'var(--radius)',
        fontSize: '13px',
        fontWeight: 500,
        cursor: 'pointer',
        transition: 'opacity 0.15s',
        ...styles[variant],
        ...style,
      }}
      {...rest}
    >
      {children}
    </button>
  )
}
