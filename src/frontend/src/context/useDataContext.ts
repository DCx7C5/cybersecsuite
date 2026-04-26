import { useContext } from 'react'
import { DataContext, type DataContextType } from './DataContext'

export const useData = (): DataContextType => {
  const context = useContext(DataContext)
  if (!context) {
    throw new Error('useData must be used within DataProvider')
  }
  return context
}

export const useSidebarState = () => {
  const { sidebar, toggleCollapsedGroup, selectItem, setSidebarOpen, setSidebarWidth, setSidebarSearchQuery } = useData()
  return { sidebar, toggleCollapsedGroup, selectItem, setSidebarOpen, setSidebarWidth, setSidebarSearchQuery }
}

export const useMenuState = () => {
  const { menu, setMenuVisible, setMenuFocusedIndex, setMenuAnimationInProgress } = useData()
  return { menu, setMenuVisible, setMenuFocusedIndex, setMenuAnimationInProgress }
}

export const useUIState = () => {
  const { ui, setDarkMode, setIsMobile, setAnimationsEnabled } = useData()
  return { ui, setDarkMode, setIsMobile, setAnimationsEnabled }
}
