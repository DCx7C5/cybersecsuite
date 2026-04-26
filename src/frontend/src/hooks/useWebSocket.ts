import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
  type: 'worker_state_changed' | 'metrics_updated' | 'audit_logged'
  payload: Record<string, unknown>
  timestamp: number
}

interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onError?: (error: Error) => void
  autoConnect?: boolean
  batchIntervalMs?: number
  maxRetries?: number
}

export function useWebSocket(options: UseWebSocketOptions) {
  const {
    url,
    onMessage,
    onError,
    autoConnect = true,
    batchIntervalMs = 500,
    maxRetries = 5,
  } = options

  const wsRef = useRef<WebSocket | null>(null)
  const retriesRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const batchTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  const messageBufferRef = useRef<WebSocketMessage[]>([])

  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)

  const processBatch = useCallback(() => {
    if (messageBufferRef.current.length > 0) {
      messageBufferRef.current.forEach(msg => {
        onMessage?.(msg)
      })
      messageBufferRef.current = []
    }
  }, [onMessage])

  const scheduleBatchProcess = useCallback(() => {
    if (batchTimeoutRef.current) {
      clearTimeout(batchTimeoutRef.current)
    }
    batchTimeoutRef.current = setTimeout(processBatch, batchIntervalMs)
  }, [processBatch, batchIntervalMs])

  const connect = useCallback(() => {
    if (isConnecting || isConnected) return

    setIsConnecting(true)

    try {
      const wsUrl = url.startsWith('http') ? url.replace(/^http/, 'ws') : url
      wsRef.current = new WebSocket(wsUrl)

      wsRef.current.onopen = () => {
        setIsConnected(true)
        setIsConnecting(false)
        retriesRef.current = 0
      }

      wsRef.current.onmessage = (event: MessageEvent) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage
          messageBufferRef.current.push(message)
          scheduleBatchProcess()
        } catch (err) {
          onError?.(err instanceof Error ? err : new Error('Failed to parse message'))
        }
      }

      wsRef.current.onerror = () => {
        setIsConnected(false)
        setIsConnecting(false)
        onError?.(new Error('WebSocket error'))
      }

      wsRef.current.onclose = () => {
        setIsConnected(false)
        setIsConnecting(false)

        if (retriesRef.current < maxRetries) {
          retriesRef.current += 1
          const backoff = Math.min(1000 * Math.pow(2, retriesRef.current - 1), 10000)
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, backoff)
        }
      }
    } catch (err) {
      setIsConnecting(false)
      onError?.(err instanceof Error ? err : new Error('Failed to create WebSocket'))
    }
  }, [url, isConnecting, isConnected, onError, maxRetries, scheduleBatchProcess])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    if (batchTimeoutRef.current) {
      clearTimeout(batchTimeoutRef.current)
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setIsConnected(false)
    setIsConnecting(false)
  }, [])

  const send = useCallback((message: unknown) => {
    if (isConnected && wsRef.current) {
      wsRef.current.send(JSON.stringify(message))
    }
  }, [isConnected])

  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      processBatch()
      disconnect()
    }
  }, [autoConnect, connect, disconnect, processBatch])

  return {
    isConnected,
    isConnecting,
    send,
    disconnect,
    reconnect: connect,
  }
}

export function useWorkerUpdates(projectId: number) {
  const [updates, setUpdates] = useState<WebSocketMessage[]>([])

  const { isConnected } = useWebSocket({
    url: `/ws/workers/${projectId}`,
    onMessage: (message) => {
      setUpdates(prev => [...prev.slice(-99), message])
    },
  })

  return { updates, isConnected }
}
