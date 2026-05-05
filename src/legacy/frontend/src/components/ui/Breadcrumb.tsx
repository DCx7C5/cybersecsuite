import type { ReactNode } from 'react'

export interface BreadcrumbItem {
  label: string
  href?: string
  icon?: ReactNode
  onClick?: () => void
}

interface BreadcrumbProps {
  items: BreadcrumbItem[]
  separator?: ReactNode
  maxItems?: number
}

export default function Breadcrumb({ items, separator = '/', maxItems = 5 }: BreadcrumbProps) {
  const displayItems = maxItems && items.length > maxItems
    ? [items[0], { label: '...', icon: null }, ...items.slice(-(maxItems - 1))]
    : items

  return (
    <nav
      data-testid="breadcrumb"
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        padding: '8px 12px',
        fontSize: '13px',
        color: 'var(--text-muted)',
      }}
      aria-label="Breadcrumb"
    >
      {displayItems.map((item, idx) => (
        <div
          key={`${item.label}-${idx}`}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
          }}
        >
          {idx > 0 && (
            <span
              style={{
                color: 'var(--text-faint)',
                margin: '0 2px',
              }}
            >
              {separator}
            </span>
          )}
          {item.href || item.onClick ? (
            <a
              href={item.href || '#'}
              onClick={(e) => {
                if (item.onClick) {
                  e.preventDefault()
                  item.onClick()
                }
              }}
              data-testid={`breadcrumb-item-${item.label}`}
              style={{
                color: 'var(--accent)',
                cursor: 'pointer',
                textDecoration: 'none',
                transition: 'color 0.15s',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
              onMouseEnter={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.color = 'var(--accent-bright)'
              }}
              onMouseLeave={(e) => {
                (e.currentTarget as HTMLAnchorElement).style.color = 'var(--accent)'
              }}
            >
              {item.icon && <span>{item.icon}</span>}
              <span>{item.label}</span>
            </a>
          ) : (
            <span
              data-testid={`breadcrumb-item-${item.label}`}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                color: 'var(--text-primary)',
              }}
            >
              {item.icon && <span>{item.icon}</span>}
              <span>{item.label}</span>
            </span>
          )}
        </div>
      ))}
    </nav>
  )
}
