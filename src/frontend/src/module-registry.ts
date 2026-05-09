import { lazy, type ComponentType, type LazyExoticComponent } from "react"
import type { LucideIcon } from "lucide-react"
import {
  LayoutDashboard,
  MessageSquare,
  Settings,
  Store,
} from "lucide-react"

type PanelComponent = LazyExoticComponent<ComponentType>

export interface ModulePanel {
  id: string
  label: string
  icon: LucideIcon
  path: string
  component: PanelComponent
  badge?: () => string
}

export const MODULE_PANELS: ModulePanel[] = [
  {
    id: "dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
    path: "/",
    component: lazy(() => import("@/pages/LandingDashboard")),
  },
  {
    id: "settings",
    label: "Settings",
    icon: Settings,
    path: "/settings",
    component: lazy(() => import("@css/core/settings/templates")),
  },
  {
    id: "marketplace",
    label: "Marketplace",
    icon: Store,
    path: "/marketplace",
    component: lazy(() => import("@css/core/marketplace/templates")),
  },
  {
    id: "chat",
    label: "Chat",
    icon: MessageSquare,
    path: "/chat",
    component: lazy(() => import("@css/modules/chat/templates")),
  },
]
