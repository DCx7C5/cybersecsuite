export const NAV_GROUPS: Record<string, string | null> = {
  platform: 'PLATFORM',
  proxy: 'AI PROXY',
  agents: 'AGENTS',
  ops: 'OPERATIONS',
  forensics: 'FORENSICS',
  data: 'DATA',
  settings: null,
}

export interface NavItem {
  id: string
  label: string
  icon: string
  group: string
}

export const NAV_ITEMS: NavItem[] = [
  { id: 'chat',                  label: 'Chat',              icon: '💬', group: 'agents' },
  { id: 'health',                label: 'Health',            icon: '♡',  group: 'platform' },
  { id: 'usage',                 label: 'Usage & Cost',      icon: '◈',  group: 'platform' },
  { id: 'telemetry',             label: 'Telemetry',         icon: '◉',  group: 'platform' },
  { id: 'providers-hub',         label: 'Provider Hub',      icon: '⊞',  group: 'platform' },
  { id: 'routing',               label: 'Routing',           icon: '⇄',  group: 'proxy' },
  { id: 'qol-controls',          label: 'QoL Controls',      icon: '⊘',  group: 'proxy' },
  { id: 'agent-factory',         label: 'Agent Factory',     icon: '⊞',  group: 'agents' },
  { id: 'agent-crafter',         label: 'Agent Crafter',     icon: '✎',  group: 'agents' },
  { id: 'team-builder',          label: 'Team Builder',      icon: '⊟',  group: 'agents' },
  { id: 'agent-query',           label: 'Agent Query',       icon: '⇒',  group: 'agents' },
  { id: 'workflows',             label: 'Workflows',         icon: '⇌',  group: 'agents' },
  { id: 'flowgraph',             label: 'Flowgraph',         icon: '⬡',  group: 'agents' },
  { id: 'prompts',               label: 'Prompts',           icon: '⊘',  group: 'agents' },
  { id: 'sdk-lab',               label: 'SDK Lab',           icon: '⊗',  group: 'agents' },
  { id: 'marketplace',           label: 'Marketplace',       icon: '⊞',  group: 'agents' },
  { id: 'marketplace-factory',   label: 'Agent Factory ⊕',  icon: '⊕',  group: 'agents' },
  { id: 'cases',                 label: 'Cases',             icon: '⊡',  group: 'ops' },
  { id: 'tasks',                 label: 'Tasks',             icon: '⊛',  group: 'ops' },
  { id: 'pocs',                  label: 'PoCs',              icon: '⊕',  group: 'ops' },
  { id: 'a2a',                   label: 'A2A Proto',         icon: '⇋',  group: 'ops' },
  { id: 'investigations',        label: 'Investigations',    icon: '◉',  group: 'forensics' },
  { id: 'findings',              label: 'Findings',          icon: '⊘',  group: 'forensics' },
  { id: 'iocs',                  label: 'IOCs',              icon: '◈',  group: 'forensics' },
  { id: 'yara',                  label: 'YARA Rules',        icon: '⊛',  group: 'forensics' },
  { id: 'intel',                 label: 'Intel Feed',        icon: '◎',  group: 'forensics' },
  { id: 'audit',                 label: 'Audit Log',         icon: '⊕',  group: 'forensics' },
  { id: 'compliance',            label: 'Compliance',        icon: '⊗',  group: 'forensics' },
  { id: 'opensearch',            label: 'OpenObserve',       icon: '⊘',  group: 'data' },
  { id: 'explorer',              label: 'Explorer',          icon: '⊡',  group: 'data' },
  { id: 'templates',             label: 'Templates',         icon: '◫',  group: 'data' },
  { id: 'settings',              label: 'Claude',            icon: '◈',  group: 'settings' },
  { id: 'settings-cybersecsuite',label: 'CyberSecSuite',     icon: '◉',  group: 'settings' },
]
