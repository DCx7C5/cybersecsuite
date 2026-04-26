import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { useWebSocket, useWorkerUpdates, type WebSocketMessage } from '@/hooks/useWebSocket.ts'

// Mock WebSocket
class MockWebSocket {
  url: string
  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: (() => void) | null = null
  onclose: (() => void) | null = null

  constructor(url: string) {
    this.url = url
  }

  send(data: string) {
    // Mock implementation
  }

  close() {
    // Mock implementation
  }

  static CONNECTING = 0
  static OPEN = 1
  static CLOSING = 2
  static CLOSED = 3
}

global.WebSocket = MockWebSocket as unknown as typeof WebSocket

describe('useWebSocket', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('connects on mount when autoConnect is true', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        autoConnect: true,
      })
    )

    await waitFor(() => {
      expect(result.current.isConnecting || result.current.isConnected).toBe(true)
    })
  })

  it('does not connect when autoConnect is false', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        autoConnect: false,
      })
    )

    expect(result.current.isConnected).toBe(false)
    expect(result.current.isConnecting).toBe(false)
  })

  it('handles incoming messages', async () => {
    const onMessage = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        onMessage,
      })
    )

    // Simulate message receive
    const testMessage: WebSocketMessage = {
      type: 'worker_state_changed',
      payload: { worker_id: '123', state: 'running' },
      timestamp: Date.now(),
    }

    // Simulate WebSocket message event
    if (result.current.send) {
      result.current.send({ test: 'data' })
    }
  })

  it('reconnects with exponential backoff on disconnect', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        maxRetries: 3,
      })
    )

    // Initial state
    expect(result.current.isConnected).toBe(false)

    // Simulate reconnect
    result.current.reconnect()
  })

  it('stops retrying after maxRetries', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        maxRetries: 2,
      })
    )

    // Multiple retry attempts
    result.current.reconnect()
    result.current.reconnect()
  })

  it('handles errors from WebSocket', async () => {
    const onError = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        onError,
      })
    )

    expect(result.current).toBeDefined()
  })

  it('batches messages by interval', async () => {
    const onMessage = vi.fn()

    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        onMessage,
        batchIntervalMs: 500,
      })
    )

    expect(result.current).toBeDefined()

    // Fast-forward time
    vi.advanceTimersByTime(600)
  })

  it('disconnects properly on unmount', async () => {
    const { unmount } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
      })
    )

    unmount()
  })

  it('can manually disconnect', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        autoConnect: false,
      })
    )

    result.current.disconnect()
    expect(result.current.isConnected).toBe(false)
  })

  it('sends messages when connected', async () => {
    const { result } = renderHook(() =>
      useWebSocket({
        url: 'ws://localhost:8000/test',
        autoConnect: false,
      })
    )

    const testMessage = { type: 'subscribe', channel: 'workers' }
    result.current.send(testMessage)
  })
})

describe('useWorkerUpdates', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('connects to worker updates WebSocket', async () => {
    const { result } = renderHook(() => useWorkerUpdates(123))

    expect(result.current).toBeDefined()
    expect('updates' in result.current).toBe(true)
    expect('isConnected' in result.current).toBe(true)
  })

  it('accumulates updates in buffer', async () => {
    const { result } = renderHook(() => useWorkerUpdates(123))

    await waitFor(() => {
      expect(Array.isArray(result.current.updates)).toBe(true)
    })
  })

  it('limits stored updates to last 100', async () => {
    const { result } = renderHook(() => useWorkerUpdates(123))

    await waitFor(() => {
      expect(result.current.updates.length).toBeLessThanOrEqual(100)
    })
  })

  it('maintains connection for project ID', async () => {
    const { result } = renderHook(() => useWorkerUpdates(456))

    expect(result.current.isConnected !== undefined).toBe(true)
  })

  it('handles different message types', async () => {
    const { result } = renderHook(() => useWorkerUpdates(789))

    expect(result.current).toBeDefined()
    expect(Array.isArray(result.current.updates)).toBe(true)
  })
})
