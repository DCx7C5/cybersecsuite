import { useState, useEffect } from 'react'

type BreakPoint = 'xs' | 'sm' | 'md' | 'lg' | 'xl'

/**
 * Hook to track responsive breakpoints
 * xs: < 480px
 * sm: 480px–768px (mobile landscape)
 * md: 768px–1024px (tablet)
 * lg: 1024px–1280px (small desktop)
 * xl: ≥ 1280px (full desktop)
 *
 * Use for conditional rendering, sidebar collapse, etc.
 * @returns Current breakpoint
 */
export function useBreakPoint(): BreakPoint {
  const [screenSize, setScreenSize] = useState<BreakPoint>(getCurrentBreakpoint())

  function getCurrentBreakpoint(): BreakPoint {
    const width = window.innerWidth
    if (width < 480) return 'xs'
    if (width < 768) return 'sm'
    if (width < 1024) return 'md'
    if (width < 1280) return 'lg'
    return 'xl'
  }

  useEffect(() => {
    const handleResize = () => {
      setScreenSize(getCurrentBreakpoint())
    }

    window.addEventListener('resize', handleResize)
    return () => {
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return screenSize
}

export default useBreakPoint
