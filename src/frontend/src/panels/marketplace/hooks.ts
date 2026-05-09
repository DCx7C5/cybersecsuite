import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { apiGet, apiPost } from "@/core/api/client"
import type {
  InstallToolResponse,
  MarketplaceKind,
  MarketplaceListResponse,
  MarketplacePreviewResponse,
  MarketplaceReseedResponse,
  MarketplaceStatusResponse,
  ToggleToolResponse,
  MarketplaceUpdateCheckResponse,
  UninstallToolResponse,
} from "@/panels/marketplace/types"

const MARKETPLACE_PREFIX = "/api/marketplace"
const TOOLS_QUERY_KEY = ["marketplace", "tools"] as const
const INSTALLED_QUERY_KEY = ["marketplace", "installed-tools"] as const
const STATUS_QUERY_KEY = ["marketplace", "status"] as const
const PREVIEW_QUERY_KEY = ["marketplace", "preview"] as const

function buildListPath({
  kind,
  installedOnly = false,
  enabledOnly = false,
  page = 1,
  perPage = 50,
}: {
  kind?: MarketplaceKind
  installedOnly?: boolean
  enabledOnly?: boolean
  page?: number
  perPage?: number
}): string {
  const search = new URLSearchParams()
  if (kind && kind !== "all") {
    search.set("kind", kind)
  }
  if (installedOnly) {
    search.set("installed_only", "true")
  }
  if (enabledOnly) {
    search.set("enabled_only", "true")
  }
  search.set("page", String(page))
  search.set("per_page", String(perPage))
  return `${MARKETPLACE_PREFIX}/items?${search.toString()}`
}

export function useMarketplaceTools(
  kind?: MarketplaceKind,
  options?: { page?: number; perPage?: number; enabled?: boolean },
) {
  const page = options?.page ?? 1
  const perPage = options?.perPage ?? 50
  return useQuery({
    queryKey: [...TOOLS_QUERY_KEY, kind ?? "all", page, perPage],
    enabled: options?.enabled ?? true,
    queryFn: () =>
      apiGet<MarketplaceListResponse>(
        buildListPath({
          kind,
          page,
          perPage,
        }),
      ),
  })
}

export function useInstalledTools(options?: {
  kind?: MarketplaceKind
  page?: number
  perPage?: number
  enabled?: boolean
}) {
  const page = options?.page ?? 1
  const perPage = options?.perPage ?? 50
  return useQuery({
    queryKey: [...INSTALLED_QUERY_KEY, options?.kind ?? "all", page, perPage],
    enabled: options?.enabled ?? true,
    queryFn: () =>
      apiGet<MarketplaceListResponse>(
        buildListPath({
          kind: options?.kind,
          installedOnly: true,
          page,
          perPage,
        }),
      ),
  })
}

export function useInstallTool() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) =>
      apiPost<InstallToolResponse>(`${MARKETPLACE_PREFIX}/items/install`, {
        item_id: itemId,
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: TOOLS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: INSTALLED_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: STATUS_QUERY_KEY }),
      ])
    },
  })
}

export function useUninstallTool() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (itemId: string) =>
      apiPost<UninstallToolResponse>(`${MARKETPLACE_PREFIX}/items/uninstall`, {
        item_id: itemId,
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: TOOLS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: INSTALLED_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: STATUS_QUERY_KEY }),
      ])
    },
  })
}

export function useToggleTool() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ itemId, enabled }: { itemId: string; enabled: boolean }) =>
      apiPost<ToggleToolResponse>(`${MARKETPLACE_PREFIX}/items/toggle`, {
        item_id: itemId,
        enabled,
      }),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: TOOLS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: INSTALLED_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: STATUS_QUERY_KEY }),
      ])
    },
  })
}

export function useMarketplaceStatus() {
  return useQuery({
    queryKey: STATUS_QUERY_KEY,
    queryFn: () => apiGet<MarketplaceStatusResponse>(`${MARKETPLACE_PREFIX}/status`),
  })
}

export function useMarketplaceUpdateCheck() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () =>
      apiPost<MarketplaceUpdateCheckResponse>(`${MARKETPLACE_PREFIX}/update-check`),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: STATUS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: TOOLS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: INSTALLED_QUERY_KEY }),
      ])
    },
  })
}

export function useMarketplaceReseed() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: () =>
      apiPost<MarketplaceReseedResponse>(`${MARKETPLACE_PREFIX}/reseed?force=true`),
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: STATUS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: TOOLS_QUERY_KEY }),
        queryClient.invalidateQueries({ queryKey: INSTALLED_QUERY_KEY }),
      ])
    },
  })
}

export function useMarketplaceItemPreview(itemId: string | null, enabled: boolean) {
  return useQuery({
    queryKey: [...PREVIEW_QUERY_KEY, itemId ?? "none"],
    enabled: enabled && Boolean(itemId),
    queryFn: () =>
      apiGet<MarketplacePreviewResponse>(`${MARKETPLACE_PREFIX}/items/${itemId}/preview`),
  })
}
