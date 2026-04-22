import { useEffect, useRef, useCallback } from 'react'

export function useSSE(
  url: string | null,
  onMessage: (event: MessageEvent) => void,
  onError?: (e: Event) => void
) {
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    if (!url) return
    const es = new EventSource(url)
    esRef.current = es
    es.onmessage = onMessage
    if (onError) es.onerror = onError
    return () => { es.close(); esRef.current = null }
  }, [url, onMessage, onError])

  const close = useCallback(() => { esRef.current?.close() }, [])
  return { close }
}
