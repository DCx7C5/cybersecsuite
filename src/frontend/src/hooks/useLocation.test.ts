import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import {
  useLocation,
  useNavigateBack,
  useNavigateForward,
  useNavigate,
  useSearchParams,
  useDeepLink,
} from '../../hooks/useLocation'

describe('Router Integration - t105: useLocation Hook', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
  })

  it('should return current location', () => {
    const { result } = renderHook(() => useLocation())
    expect(result.current.pathname).toBe('/')
    expect(typeof result.current.search).toBe('string')
    expect(typeof result.current.hash).toBe('string')
  })

  it('should update on history changes', async () => {
    const { result } = renderHook(() => useLocation())
    
    act(() => {
      window.history.pushState({}, '', '/dashboard')
      window.dispatchEvent(new PopStateEvent('popstate'))
    })

    expect(result.current.pathname).toBe('/dashboard')
  })

  it('should handle search parameters', () => {
    window.history.pushState({}, '', '/?search=test&filter=active')
    const { result } = renderHook(() => useLocation())
    
    expect(result.current.search).toBe('?search=test&filter=active')
  })

  it('should handle hash fragments', () => {
    window.history.pushState({}, '', '/#section')
    const { result } = renderHook(() => useLocation())
    
    expect(result.current.hash).toBe('#section')
  })
})

describe('Router Integration - t106: Back/Forward Navigation', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
  })

  it('should navigate backward in history', async () => {
    window.history.pushState({}, '', '/page1')
    window.history.pushState({}, '', '/page2')
    
    const { result } = renderHook(() => useNavigateBack())
    
    const backSpy = vi.spyOn(window.history, 'back')
    act(() => {
      result.current()
    })
    
    expect(backSpy).toHaveBeenCalled()
    backSpy.mockRestore()
  })

  it('should navigate forward in history', async () => {
    const { result } = renderHook(() => useNavigateForward())
    
    const forwardSpy = vi.spyOn(window.history, 'forward')
    act(() => {
      result.current()
    })
    
    expect(forwardSpy).toHaveBeenCalled()
    forwardSpy.mockRestore()
  })
})

describe('Router Integration - t107: Deep Linking', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
    sessionStorage.clear()
  })

  it('should support deep linking with state', async () => {
    const { result } = renderHook(() => useDeepLink('test'))
    
    act(() => {
      result.current[1]({ id: '123', name: 'Test' })
    })

    expect(result.current[0]).toEqual({ id: '123', name: 'Test' })
  })

  it('should persist deep link state to sessionStorage', async () => {
    const { result } = renderHook(() => useDeepLink('investigation'))
    
    act(() => {
      result.current[1]({ caseId: 'case-123' })
    })

    const stored = sessionStorage.getItem('deeplink-investigation')
    expect(JSON.parse(stored!)).toEqual({ caseId: 'case-123' })
  })

  it('should restore deep link state on mount', () => {
    sessionStorage.setItem('deeplink-suspect', JSON.stringify({ id: 'suspect-456' }))
    
    const { result } = renderHook(() => useDeepLink('suspect'))
    
    expect(result.current[0]).toEqual({ id: 'suspect-456' })
  })
})

describe('Router Integration - t108: URL Parameter Handling', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/')
  })

  it('should read search parameters', () => {
    window.history.pushState({}, '', '/?tab=forensics&sort=date')
    const { result } = renderHook(() => useSearchParams())
    
    expect(result.current[0].get('tab')).toBe('forensics')
    expect(result.current[0].get('sort')).toBe('date')
  })

  it('should set search parameters', async () => {
    window.history.pushState({}, '', '/')
    const { result } = renderHook(() => useSearchParams())
    
    act(() => {
      result.current[1]({ search: 'malware', filter: 'critical' })
    })

    expect(result.current[0].get('search')).toBe('malware')
    expect(result.current[0].get('filter')).toBe('critical')
  })

  it('should handle URLSearchParams directly', async () => {
    window.history.pushState({}, '', '/')
    const { result } = renderHook(() => useSearchParams())
    
    const params = new URLSearchParams()
    params.set('page', '2')
    params.set('limit', '50')
    
    act(() => {
      result.current[1](params)
    })

    expect(result.current[0].get('page')).toBe('2')
    expect(result.current[0].get('limit')).toBe('50')
  })

  it('should support multiple values per parameter', () => {
    window.history.pushState({}, '', '/?tag=urgent&tag=malware&tag=critical')
    const { result } = renderHook(() => useSearchParams())
    
    const tags = result.current[0].getAll('tag')
    expect(tags).toEqual(['urgent', 'malware', 'critical'])
  })

  it('should handle empty parameters gracefully', () => {
    window.history.pushState({}, '', '/search')
    const { result } = renderHook(() => useSearchParams())
    
    expect(result.current[0].toString()).toBe('')
  })
})
