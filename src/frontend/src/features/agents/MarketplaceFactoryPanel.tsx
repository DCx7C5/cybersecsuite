import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Spinner from '@/components/ui/Spinner'

export default function MarketplaceFactoryPanel() {
  const [form, setForm] = useState({ name: '', description: '', type: '' })
  const [result, setResult] = useState<unknown>(null)

  const createMut = useMutation({
    mutationFn: () => fetchApi<unknown>('/api/marketplace/create', { method: 'POST', body: JSON.stringify(form) }),
    onSuccess: (data) => { setResult(data) }
  })

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Marketplace Agent Factory">
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <Input label="Name" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))} />
          <Input label="Description" value={form.description} onChange={e => setForm(f => ({ ...f, description: e.target.value }))} />
          <Input label="Type" value={form.type} onChange={e => setForm(f => ({ ...f, type: e.target.value }))} placeholder="agent | skill | workflow" />
          <Button onClick={() => createMut.mutate()} disabled={createMut.isPending || !form.name}>
            {createMut.isPending ? <Spinner size={14} /> : 'Create'}
          </Button>
        </div>
      </Card>
      {result != null && (
        <Card title="Result">
          <pre style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-primary)', whiteSpace: 'pre-wrap' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </Card>
      )}
    </div>
  )
}
