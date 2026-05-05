import { useState } from 'react'
import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface ModelInfo { name: string; table?: string }
interface ModelsData { models?: ModelInfo[] }

interface TableRow { [key: string]: unknown }
interface TableData { rows?: TableRow[]; columns?: string[] }

export default function ExplorerPanel() {
  const { data: modelsData, isLoading: modelsLoading } = useApiQuery<ModelsData>(['explorer-models'], '/api/models')
  const [selectedModel, setSelectedModel] = useState<string>('')

  const { data: tableData, isLoading: tableLoading } = useApiQuery<TableData>(
    ['explorer-table', selectedModel],
    `/api/tables/${selectedModel}`,
    { enabled: !!selectedModel }
  )

  const models = modelsData?.models ?? []
  const rows = (tableData?.rows ?? []) as TableRow[]

  const columns: ColumnDef<TableRow>[] = (tableData?.columns ?? Object.keys(rows[0] ?? {})).map(col => ({
    accessorKey: col,
    header: col,
    cell: ({ getValue }) => {
      const v = getValue<unknown>()
      return <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{v == null ? '—' : String(v)}</span>
    },
  }))

  if (modelsLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Data Explorer">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginBottom: '16px' }}>
          <label style={{ fontSize: '12px', color: 'var(--text-muted)', fontWeight: 500 }}>Model</label>
          <select
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
            style={{ background: 'var(--surface-2)', border: '1px solid var(--border)', borderRadius: 'var(--radius)', color: 'var(--text-primary)', padding: '7px 10px', fontSize: '13px', maxWidth: '300px' }}
          >
            <option value="">Select a model…</option>
            {models.map(m => <option key={m.name} value={m.name}>{m.name}</option>)}
          </select>
        </div>
        {tableLoading && <Spinner />}
        {!tableLoading && selectedModel && (
          <Table data={rows} columns={columns} />
        )}
      </Card>
    </div>
  )
}
