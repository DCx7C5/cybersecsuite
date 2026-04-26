import { useEffect, useState, useCallback } from 'react'

export interface Location {
  pathname: string
  search: string
  hash: string
  state?: Record<string, unknown>
}

export interface NavigationOptions {
  replace?: boolean
  state?: Record<string, unknown>
}

/**
 * Hook for accessing current location and navigation history
 * Provides pathname, search, hash, and navigation utilities
 */
export function useLocation(): Location {
  const [location, setLocation] = useState<Location>(() => ({
    pathname: window.location.pathname,
    search: window.location.search,
    hash: window.location.hash,
  }))

  useEffect(() => {
    const handlePopState = () => {
      setLocation({
        pathname: window.location.pathname,
        search: window.location.search,
        hash: window.location.hash,
      })
    }

    window.addEventListener('popstate', handlePopState)
    return () => window.removeEventListener('popstate', handlePopState)
  }, [])

  return location
}

/**
 * Hook for backward navigation in history
 */
export function useNavigateBack(): () => void {
  return useCallback(() => {
    window.history.back()
  }, [])
}

/**
 * Hook for forward navigation in history
 */
export function useNavigateForward(): () => void {
  return useCallback(() => {
    window.history.forward()
  }, [])
}

/**
 * Hook for programmatic navigation with deep linking support
 */
export function useNavigate(): (pathname: string, options?: NavigationOptions) => void {
  return useCallback((pathname: string, options?: NavigationOptions) => {
    const url = new URL(pathname, window.location.origin)
    if (options?.state) {
      window.history.replaceState(options.state, '', window.location.href)
    }
    if (options?.replace) {
      window.history.replaceState(null, '', url.toString())
    } else {
      window.history.pushState(null, '', url.toString())
    }
    window.dispatchEvent(new PopStateEvent('popstate'))
  }, [])
}

/**
 * Hook for getting and setting URL parameters
 */
export function useSearchParams(): [URLSearchParams, (params: URLSearchParams | Record<string, string>) => void] {
  const location = useLocation()
  const navigate = useNavigate()
  
  const searchParams = new URLSearchParams(location.search)
  
  const setSearchParams = useCallback((params: URLSearchParams | Record<string, string>) => {
    const newParams = params instanceof URLSearchParams ? params : new URLSearchParams(params)
    navigate(`${location.pathname}?${newParams.toString()}`)
  }, [location.pathname, navigate])

  return [searchParams, setSearchParams]
}

/**
 * Hook for deep linking with state persistence
 */
export function useDeepLink(key: string): [unknown, (value: unknown) => void] {
  const navigate = useNavigate()
  const location = useLocation()
  
  const [state, setState] = useState<unknown>(() => {
    const saved = sessionStorage.getItem(`deeplink-${key}`)
    return saved ? JSON.parse(saved) : null
  })

  const setDeepLinkState = useCallback((value: unknown) => {
    sessionStorage.setItem(`deeplink-${key}`, JSON.stringify(value))
    setState(value)
    navigate(location.pathname, { state: { [key]: value } })
  }, [key, location.pathname, navigate])

  return [state, setDeepLinkState]
}
