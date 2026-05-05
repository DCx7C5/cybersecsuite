import { forwardRef } from 'react'
import type { SelectHTMLAttributes, ReactNode } from 'react'

const Select = forwardRef<HTMLSelectElement, SelectHTMLAttributes<HTMLSelectElement> & { label?: string; children?: ReactNode }>(
  ({ label, style, children, ...rest }, ref) => (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
      {label && <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>{label}</label>}
      <select
        ref={ref}
        style={{
          background: 'var(--surface-2)',
          border: '1px solid var(--border)',
          borderRadius: 'var(--radius)',
          color: 'var(--text-primary)',
          fontSize: '13px',
          padding: '7px 10px',
          outline: 'none',
          cursor: 'pointer',
          ...style,
        }}
        {...rest}
      >
        {children}
      </select>
    </div>
  )
)
Select.displayName = 'Select'
export default Select
