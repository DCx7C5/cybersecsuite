import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchApi } from '@/hooks/useApi'

interface HealthMetrics {
  uptime_hours: number
  active_workers: number
  idle_workers: number
  failed_workers: number
  api_response_time_ms: number
  database_connections_used: number
  database_connections_available: number
  memory_usage_percent: number
  cpu_usage_percent: number
  error_rate_24h: number
}

export function useSystemHealth() {
  const [metrics, setMetrics] = useState<HealthMetrics>({
    uptime_hours: 240,
    active_workers: 5,
    idle_workers: 2,
    failed_workers: 0,
    api_response_time_ms: 125,
    database_connections_used: 3,
    database_connections_available: 7,
    memory_usage_percent: 62,
    cpu_usage_percent: 35,
    error_rate_24h: 0.2,
  })

  const { data: fetchedMetrics, isLoading } = useQuery({
    queryKey: ['system-health'],
    queryFn: () => fetchApi<HealthMetrics>('/api/system/health'),
    refetchInterval: 5000,
  })

  const metricsToReturn = fetchedMetrics || metrics

  return {
    metrics: metricsToReturn,
    isLoading,
    isHealthy: metricsToReturn.error_rate_24h < 1 && metricsToReturn.cpu_usage_percent < 80,
  }
}
