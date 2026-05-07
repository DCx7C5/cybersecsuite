import React from 'react'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'

interface MarketplaceStatusProps {
  hasUpdates?: boolean
  updateCount?: number
  onCheck?: () => void
  isChecking?: boolean
}

/**
 * MarketplaceStatus — displays marketplace update badge and status.
 * Shows when updates are available for installed packages.
 */
export default function MarketplaceStatus({
  hasUpdates = false,
  updateCount = 0,
  onCheck,
  isChecking = false,
}: MarketplaceStatusProps) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {hasUpdates && (
        <Badge variant="warning">
          {updateCount > 0 ? `${updateCount} update${updateCount !== 1 ? 's' : ''}` : 'Updates available'}
        </Badge>
      )}
      {onCheck && (
        <Button
          variant="ghost"
          onClick={onCheck}
          disabled={isChecking}
          style={{ fontSize: '11px', padding: '4px 10px' }}
        >
          {isChecking ? 'Checking...' : 'Check for updates'}
        </Button>
      )}
    </div>
  )
}
