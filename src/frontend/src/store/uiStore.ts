import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface UIState {
  activeTab: string
  sidebarCollapsed: boolean
  theme: 'blue' | 'purple' | 'red'
  setActiveTab: (tab: string) => void
  toggleSidebar: () => void
  setTheme: (t: 'blue' | 'purple' | 'red') => void
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      activeTab: 'chat',
      sidebarCollapsed: false,
      theme: 'blue',
      setActiveTab: (activeTab) => set({ activeTab }),
      toggleSidebar: () => set((s) => ({ sidebarCollapsed: !s.sidebarCollapsed })),
      setTheme: (theme) => set({ theme }),
    }),
    {
      name: 'cybersecsuite-ui',
      skipHydration: false,
      partialize: (state) => ({
        activeTab: state.activeTab,
        sidebarCollapsed: state.sidebarCollapsed,
        theme: state.theme,
      }),
    }
  )
)
