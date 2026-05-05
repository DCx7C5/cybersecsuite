import { createContext } from 'react'

export interface SidebarState {
  collapsedGroups: Set<string>
  selectedItem: { groupId: string; itemId: string } | null
  isOpen: boolean
  width: number
  searchQuery: string
}

export interface MenuState {
  isVisible: boolean
  focusedIndex: number
  animationInProgress: boolean
}

export interface UIState {
  isDarkMode: boolean
  isMobile: boolean
  animationsEnabled: boolean
}

export interface DataContextType {
  sidebar: SidebarState
  menu: MenuState
  ui: UIState
  toggleCollapsedGroup: (groupId: string) => void
  selectItem: (groupId: string, itemId: string) => void
  setSidebarOpen: (isOpen: boolean) => void
  setSidebarWidth: (width: number) => void
  setSidebarSearchQuery: (query: string) => void
  setMenuVisible: (isVisible: boolean) => void
  setMenuFocusedIndex: (index: number) => void
  setMenuAnimationInProgress: (inProgress: boolean) => void
  setDarkMode: (isDarkMode: boolean) => void
  setIsMobile: (isMobile: boolean) => void
  setAnimationsEnabled: (enabled: boolean) => void
  reset: () => void
}

export const DataContext = createContext<DataContextType | undefined>(undefined)

export const initialSidebarState: SidebarState = {
  collapsedGroups: new Set(),
  selectedItem: null,
  isOpen: true,
  width: 256,
  searchQuery: ''
}

export const initialMenuState: MenuState = {
  isVisible: false,
  focusedIndex: -1,
  animationInProgress: false
}

export const initialUIState: UIState = {
  isDarkMode: false,
  isMobile: false,
  animationsEnabled: true
}
