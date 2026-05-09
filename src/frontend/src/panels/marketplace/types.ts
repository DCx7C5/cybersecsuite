export type MarketplaceKind =
  | "agent"
  | "skill"
  | "mcp"
  | "prompt"
  | "workflow"
  | "template"
  | "team"
  | string

export interface MarketplaceTool {
  id: string
  name: string
  description: string
  kind: MarketplaceKind
  status: string
  enabled: boolean
  installed: boolean
  version: string
  tags: string[]
  model?: string
  max_turns?: number
  tools_count?: number
  repository_url?: string
  source_url?: string | null
  install_path?: string | null
}

export interface MarketplaceListResponse {
  items: MarketplaceTool[]
  total: number
  page: number
  per_page: number
}

export interface InstallToolResponse {
  success: boolean
  item_id: string
  message: string
  installed_path?: string | null
  error?: string | null
}

export interface UninstallToolResponse {
  success: boolean
  item_id: string
  message: string
  error?: string | null
}

export interface ToggleToolResponse {
  success: boolean
  item_id: string
  enabled: boolean
  message: string
  error?: string | null
}

export interface MarketplaceStatusResponse {
  total_items: number
  installed_items: number
  enabled_items: number
  update_available: boolean
  last_index_check: string | null
  remote_index_hash: string | null
  local_index_hash: string | null
  version: string | null
}

export interface MarketplaceUpdateCheckResponse {
  update_available: boolean
  version: string | null
  remote_index_hash: string | null
  local_index_hash: string | null
}

export interface MarketplaceReseedResponse {
  success: boolean
  created: number
  skipped: number
  force: boolean
}

export interface MarketplacePreviewResponse {
  item_id: string
  markdown: string
  install_path: string
}
