import { useQuery } from '@tanstack/react-query'

export async function fetchApi<T>(url: string, opts?: RequestInit): Promise<T> {
  const r = await fetch(url, { headers: { 'Content-Type': 'application/json' }, ...opts })
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`)
  return await r.json() as Promise<T>
}

export function useApiQuery<T>(
  key: string[],
  url: string,
  opts?: { enabled?: boolean; refetchInterval?: number }
) {
  return useQuery<T>({ queryKey: key, queryFn: () => fetchApi<T>(url), ...opts })
}
