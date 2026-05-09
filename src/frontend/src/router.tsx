import {
  createRootRoute,
  createRoute,
  createRouter,
} from "@tanstack/react-router"
import AppShell from "@/core/layout/AppShell"
import { PanelContainer } from "@/core/layout/PanelContainer"
import { MODULE_PANELS } from "@/module-registry"

const rootRoute = createRootRoute({
  component: AppShell,
})

const panelRoutes = MODULE_PANELS.map((panel) =>
  createRoute({
    getParentRoute: () => rootRoute,
    path: panel.path,
    component: () => {
      const Component = panel.component
      return (
        <PanelContainer>
          <Component />
        </PanelContainer>
      )
    },
  }),
)

const routeTree = rootRoute.addChildren(panelRoutes)

export const router = createRouter({
  routeTree,
  defaultPreload: "intent",
  defaultPreloadStaleTime: 0,
  trailingSlash: "always",
})

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router
  }
}
