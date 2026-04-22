import { useEffect, useRef } from 'react'

type EventListenerCallback = (event: Event) => void
type EventListenerElement = Window | Element | null

/**
 * Hook to attach event listeners with automatic cleanup
 *
 * Use for:
 * - Global keyboard shortcuts (⌘K search)
 * - Click-outside detection
 * - Resize, scroll, keydown events
 *
 * Benefits:
 * - Automatically removes listener on unmount (memory leak prevention)
 * - Stable callback using useRef
 * - Works with window or specific DOM elements
 *
 * @param eventType - Event to listen for (e.g., 'keydown', 'click')
 * @param callback - Function to call when event fires
 * @param element - Element to attach to (defaults to window)
 */
export function useEventListener(
  eventType: string,
  callback: EventListenerCallback,
  element: EventListenerElement = window
): void {
  const callbackRef = useRef<EventListenerCallback>(callback)

  // Update callback ref when callback changes (but don't re-attach listener)
  useEffect(() => {
    callbackRef.current = callback
  }, [callback])

  // Attach/detach listener
  useEffect(() => {
    if (element == null) return

    const handler = (event: Event) => callbackRef.current(event)
    element.addEventListener(eventType, handler)

    return () => element.removeEventListener(eventType, handler)
  }, [eventType, element])
}

export default useEventListener
