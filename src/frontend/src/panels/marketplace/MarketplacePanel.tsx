import { useEffect, useMemo, useState } from "react"
import { useRouterState } from "@tanstack/react-router"
import {
  ChevronLeft,
  ChevronRight,
  Loader2,
  Search,
  Sparkles,
  Wrench,
} from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import {
  useInstallTool,
  useInstalledTools,
  useMarketplaceItemPreview,
  useMarketplaceReseed,
  useMarketplaceStatus,
  useMarketplaceTools,
  useMarketplaceUpdateCheck,
  useToggleTool,
  useUninstallTool,
} from "@/panels/marketplace/hooks"
import type { MarketplaceKind, MarketplaceTool } from "@/panels/marketplace/types"

const PER_PAGE = 50

type MarketplaceTab = "marketplace" | "installed"

const KIND_FILTERS: Array<{ label: string; value: MarketplaceKind }> = [
  { label: "Agents", value: "agent" },
  { label: "Skills", value: "skill" },
  { label: "MCPs", value: "mcp" },
  { label: "Workflows", value: "workflow" },
  { label: "Teams", value: "team" },
  { label: "Templates", value: "template" },
  { label: "Prompts", value: "prompt" },
]

const API_KIND_FILTERS = new Set<MarketplaceKind>([
  "agent",
  "skill",
  "mcp",
  "workflow",
  "template",
  "prompt",
])

function matchesKind(item: MarketplaceTool, kind: MarketplaceKind): boolean {
  if (kind === "team") {
    const fields = [item.id, item.name, item.description, ...item.tags]
    return fields.some((value) => value.toLowerCase().includes("team"))
  }
  return item.kind === kind
}

function matchesQuery(item: MarketplaceTool, query: string): boolean {
  if (!query) {
    return true
  }
  const normalized = query.toLowerCase()
  return (
    item.name.toLowerCase().includes(normalized) ||
    item.description.toLowerCase().includes(normalized) ||
    item.kind.toLowerCase().includes(normalized) ||
    item.tags.some((tag) => tag.toLowerCase().includes(normalized))
  )
}

function kindLabel(kind: string): string {
  if (kind === "mcp") {
    return "MCPs"
  }
  return kind[0]?.toUpperCase() + kind.slice(1)
}

interface PaginatorProps {
  page: number
  totalPages: number
  onPageChange: (nextPage: number) => void
}

function Paginator({ page, totalPages, onPageChange }: PaginatorProps) {
  return (
    <div className="flex flex-wrap items-center justify-between gap-2 rounded-md border border-border/70 px-3 py-2">
      <span className="text-xs text-muted-foreground">
        Page {page} of {totalPages}
      </span>
      <div className="flex items-center gap-2">
        <span className="text-xs text-muted-foreground">Go to page</span>
        <select
          className="h-8 rounded-md border border-input bg-background px-2 text-xs"
          onChange={(event) => onPageChange(Number(event.target.value))}
          value={String(page)}
        >
          {Array.from({ length: totalPages }, (_, index) => index + 1).map((pageOption) => (
            <option key={pageOption} value={pageOption}>
              {pageOption}
            </option>
          ))}
        </select>
        <Button
          className="h-8"
          disabled={page <= 1}
          onClick={() => onPageChange(page - 1)}
          size="sm"
          type="button"
          variant="outline"
        >
          <ChevronLeft className="mr-1 size-4" />
          Previous
        </Button>
        <Button
          className="h-8"
          disabled={page >= totalPages}
          onClick={() => onPageChange(page + 1)}
          size="sm"
          type="button"
          variant="outline"
        >
          Next
          <ChevronRight className="ml-1 size-4" />
        </Button>
      </div>
    </div>
  )
}

export default function MarketplacePanel() {
  const searchState = useRouterState({
    select: (state) => state.location.searchStr,
  })
  const [activeTab, setActiveTab] = useState<MarketplaceTab>("marketplace")
  const [search, setSearch] = useState("")
  const [kindFilter, setKindFilter] = useState<MarketplaceKind>("agent")
  const [marketplacePage, setMarketplacePage] = useState(1)
  const [installedPage, setInstalledPage] = useState(1)
  const [previewOpen, setPreviewOpen] = useState(false)
  const [previewItemId, setPreviewItemId] = useState<string | null>(null)

  const apiKindFilter = API_KIND_FILTERS.has(kindFilter) ? kindFilter : undefined

  useEffect(() => {
    const params = new URLSearchParams(searchState)
    const tabValue = params.get("tab")
    const kindValue = params.get("kind")
    if (tabValue === "installed" || tabValue === "marketplace") {
      setActiveTab(tabValue)
    }
    if (kindValue && KIND_FILTERS.some((filter) => filter.value === kindValue)) {
      setKindFilter(kindValue)
    }
  }, [searchState])

  useEffect(() => {
    if (activeTab === "marketplace") {
      setMarketplacePage(1)
      return
    }
    setInstalledPage(1)
  }, [activeTab, kindFilter, search])

  const toolsQuery = useMarketplaceTools(apiKindFilter, {
    page: marketplacePage,
    perPage: PER_PAGE,
    enabled: activeTab === "marketplace",
  })
  const installedQuery = useInstalledTools({
    kind: apiKindFilter,
    page: installedPage,
    perPage: PER_PAGE,
    enabled: activeTab === "installed",
  })

  const agentsTotalQuery = useMarketplaceTools("agent", { perPage: 1 })
  const skillsTotalQuery = useMarketplaceTools("skill", { perPage: 1 })
  const mcpsTotalQuery = useMarketplaceTools("mcp", { perPage: 1 })
  const workflowsTotalQuery = useMarketplaceTools("workflow", { perPage: 1 })
  const templatesTotalQuery = useMarketplaceTools("template", { perPage: 1 })
  const promptsTotalQuery = useMarketplaceTools("prompt", { perPage: 1 })

  const statusQuery = useMarketplaceStatus()
  const updateCheckMutation = useMarketplaceUpdateCheck()
  const installMutation = useInstallTool()
  const uninstallMutation = useUninstallTool()
  const toggleMutation = useToggleTool()
  const reseedMutation = useMarketplaceReseed()
  const previewQuery = useMarketplaceItemPreview(previewItemId, previewOpen)

  useEffect(() => {
    updateCheckMutation.mutate()
    // run once when panel mounts
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const marketplaceItems = toolsQuery.data?.items ?? []
  const installedItems = installedQuery.data?.items ?? []

  const visibleMarketplaceTools = useMemo(
    () =>
      marketplaceItems.filter(
        (item) => matchesKind(item, kindFilter) && matchesQuery(item, search),
      ),
    [kindFilter, marketplaceItems, search],
  )
  const visibleInstalledTools = useMemo(
    () =>
      installedItems.filter(
        (item) => matchesKind(item, kindFilter) && matchesQuery(item, search),
      ),
    [kindFilter, installedItems, search],
  )

  const categoryTotals: Record<string, number> = useMemo(
    () => ({
      agent: agentsTotalQuery.data?.total ?? 0,
      skill: skillsTotalQuery.data?.total ?? 0,
      mcp: mcpsTotalQuery.data?.total ?? 0,
      workflow: workflowsTotalQuery.data?.total ?? 0,
      template: templatesTotalQuery.data?.total ?? 0,
      prompt: promptsTotalQuery.data?.total ?? 0,
      team: marketplaceItems.filter((item) => matchesKind(item, "team")).length,
    }),
    [
      agentsTotalQuery.data?.total,
      marketplaceItems,
      mcpsTotalQuery.data?.total,
      promptsTotalQuery.data?.total,
      skillsTotalQuery.data?.total,
      templatesTotalQuery.data?.total,
      workflowsTotalQuery.data?.total,
    ],
  )

  const globalTotalCount = useMemo(
    () => Object.values(categoryTotals).reduce((sum, value) => sum + value, 0),
    [categoryTotals],
  )

  const activePage = activeTab === "marketplace" ? marketplacePage : installedPage
  const setActivePage =
    activeTab === "marketplace" ? setMarketplacePage : setInstalledPage
  const activeTools = activeTab === "marketplace" ? visibleMarketplaceTools : visibleInstalledTools
  const marketplaceTotal = toolsQuery.data?.total ?? 0
  const installedTotal = installedQuery.data?.total ?? 0
  const activeTotal = activeTab === "marketplace" ? marketplaceTotal : installedTotal
  const totalPages = Math.max(1, Math.ceil(activeTotal / PER_PAGE))
  const showPagination = activeTotal > PER_PAGE || activePage > 1
  const activeLoading = activeTab === "marketplace" ? toolsQuery.isLoading : installedQuery.isLoading
  const activeError = activeTab === "marketplace" ? toolsQuery.isError : installedQuery.isError

  const busyItemId = installMutation.isPending
    ? installMutation.variables
    : uninstallMutation.isPending
      ? uninstallMutation.variables
      : toggleMutation.isPending
        ? toggleMutation.variables.itemId
        : undefined

  const remoteHash = updateCheckMutation.data?.remote_index_hash ?? statusQuery.data?.remote_index_hash
  const localHash = updateCheckMutation.data?.local_index_hash ?? statusQuery.data?.local_index_hash
  const hashesDiffer = Boolean(remoteHash) && Boolean(localHash) && remoteHash !== localHash
  const hasUpdates = Boolean(
    (updateCheckMutation.data?.update_available ?? statusQuery.data?.update_available) ||
      hashesDiffer,
  )

  return (
    <div className="space-y-6">
      <header className="space-y-3">
        <div className="flex flex-wrap items-center gap-2">
          <Wrench className="size-4 text-primary" />
          <h1 className="text-xl font-semibold">Marketplace</h1>
          <Badge variant="secondary">{globalTotalCount}</Badge>
          <Badge variant="outline">v{statusQuery.data?.version ?? "n/a"}</Badge>
          <Button
            className={cn(
              "h-8",
              hasUpdates
                ? "border-emerald-500/50 bg-emerald-600 text-white hover:bg-emerald-500"
                : "border-border text-muted-foreground",
            )}
            disabled={reseedMutation.isPending || updateCheckMutation.isPending || !hasUpdates}
            onClick={() => reseedMutation.mutate()}
            size="sm"
            type="button"
            variant={hasUpdates ? "default" : "outline"}
          >
            {reseedMutation.isPending ? (
              <>
                <Loader2 className="mr-1 size-4 animate-spin" />
                Upgrading index…
              </>
            ) : updateCheckMutation.isPending ? (
              <>
                <Loader2 className="mr-1 size-4 animate-spin" />
                Checking updates…
              </>
            ) : hasUpdates ? (
              <>
                <Sparkles className="mr-1 size-4" />
                Upgrade packages
              </>
            ) : (
              "No updates available"
            )}
          </Button>
        </div>
      </header>

      <section className="space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <Button
            className="h-8"
            onClick={() => setActiveTab("installed")}
            size="sm"
            type="button"
            variant={activeTab === "installed" ? "default" : "outline"}
          >
            Installed ({statusQuery.data?.installed_items ?? 0})
          </Button>
          <Button
            className="h-8"
            onClick={() => setActiveTab("marketplace")}
            size="sm"
            type="button"
            variant={activeTab === "marketplace" ? "default" : "outline"}
          >
            Marketplace ({globalTotalCount})
          </Button>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {KIND_FILTERS.map((filter) => (
            <Button
              className="h-8"
              key={filter.value}
              onClick={() => setKindFilter(filter.value)}
              size="sm"
              type="button"
              variant={kindFilter === filter.value ? "default" : "outline"}
            >
              {filter.label} ({categoryTotals[filter.value] ?? 0})
            </Button>
          ))}
        </div>

        <div className="relative max-w-md">
          <Search className="absolute left-2.5 top-2.5 size-4 text-muted-foreground" />
          <Input
            className="pl-8"
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search tools, description, or tags"
            value={search}
          />
        </div>
      </section>

      {showPagination ? (
        <Paginator page={activePage} totalPages={totalPages} onPageChange={setActivePage} />
      ) : null}

      <section className="grid grid-cols-1 gap-4 xl:grid-cols-2 2xl:grid-cols-3">
        {activeLoading ? (
          <Card className="col-span-full">
            <CardContent className="flex h-28 items-center justify-center text-sm text-muted-foreground">
              Loading items…
            </CardContent>
          </Card>
        ) : null}

        {activeError ? (
          <Card className="col-span-full border-destructive/40">
            <CardContent className="flex h-28 items-center text-sm text-destructive">
              Failed to load items.
            </CardContent>
          </Card>
        ) : null}

        {!activeLoading && !activeError && activeTools.length === 0 ? (
          <Card className="col-span-full">
            <CardContent className="flex h-28 items-center justify-center text-sm text-muted-foreground">
              No items match the current filters.
            </CardContent>
          </Card>
        ) : null}

        {activeTools.map((tool) => {
          const isBusy = busyItemId === tool.id
          const isInstalled = tool.installed

          return (
            <Card key={`${activeTab}-${tool.id}`}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <CardTitle className="truncate text-base">{tool.name}</CardTitle>
                    <CardDescription className="line-clamp-2 pt-1">
                      {tool.description}
                    </CardDescription>
                  </div>
                  <Badge variant="secondary">{kindLabel(tool.kind)}</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex flex-wrap gap-1.5">
                  {tool.tags.slice(0, 4).map((tag) => (
                    <Badge className="text-[11px]" key={tag} variant="outline">
                      {tag}
                    </Badge>
                  ))}
                </div>
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="text-xs text-muted-foreground">v{tool.version}</span>
                  <div className="flex flex-wrap items-center gap-2">
                    <Button
                      className={cn(
                        "min-w-24 text-white",
                        isInstalled
                          ? "bg-rose-600 hover:bg-rose-500"
                          : "bg-sky-600 hover:bg-sky-500",
                      )}
                      disabled={isBusy}
                      onClick={() =>
                        isInstalled
                          ? uninstallMutation.mutate(tool.id)
                          : installMutation.mutate(tool.id)
                      }
                      size="sm"
                      type="button"
                    >
                      {isBusy ? (
                        <Loader2 className="size-4 animate-spin" />
                      ) : isInstalled ? (
                        "Uninstall"
                      ) : (
                        "Install"
                      )}
                    </Button>

                    {activeTab === "installed" ? (
                      <>
                        <Button
                          className={cn(
                            "min-w-24 text-white",
                            tool.enabled
                              ? "bg-amber-600 hover:bg-amber-500"
                              : "bg-emerald-600 hover:bg-emerald-500",
                          )}
                          disabled={isBusy}
                          onClick={() =>
                            toggleMutation.mutate({
                              itemId: tool.id,
                              enabled: !tool.enabled,
                            })
                          }
                          size="sm"
                          type="button"
                        >
                          {tool.enabled ? "Disable" : "Enable"}
                        </Button>
                        <Button
                          className="min-w-24"
                          disabled={isBusy}
                          onClick={() => {
                            setPreviewItemId(tool.id)
                            setPreviewOpen(true)
                          }}
                          size="sm"
                          type="button"
                          variant="outline"
                        >
                          Vorschau
                        </Button>
                      </>
                    ) : null}
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </section>

      {showPagination ? (
        <Paginator page={activePage} totalPages={totalPages} onPageChange={setActivePage} />
      ) : null}

      <Dialog onOpenChange={setPreviewOpen} open={previewOpen}>
        <DialogContent className="sm:max-w-4xl">
          <DialogHeader>
            <DialogTitle>Vorschau</DialogTitle>
            <DialogDescription>
              Installed markdown preview for {previewItemId ?? "selected item"}.
            </DialogDescription>
          </DialogHeader>
          <div className="max-h-[65vh] overflow-auto rounded-md border border-border/70 bg-muted/25 p-3">
            {previewQuery.isLoading ? (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                Loading preview…
              </div>
            ) : previewQuery.isError ? (
              <p className="text-sm text-destructive">Failed to load preview.</p>
            ) : (
              <pre className="whitespace-pre-wrap break-words text-xs leading-relaxed">
                {previewQuery.data?.markdown ?? ""}
              </pre>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
