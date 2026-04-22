export const NAV_GROUPS: Record<string, { label: string; icon: string; collapsible: boolean; defaultOpen: boolean }> = {
  platform: { label: 'PLATFORM', icon: '📊', collapsible: false, defaultOpen: true },
  proxy: { label: 'AI PROXY', icon: '⚙️', collapsible: false, defaultOpen: true },
  agents: { label: 'AGENTS', icon: '🤖', collapsible: true, defaultOpen: true },
  ops: { label: 'OPERATIONS', icon: '⚡', collapsible: true, defaultOpen: false },
  forensics: { label: 'INVESTIGATIONS', icon: '🔍', collapsible: true, defaultOpen: false },
  data: { label: 'INTEL & STORAGE', icon: '📈', collapsible: false, defaultOpen: true },
  settings: { label: 'SETTINGS', icon: '⚙️', collapsible: false, defaultOpen: true },
}

export interface NavItem {
  id: string
  label: string
  icon: string
  group: string
}

export const NAV_ITEMS: NavItem[] = [
  // PLATFORM
  { id: 'health', label: 'Health', icon: 'Heart', group: 'platform' },
  { id: 'usage', label: 'Usage & Cost', icon: 'Activity', group: 'platform' },
  { id: 'telemetry', label: 'Telemetry', icon: 'Signal', group: 'platform' },
  { id: 'providers-hub', label: 'Provider Hub', icon: 'Globe', group: 'platform' },

  // AI PROXY
  { id: 'routing', label: 'Routing', icon: 'Route', group: 'proxy' },
  { id: 'qol-controls', label: 'QoL Controls', icon: 'Sliders', group: 'proxy' },

  // AGENTS
  { id: 'chat', label: 'Chat', icon: 'MessageCircle', group: 'agents' },
  { id: 'agent-factory', label: 'Agent Factory', icon: 'Boxes', group: 'agents' },
  { id: 'agent-crafter', label: 'Agent Crafter', icon: 'Wand', group: 'agents' },
  { id: 'team-builder', label: 'Team Builder', icon: 'Users', group: 'agents' },
  { id: 'agent-query', label: 'Agent Query', icon: 'Search', group: 'agents' },
  { id: 'workflows', label: 'Workflows', icon: 'GitBranch', group: 'agents' },
  { id: 'flowgraph', label: 'Flowgraph', icon: 'GitGraph', group: 'agents' },
  { id: 'prompts', label: 'Prompts', icon: 'BookOpen', group: 'agents' },
  { id: 'sdk-lab', label: 'SDK Lab', icon: 'Code', group: 'agents' },
  { id: 'marketplace', label: 'Marketplace', icon: 'Store', group: 'agents' },
  { id: 'marketplace-factory', label: 'Agent Factory ⊕', icon: 'Plus', group: 'agents' },

  // OPERATIONS
  { id: 'cases', label: 'Cases', icon: 'Briefcase', group: 'ops' },
  { id: 'tasks', label: 'Tasks', icon: 'CheckSquare', group: 'ops' },
  { id: 'pocs', label: 'PoCs', icon: 'Lightbulb', group: 'ops' },
  { id: 'a2a', label: 'A2A Proto', icon: 'Link', group: 'ops' },

  // INVESTIGATIONS (FORENSICS)
  { id: 'investigations', label: 'Investigations', icon: 'Magnifier', group: 'forensics' },
  { id: 'findings', label: 'Findings', icon: 'Flag', group: 'forensics' },
  { id: 'iocs', label: 'IOCs', icon: 'AlertTriangle', group: 'forensics' },
  { id: 'yara', label: 'YARA Rules', icon: 'Shield', group: 'forensics' },
  { id: 'intel', label: 'Intel Feed', icon: 'Zap', group: 'forensics' },
  { id: 'audit', label: 'Audit Log', icon: 'LogIn', group: 'forensics' },
  { id: 'compliance', label: 'Compliance', icon: 'CheckCircle', group: 'forensics' },

  // INTEL & STORAGE
  { id: 'opensearch', label: 'OpenObserve', icon: 'Database', group: 'data' },
  { id: 'explorer', label: 'Explorer', icon: 'FolderOpen', group: 'data' },
  { id: 'templates', label: 'Templates', icon: 'Layout', group: 'data' },

  // SETTINGS
  { id: 'settings', label: 'Claude SDK', icon: 'Settings', group: 'settings' },
  { id: 'settings-cybersecsuite', label: 'CyberSecSuite', icon: 'Cpu', group: 'settings' },
]
