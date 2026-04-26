import * as RQ from '@tanstack/react-query'
export const queryClient = new RQ.QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
  },
})
