import { useApiQuery } from './useApi.ts'

export interface WorkerResponse {
  id: number
  worker_id: string
  name: string
  description: string
  worker_type: string
  current_state: string
  config: Record<string, unknown>
  project_id: number
  session_id: string
  steps_executed: number
  total_duration_ms: number
  start_time: string
  last_activity_at: string
}

export interface WorkersListResponse {
  data: WorkerResponse[]
  total: number
  page: number
  limit: number
}

interface UseWorkersOptions {
  page?: number
  limit?: number
  search?: string
  state?: string
  sort?: string
  enabled?: boolean
}

export function useWorkers(
  projectId: number,
  options: UseWorkersOptions = {}
) {
  const { page = 1, limit = 50, search = '', state = '', sort = 'name', enabled = true } = options

  const params = new URLSearchParams()
  params.append('page', page.toString())
  params.append('limit', limit.toString())
  if (search) params.append('search', search)
  if (state) params.append('state', state)
  if (sort) params.append('sort', sort)

  const url = `/api/projects/${projectId}/workers?${params.toString()}`

  return useApiQuery<WorkersListResponse>(
    ['workers', projectId, page, limit, search, state, sort],
    url,
    { enabled }
  )
}

export function useWorkerDetail(projectId: number, workerId: number) {
  return useApiQuery<WorkerResponse>(
    ['worker', projectId, workerId],
    `/api/projects/${projectId}/workers/${workerId}`
  )
}

export interface WorkerMetrics {
  worker_id: string
  step_count: number
  success_rate: number
  avg_duration_ms: number
  current_state: string
  uptime_ms: number
}

export function useWorkerMetrics(projectId: number, workerId: number) {
  return useApiQuery<WorkerMetrics>(
    ['worker-metrics', projectId, workerId],
    `/api/projects/${projectId}/workers/${workerId}/metrics`
  )
}

export interface WorkerSummary {
  project_id: number
  total_workers: number
  running: number
  paused: number
  completed: number
  failed: number
  queued: number
  avg_step_count: number
  avg_success_rate: number
}

export function useWorkersSummary(projectId: number) {
  return useApiQuery<WorkerSummary>(
    ['workers-summary', projectId],
    `/api/projects/${projectId}/workers/summary`
  )
}
