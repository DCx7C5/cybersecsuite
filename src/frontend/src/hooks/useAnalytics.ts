import { useQuery } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'

interface AnalyticsData {
  success_rate: number
  avg_runtime_ms: number
  throughput: number
  total_executions: number
  state_distribution: {
    queued: number
    running: number
    paused: number
    completed: number
    failed: number
  }
  error_rate: number
}

export function useAnalytics(dateRange: string = '7d', filters: Record<string, string> = {}) {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics', dateRange, filters],
    queryFn: () => {
      const params = new URLSearchParams()
      params.append('range', dateRange)
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value)
      })
      return fetchApi<AnalyticsData>(`/api/analytics?${params.toString()}`)
    },
    refetchInterval: 30000,
  })

  const mockData: AnalyticsData = {
    success_rate: 98.5,
    avg_runtime_ms: 245,
    throughput: 1240,
    total_executions: 8674,
    state_distribution: {
      queued: 234,
      running: 12,
      paused: 0,
      completed: 8401,
      failed: 27,
    },
    error_rate: 1.5,
  }

  return {
    data: data || mockData,
    isLoading,
  }
}
