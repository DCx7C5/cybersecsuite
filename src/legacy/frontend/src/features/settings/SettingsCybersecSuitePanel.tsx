import { useApiQuery } from '@/hooks/useApi'
import Card from '@/components/ui/Card'
import Spinner from '@/components/ui/Spinner'
import Badge from '@/components/ui/Badge'

interface GlobalSettings { workspace?: string; project?: string; db_host?: string; version?: string }
interface EnvEntry { key: string; value: string }
interface EnvData { env?: EnvEntry[] }
interface BootstrapStatus { bootstrapped?: boolean; last_run?: string; status?: string }

export default function SettingsCybersecSuitePanel() {
  const { data: global, isLoading } = useApiQuery<GlobalSettings>(['settings-global'], '/api/settings/global')
  const { data: globalEnv } = useApiQuery<EnvData>(['settings-global-env'], '/api/settings/global-env')
  const { data: projectEnv } = useApiQuery<EnvData>(['settings-project-env'], '/api/settings/project-env')
  const { data: bootstrap } = useApiQuery<BootstrapStatus>(['bootstrap-status'], '/api/bootstrap/status')

  if (isLoading) return <div style={{ display: 'flex', justifyContent: 'center', padding: '40px' }}><Spinner /></div>

  const globalEnvEntries = globalEnv?.env ?? []
  const projectEnvEntries = projectEnv?.env ?? []

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <Card title="Global Settings">
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '12px' }}>
          {Object.entries(global ?? {}).map(([k, v]) => (
            <div key={k}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginBottom: '2px', textTransform: 'uppercase' }}>{k}</div>
              <div style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>{String(v ?? '—')}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card title="Bootstrap Status">
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <Badge variant={bootstrap?.bootstrapped ? 'ok' : 'warn'}>{bootstrap?.bootstrapped ? 'Bootstrapped' : 'Not Bootstrapped'}</Badge>
          {bootstrap?.status && <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>{bootstrap.status}</span>}
          {bootstrap?.last_run && <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Last run: {bootstrap.last_run}</span>}
        </div>
      </Card>

      <Card title="Global Environment">
        {globalEnvEntries.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {globalEnvEntries.map((e: any) => (
              <div key={e.key} style={{ display: 'flex', gap: '12px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent)', minWidth: '200px' }}>{e.key}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)' }}>{e.value}</span>
              </div>
            ))}
          </div>
        ) : <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No global env vars</div>}
      </Card>

      <Card title="Project Environment">
        {projectEnvEntries.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            {projectEnvEntries.map((e: any) => (
              <div key={e.key} style={{ display: 'flex', gap: '12px', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--accent)', minWidth: '200px' }}>{e.key}</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)' }}>{e.value}</span>
              </div>
            ))}
          </div>
        ) : <div style={{ color: 'var(--text-muted)', fontSize: '13px' }}>No project env vars</div>}
      </Card>
    </div>
  )
}
