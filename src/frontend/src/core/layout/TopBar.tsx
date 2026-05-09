import { useEffect, useMemo, useRef, useState } from "react"
import { useIsFetching, useIsMutating, useMutationState } from "@tanstack/react-query"
import { useRouterState } from "@tanstack/react-router"
import { Loader2, Menu, PanelLeftClose, PanelLeftOpen } from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { MODULE_PANELS } from "@/module-registry"

interface TopBarProps {
  collapsed: boolean
  onToggleCollapsed: () => void
  onOpenMobileSidebar: () => void
}

type ActionStatusPhase = "hidden" | "running" | "fading" | "error_fading"

const NORMAL_FADE_MS = 2200
const ERROR_FADE_MS = 4200

export function TopBar({
  collapsed,
  onToggleCollapsed,
  onOpenMobileSidebar,
}: TopBarProps) {
  const [statusPhase, setStatusPhase] = useState<ActionStatusPhase>("hidden")
  const [errorMessage, setErrorMessage] = useState("Action failed")
  const fadeTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const handledErrorTimestampRef = useRef(0)

  const mutatingCount = useIsMutating()
  const fetchingCount = useIsFetching()
  const hasPendingActions = mutatingCount + fetchingCount > 0
  const failedMutations = useMutationState({
    filters: { status: "error" },
    select: (mutation) => ({
      submittedAt: mutation.state.submittedAt ?? 0,
      message:
        mutation.state.error instanceof Error
          ? mutation.state.error.message
          : "Action failed",
    }),
  })

  const latestFailedMutation = useMemo(
    () =>
      failedMutations.reduce<{ submittedAt: number; message: string } | null>(
        (latest, current) =>
          !latest || current.submittedAt > latest.submittedAt ? current : latest,
        null,
      ),
    [failedMutations],
  )

  useEffect(() => {
    if (hasPendingActions) {
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current)
        fadeTimerRef.current = null
      }
      setStatusPhase("running")
      return
    }

    if (
      latestFailedMutation &&
      latestFailedMutation.submittedAt > handledErrorTimestampRef.current
    ) {
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current)
      }
      handledErrorTimestampRef.current = latestFailedMutation.submittedAt
      setErrorMessage(latestFailedMutation.message)
      setStatusPhase("error_fading")
      fadeTimerRef.current = setTimeout(() => setStatusPhase("hidden"), ERROR_FADE_MS)
      return
    }

    if (statusPhase === "running") {
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current)
      }
      setStatusPhase("fading")
      fadeTimerRef.current = setTimeout(() => setStatusPhase("hidden"), NORMAL_FADE_MS)
    }
  }, [hasPendingActions, latestFailedMutation, statusPhase])

  useEffect(
    () => () => {
      if (fadeTimerRef.current) {
        clearTimeout(fadeTimerRef.current)
      }
    },
    [],
  )

  const pathname = useRouterState({
    select: (state) => state.location.pathname,
  })

  const breadcrumb = useMemo(() => {
    const matched = MODULE_PANELS.find((panel) =>
      panel.path === "/"
        ? pathname === "/"
        : pathname === panel.path || pathname.startsWith(`${panel.path}/`),
    )

    if (matched) {
      return matched.label
    }

    if (pathname === "/") {
      return "Dashboard"
    }

    return pathname
      .split("/")
      .filter(Boolean)
      .map((segment) => segment[0].toUpperCase() + segment.slice(1))
      .join(" / ")
  }, [pathname])

  return (
    <header className="z-20 flex h-14 items-center gap-2 rounded-xl border border-border bg-background px-3 md:px-4">
      <Button
        className="h-8 w-8 lg:hidden"
        onClick={onOpenMobileSidebar}
        size="icon"
        type="button"
        variant="ghost"
      >
        <Menu className="size-4" />
      </Button>
      <Button
        className="hidden h-8 w-8 lg:inline-flex"
        onClick={onToggleCollapsed}
        size="icon"
        type="button"
        variant="ghost"
      >
        {collapsed ? (
          <PanelLeftOpen className="size-4" />
        ) : (
          <PanelLeftClose className="size-4" />
        )}
      </Button>
      <div className="min-w-0 flex flex-1 items-center gap-2">
        <span className="truncate text-sm font-medium text-foreground">{breadcrumb}</span>
        {statusPhase !== "hidden" ? (
          <div
            className={cn(
              "inline-flex shrink-0 items-center gap-1.5 rounded-md border bg-transparent px-2 py-1 text-xs font-medium transition-opacity",
              statusPhase === "error_fading"
                ? "border-destructive/60 text-destructive duration-[4200ms]"
                : "border-amber-500/40 text-amber-300 duration-[2200ms]",
              statusPhase === "running" ? "opacity-100" : "opacity-0",
            )}
          >
            <Loader2 className="size-3.5 animate-spin" />
            <span>
              {statusPhase === "error_fading"
                ? errorMessage
                : statusPhase === "running"
                  ? "Processing…"
                  : "Completed"}
            </span>
          </div>
        ) : null}
      </div>
    </header>
  )
}
