import { Link, useRouterState } from "@tanstack/react-router"
import { useQuery } from "@tanstack/react-query"
import {
  LayoutDashboard,
  MessageSquare,
  Settings,
  Shield,
  Store,
  X,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { apiGet } from "@/core/api/client"
import { cn } from "@/lib/utils"
import { MODULE_PANELS } from "@/module-registry"

interface SidebarProps {
  collapsed: boolean
  mobileOpen: boolean
  onCloseMobile: () => void
}

type MenuItemResponse = {
  id: number
  name: string
  url: string
  icon_path: string
  icon_url: string | null
  order: number
}

const ICON_MAP = {
  LayoutDashboard,
  Settings,
  Store,
  MessageSquare,
} as const

export function Sidebar({
  collapsed,
  mobileOpen,
  onCloseMobile,
}: SidebarProps) {
  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  })
  const { data } = useQuery({
    queryKey: ["menu", "items"],
    queryFn: () => apiGet<{ items: MenuItemResponse[] }>("/api/menu/items"),
  })

  const panelByPath = new Map(
    MODULE_PANELS.map((panel) => [panel.path.replace(/\/+$/, "") || "/", panel]),
  )
  const menuPanels =
    data?.items
      .slice()
      .sort((a, b) => a.order - b.order)
      .map((item) => {
        const normalizedPath = item.url.replace(/\/+$/, "") || "/"
        const panel = panelByPath.get(normalizedPath)
        if (!panel) {
          return null
        }
        const mappedIcon = ICON_MAP[item.icon_path as keyof typeof ICON_MAP]
        return {
          ...panel,
          label: item.name,
          icon: mappedIcon ?? panel.icon,
        }
      })
      .filter((panel): panel is (typeof MODULE_PANELS)[number] => panel !== null) ?? MODULE_PANELS

  return (
    <>
      {mobileOpen ? (
        <button
          aria-label="Close navigation"
          className="fixed inset-0 z-30 bg-black/55 lg:hidden"
          onClick={onCloseMobile}
          type="button"
        />
      ) : null}
      <aside
        className={cn(
          "fixed inset-y-0 left-0 z-40 flex h-full flex-col border-r border-sidebar-border bg-sidebar/95 text-sidebar-foreground shadow-xl backdrop-blur transition-all duration-200 lg:relative lg:z-10 lg:border",
          collapsed ? "w-[56px]" : "w-[272px]",
          mobileOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0",
        )}
      >
        <div className="flex h-14 items-center border-b border-sidebar-border/80 px-3">
          <div
            className={cn(
              "flex w-full items-center gap-2 px-1 text-sidebar-foreground",
              collapsed ? "justify-center" : "justify-start",
            )}
          >
            <Shield className="size-4 text-primary" />
            {!collapsed ? <span className="text-sm font-medium">CyberSecSuite</span> : null}
          </div>
          <Button
            className="ml-1 h-8 w-8 shrink-0 text-sidebar-foreground hover:bg-sidebar-accent lg:hidden"
            onClick={onCloseMobile}
            size="icon"
            type="button"
            variant="ghost"
          >
            <X className="size-4" />
          </Button>
        </div>

        <ScrollArea className="flex-1 px-2 py-3">
          {!collapsed ? (
            <div className="px-2 pb-2 text-[10px] font-semibold uppercase tracking-[0.18em] text-sidebar-foreground/60">
              Platform
            </div>
          ) : null}
          <ul className="space-y-1">
            {menuPanels.map((panel) => {
              const Icon = panel.icon
              const isActive =
                panel.path === "/"
                  ? pathname === "/"
                  : pathname === panel.path || pathname.startsWith(`${panel.path}/`)

              const navItem = (
                <Link
                  className={cn(
                    "flex h-10 items-center gap-3 rounded-lg px-3 text-sm transition-colors",
                    isActive
                      ? "bg-sidebar-primary text-sidebar-primary-foreground shadow-sm"
                      : "text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                    collapsed ? "justify-center px-2" : "justify-start",
                  )}
                  onClick={onCloseMobile}
                  to={panel.path}
                >
                  <Icon className="size-4 shrink-0" />
                  {!collapsed ? (
                    <span className="truncate">
                      {panel.label}
                      {panel.badge ? (
                        <span className="ml-2 rounded bg-sidebar-accent px-1.5 py-0.5 text-xs text-sidebar-accent-foreground">
                          {panel.badge()}
                        </span>
                      ) : null}
                    </span>
                  ) : null}
                </Link>
              )

              return (
                <li key={panel.id}>
                  {collapsed ? (
                    <Tooltip>
                      <TooltipTrigger asChild>{navItem}</TooltipTrigger>
                      <TooltipContent side="right">{panel.label}</TooltipContent>
                    </Tooltip>
                  ) : (
                    navItem
                  )}
                </li>
              )
            })}
          </ul>
        </ScrollArea>
      </aside>
    </>
  )
}
