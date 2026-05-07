import React from 'react'
import Button from '@/components/ui/Button'
import Spinner from '@/components/ui/Spinner'

interface InstallPackageButtonProps {
  packageId: string
  packageName: string
  onInstall: (packageId: string) => Promise<void>
  isInstalling?: boolean
  isInstalled?: boolean
  error?: string | null
}

/**
 * InstallPackageButton — handles package installation with loading and error states.
 * Shows different UI based on installation status.
 */
export default function InstallPackageButton({
  packageId,
  packageName,
  onInstall,
  isInstalling = false,
  isInstalled = false,
  error = null,
}: InstallPackageButtonProps) {
  const [localError, setLocalError] = React.useState<string | null>(error)

  const handleClick = async () => {
    try {
      setLocalError(null)
      await onInstall(packageId)
    } catch (err) {
      setLocalError(err instanceof Error ? err.message : 'Installation failed')
    }
  }

  if (isInstalled) {
    return (
      <div style={{ color: 'var(--text-success)', fontSize: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
        ✓ Installed
      </div>
    )
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
      <Button
        variant="primary"
        onClick={handleClick}
        disabled={isInstalling}
        style={{
          fontSize: '11px',
          padding: '6px 12px',
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          justifyContent: 'center',
        }}
      >
        {isInstalling && <Spinner size="small" />}
        {isInstalling ? 'Installing...' : `Install ${packageName}`}
      </Button>
      {(error || localError) && (
        <div style={{ color: 'var(--text-error)', fontSize: '11px' }}>
          {error || localError}
        </div>
      )}
    </div>
  )
}
