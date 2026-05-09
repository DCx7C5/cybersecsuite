import {
  Component,
  type ErrorInfo,
  type PropsWithChildren,
  Suspense,
} from "react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"

type BoundaryState = {
  hasError: boolean
}

class PanelErrorBoundary extends Component<PropsWithChildren, BoundaryState> {
  public state: BoundaryState = { hasError: false }

  public static getDerivedStateFromError(): BoundaryState {
    return { hasError: true }
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // eslint-disable-next-line no-console
    console.error("Panel render failed", error, errorInfo)
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex h-full min-h-80 flex-col items-center justify-center gap-4 rounded-md border border-destructive/40 bg-card p-6 text-card-foreground">
          <p className="text-sm text-muted-foreground">
            Panel rendering failed.
          </p>
          <Button onClick={() => window.location.reload()} type="button">
            Retry
          </Button>
        </div>
      )
    }
    return this.props.children
  }
}

function PanelSkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-8 w-56" />
      <Skeleton className="h-20 w-full" />
      <Skeleton className="h-60 w-full" />
    </div>
  )
}

export function PanelContainer({ children }: PropsWithChildren) {
  return (
    <PanelErrorBoundary>
      <Suspense fallback={<PanelSkeleton />}>{children}</Suspense>
    </PanelErrorBoundary>
  )
}
