export default function StatusBar() {
  return (
    <div style={{
      height: '24px',
      background: 'var(--bg-deep)',
      borderTop: '1px solid var(--border)',
      display: 'flex',
      alignItems: 'center',
      padding: '0 16px',
      fontSize: '11px',
      color: 'var(--text-faint)',
      gap: '16px',
      flexShrink: 0,
    }}>
      <span>CyberSecSuite</span>
      <span>●</span>
      <span>Ready</span>
    </div>
  )
}
