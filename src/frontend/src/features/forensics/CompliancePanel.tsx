import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'

interface FrameworkControl { id: string; name: string; status: string; score?: number }
interface ComplianceData { frameworks?: Array<{ name: string; score: number; controls?: FrameworkControl[] }> }
interface NistData { controls?: FrameworkControl[]; overall_score?: number }

export default function CompliancePanel() {
  const { data: compliance, isLoading } = useApiQuery<ComplianceData>(['compliance'], '/api/compliance')
  const { data: nistCsf } = useApiQuery<NistData>(['nist-csf'], '/api/nist-csf')
  const { data: nistAiRmf } = useApiQuery<NistData>(['nist-ai-rmf'], '/api/nist-ai-rmf')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>

  const frameworks = [
    { name: 'NIST CSF 2.0', score: nistCsf?.overall_score ?? 0 },
    { name: 'NIST AI RMF 1.0', score: nistAiRmf?.overall_score ?? 0 },
    ...(compliance?.frameworks ?? []),
  ]

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))', gap: '12px' }}>
        {frameworks.map(fw => (
          <Card key={fw.name}>
            <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>{fw.name}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ fontSize: '24px', fontWeight: 700, color: fw.score >= 80 ? 'var(--success)' : fw.score >= 50 ? 'var(--amber)' : 'var(--red)' }}>
                {fw.score}%
              </div>
              <div style={{ flex: 1, height: '6px', background: 'var(--surface-2)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{
                  width: `${fw.score}%`, height: '100%',
                  background: fw.score >= 80 ? 'var(--success)' : fw.score >= 50 ? 'var(--amber)' : 'var(--red)',
                  transition: 'width 0.3s ease',
                }} />
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}
