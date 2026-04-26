import React, { useReducer, useCallback, ReactNode } from 'react'
import { 
  DataContext, 
  type DataContextType, 
  type SidebarState, 
  type MenuState, 
  type UIState,
  initialSidebarState,
  initialMenuState,
  initialUIState,
} from '@/context/DataContext'

// ============================================================================
// Actions
// ============================================================================

type Action =
  | { type: 'TOGGLE_COLLAPSED_GROUP'; payload: string }
  | { type: 'SELECT_ITEM'; payload: { groupId: string; itemId: string } }
  | { type: 'SET_SIDEBAR_OPEN'; payload: boolean }
  | { type: 'SET_SIDEBAR_WIDTH'; payload: number }
  | { type: 'SET_SIDEBAR_SEARCH_QUERY'; payload: string }
  | { type: 'SET_MENU_VISIBLE'; payload: boolean }
  | { type: 'SET_MENU_FOCUSED_INDEX'; payload: number }
  | { type: 'SET_MENU_ANIMATION_IN_PROGRESS'; payload: boolean }
  | { type: 'SET_DARK_MODE'; payload: boolean }
  | { type: 'SET_IS_MOBILE'; payload: boolean }
  | { type: 'SET_ANIMATIONS_ENABLED'; payload: boolean }
  | { type: 'RESET' }

interface State {
  sidebar: SidebarState
  menu: MenuState
  ui: UIState
}

// ============================================================================
// Reducer
// ============================================================================

const dataReducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'TOGGLE_COLLAPSED_GROUP': {
      const newCollapsed = new Set(state.sidebar.collapsedGroups)
      if (newCollapsed.has(action.payload)) {
        newCollapsed.delete(action.payload)
      } else {
        newCollapsed.add(action.payload)
      }
      return {
        ...state,
        sidebar: { ...state.sidebar, collapsedGroups: newCollapsed }
      }
    }

    case 'SELECT_ITEM':
      return {
        ...state,
        sidebar: { ...state.sidebar, selectedItem: action.payload }
      }

    case 'SET_SIDEBAR_OPEN':
      return {
        ...state,
        sidebar: { ...state.sidebar, isOpen: action.payload }
      }

    case 'SET_SIDEBAR_WIDTH':
      return {
        ...state,
        sidebar: { ...state.sidebar, width: action.payload }
      }

    case 'SET_SIDEBAR_SEARCH_QUERY':
      return {
        ...state,
        sidebar: { ...state.sidebar, searchQuery: action.payload }
      }

    case 'SET_MENU_VISIBLE':
      return {
        ...state,
        menu: { ...state.menu, isVisible: action.payload }
      }

    case 'SET_MENU_FOCUSED_INDEX':
      return {
        ...state,
        menu: { ...state.menu, focusedIndex: action.payload }
      }

    case 'SET_MENU_ANIMATION_IN_PROGRESS':
      return {
        ...state,
        menu: { ...state.menu, animationInProgress: action.payload }
      }

    case 'SET_DARK_MODE':
      return {
        ...state,
        ui: { ...state.ui, isDarkMode: action.payload }
      }

    case 'SET_IS_MOBILE':
      return {
        ...state,
        ui: { ...state.ui, isMobile: action.payload }
      }

    case 'SET_ANIMATIONS_ENABLED':
      return {
        ...state,
        ui: { ...state.ui, animationsEnabled: action.payload }
      }

    case 'RESET':
      return {
        sidebar: initialSidebarState,
        menu: initialMenuState,
        ui: initialUIState
      }

    default:
      return state
  }
}

// ============================================================================
// Context & Hook
// ============================================================================

export const DataProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(dataReducer, {
    sidebar: initialSidebarState,
    menu: initialMenuState,
    ui: initialUIState
  })

  const toggleCollapsedGroup = useCallback(
    (groupId: string) => {
      dispatch({ type: 'TOGGLE_COLLAPSED_GROUP', payload: groupId })
    },
    []
  )

  const selectItem = useCallback(
    (groupId: string, itemId: string) => {
      dispatch({ type: 'SELECT_ITEM', payload: { groupId, itemId } })
    },
    []
  )

  const setSidebarOpen = useCallback((isOpen: boolean) => {
    dispatch({ type: 'SET_SIDEBAR_OPEN', payload: isOpen })
  }, [])

  const setSidebarWidth = useCallback((width: number) => {
    dispatch({ type: 'SET_SIDEBAR_WIDTH', payload: width })
  }, [])

  const setSidebarSearchQuery = useCallback((query: string) => {
    dispatch({ type: 'SET_SIDEBAR_SEARCH_QUERY', payload: query })
  }, [])

  const setMenuVisible = useCallback((isVisible: boolean) => {
    dispatch({ type: 'SET_MENU_VISIBLE', payload: isVisible })
  }, [])

  const setMenuFocusedIndex = useCallback((index: number) => {
    dispatch({ type: 'SET_MENU_FOCUSED_INDEX', payload: index })
  }, [])

  const setMenuAnimationInProgress = useCallback((inProgress: boolean) => {
    dispatch({ type: 'SET_MENU_ANIMATION_IN_PROGRESS', payload: inProgress })
  }, [])

  const setDarkMode = useCallback((isDarkMode: boolean) => {
    dispatch({ type: 'SET_DARK_MODE', payload: isDarkMode })
  }, [])

  const setIsMobile = useCallback((isMobile: boolean) => {
    dispatch({ type: 'SET_IS_MOBILE', payload: isMobile })
  }, [])

  const setAnimationsEnabled = useCallback((enabled: boolean) => {
    dispatch({ type: 'SET_ANIMATIONS_ENABLED', payload: enabled })
  }, [])

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' })
  }, [])

  const value: DataContextType = {
    sidebar: state.sidebar,
    menu: state.menu,
    ui: state.ui,
    toggleCollapsedGroup,
    selectItem,
    setSidebarOpen,
    setSidebarWidth,
    setSidebarSearchQuery,
    setMenuVisible,
    setMenuFocusedIndex,
    setMenuAnimationInProgress,
    setDarkMode,
    setIsMobile,
    setAnimationsEnabled,
    reset
  }

  return (
    <DataContext.Provider value={value}>
      {children}
    </DataContext.Provider>
  )
}

export type { SidebarState, MenuState, UIState, DataContextType }
