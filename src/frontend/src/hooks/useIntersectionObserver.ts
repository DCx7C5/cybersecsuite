import { useState, useEffect } from 'react'
import type { RefObject } from 'react'

/**
 * Hook to detect when an element enters/exits the viewport
 *
 * Use for:
 * - Lazy loading panels/images when scrolled into view
 * - Infinite scroll pagination
 * - Performance optimization (only render when visible)
 *
 * Benefits:
 * - Uses browser Intersection Observer API (efficient)
 * - Returns boolean (true = element is visible)
 * - Configurable via IntersectionObserverInit options
 *
 * @param ref - Ref to the element to observe
 * @param options - IntersectionObserver options (threshold, root, rootMargin)
 * @returns True if element is in viewport, false otherwise
 *
 * @example
 * const ref = useRef<HTMLDivElement>(null)
 * const isVisible = useIntersectionObserver(ref, { threshold: 0.1 })
 * return (
 *   <div ref={ref}>
 *     {isVisible ? <ExpensiveComponent /> : <Spinner />}
 *   </div>
 * )
 */
export function useIntersectionObserver(
  ref: RefObject<Element>,
  options?: IntersectionObserverInit
): boolean {
  const [intersecting, setIntersecting] = useState<boolean>(false)

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]: IntersectionObserverEntry[]) => {
        setIntersecting(entry.isIntersecting)
      },
      {
        threshold: 0.1, // Default: trigger when 10% visible
        ...options,
      }
    )

    if (ref.current) {
      observer.observe(ref.current)
    }

    return () => {
      observer.disconnect()
    }
  }, [ref, options])

  return intersecting
}

export default useIntersectionObserver
