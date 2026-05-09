import { Activity, Cpu, Database, ShieldCheck } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const WIDGETS = [
  { id: "system", title: "System Health", icon: ShieldCheck },
  { id: "agents", title: "Active Agents", icon: Cpu },
  { id: "events", title: "Recent Events", icon: Activity },
  { id: "models", title: "Model Usage", icon: Database },
]

export default function LandingDashboard() {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 2xl:grid-cols-4">
      {WIDGETS.map((widget) => {
        const Icon = widget.icon
        return (
          <Card key={widget.id}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">{widget.title}</CardTitle>
              <Icon className="size-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <p className="text-xs text-muted-foreground">
                Live data wiring pending.
              </p>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
