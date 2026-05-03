import { forwardRef } from 'react'
import type { InputHTMLAttributes } from 'react'
import { cn } from '@/libs/cn.ts'

const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement> & { label?: string }>(
  ({ label, className, style, ...rest }, ref) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {label && <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>{label}</label>}
      <input
        ref={ref}
        className={cn(className)}
        style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          color: 'var(--text-primary)',
          fontSize: '13px',
          padding: '7px 10px',
          outline: 'none',
          transition: 'border-color 0.15s',
          ...style,
        }}
        onFocus={e => (e.currentTarget.style.borderColor = 'var(--accent)')}
        onBlur={e => (e.currentTarget.style.borderColor = 'var(--border)')}
        {...rest}
      />
    </div>
  )
)
Input.displayName = 'Input'
export default Input
