import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Table from '@/components/ui/Table'
import type { ColumnDef } from '@tanstack/react-table'

interface AuditEntry { id: string; action: string; resource: string; user?: string; created_at: string }
interface AuditData { entries?: AuditEntry[] }

export default function AuditPanel() {
  const { data, isLoading, error } = useApiQuery<AuditData>(['audit'], '/api/audit')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>
  if (error) return <div style={{ color: 'var(--red)', padding: '16px' }}>{String(error)}</div>

  const entries = data?.entries ?? []

  const columns: ColumnDef<AuditEntry>[] = [
    { accessorKey: 'id', header: 'ID' },
    { accessorKey: 'action', header: 'Action', cell: ({ getValue }) =>
      <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent)' }}>{getValue<string>()}</span>
    },
    { accessorKey: 'resource', header: 'Resource' },
    { accessorKey: 'user', header: 'User' },
    { accessorKey: 'created_at', header: 'Time' },
  ]

  return (
    <Card title="Audit Log">
      <Table data={entries} columns={columns} />
    </Card>
  )
}
