/* eslint-disable react-hooks/set-state-in-effect */
/**
 * QoL Output Controls — React UI Panel
 *
 * This component provides a React UI for managing QoL (Quality of Life) output
 * control toggles. It displays current settings, allows users to modify them,
 * and persists changes to the backend via the /api/qol endpoint.
 *
 * Features:
 * - Display active toggles and their current state
 * - Toggle individual switches on/off
 * - Save changes to backend (persisted to ~/.cybersecsuite/data/qol.json)
 * - Real-time UI updates using TanStack Query (React Query)
 * - Loading spinner during fetch
 * - Error display if API call fails
 * - Disabled save button while request is in flight
 *
 * Props: None (uses hooks for state management)
 *
 * Hooks used:
 * - useState: local form state (reflecting backend settings)
 * - useEffect: sync fetched data to local state on mount
 * - useCallback: memoized save handler
 * - useApiQuery: fetch QoL settings from /api/qol
 * - useQueryClient: invalidate cache after save
 *
 * API Integration:
 * - GET /api/qol → fetch current settings
 * - POST /api/qol → save updated settings
 *
 * Styling:
 * - Uses CSS variables (--border, --text-primary, --success, etc.)
 * - Flexbox layout for toggle switches
 * - Card wrapper component with title and action button
 * - Inline styles (could be refactored to CSS modules)
 *
 * Error handling:
 * - Catches API errors and displays them
 * - Maintains UI state even if save fails
 * - Shows loading spinner during async operations
 *
 * Referenz:
 * - plan.md T009 — Phase 1 QoL Core (React UI)
 * - plan.md T010 — Testing & Compliance (expanded tests)
 * - src/dashboard/api/qol_endpoints.py — FastAPI endpoints
 * - src/ai_proxy/qol_controls/manager.py — backend manager
 * - src/hooks/useApi.ts — API query hook
 * - src/components/ui/Card.tsx — Card wrapper component
 * - src/components/ui/Button.tsx — Button component
 * - src/components/ui/Spinner.tsx — Loading spinner
 *
 * Status: production (Phase 1 complete)
 * Version: 1.0
 * Last modified: 2026-04-26 06:00:00Z
 * Author: frontend-developer
 */
import { useState, useEffect, useCallback } from 'react'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Button from '@/components/ui/Button'
import { useApiQuery, fetchApi } from '@/hooks/useApi'
import { useQueryClient } from '@tanstack/react-query'

interface QolData {
  settings?: Record<string, boolean | string | number>
}

export default function QolPanel() {
  const { data, isLoading, error } = useApiQuery<QolData>(['qol'], '/api/qol')
  const [local, setLocal] = useState<Record<string, boolean | string | number>>(() => data?.settings ?? {})
  const [saving, setSaving] = useState(false)
  const qc = useQueryClient()

  // TanStack Query: intentionally sync data to local state on mount
  useEffect(() => {
    if (data?.settings) setLocal(data.settings)
  }, [data?.settings])

  const save = useCallback(async () => {
    setSaving(true)
    try {
      await fetchApi('/api/qol', { method: 'POST', body: JSON.stringify(local) })
      await qc.invalidateQueries({ queryKey: ['qol'] })
    } finally {
      setSaving(false)
    }
  }, [local, qc])

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  return (
    <Card title="QoL Controls" actions={<Button onClick={() => { void save() }} disabled={saving}>{saving ? 'Saving…' : 'Save'}</Button>}>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {Object.entries(local).map(([key, val]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 0', borderBottom: '1px solid var(--border)' }}>
            <label style={{ fontSize: '13px', color: 'var(--text-primary)' }}>{key}</label>
            {typeof val === 'boolean' ? (
              <button
                onClick={() => setLocal(l => ({ ...l, [key]: !val }))}
                style={{
                  background: val ? 'var(--success-glow)' : 'var(--surface-2)',
                  color: val ? 'var(--success)' : 'var(--text-muted)',
                  border: `1px solid ${val ? 'var(--success)' : 'var(--border)'}`,
                  borderRadius: 'var(--radius)',
                  padding: '2px 12px',
                  fontSize: '11px',
                  cursor: 'pointer',
                }}
              >
                {val ? 'ON' : 'OFF'}
              </button>
            ) : (
              <input
                value={String(val)}
                onChange={e => setLocal(l => ({ ...l, [key]: e.target.value }))}
                style={{
                  background: 'var(--surface-2)',
                  border: '1px solid var(--border)',
                  borderRadius: 'var(--radius)',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  padding: '4px 8px',
                  outline: 'none',
                  width: '200px',
                }}
              />
            )}
          </div>
        ))}
        {Object.keys(local).length === 0 && <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No settings available</div>}
      </div>
    </Card>
  )
}
