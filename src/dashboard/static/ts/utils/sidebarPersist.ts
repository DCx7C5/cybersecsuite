/**
 * Sidebar State Persistence
 * localStorage-based persistence for sidebar state
 */

export interface SidebarState {
  isCollapsed: boolean;
  openDropdowns: string[];
  themeMode: 'blue' | 'purple' | 'red';
  lastActiveTab: string;
}

const STORAGE_KEY = 'sidebar_state';
const DEFAULT_STATE: SidebarState = {
  isCollapsed: false,
  openDropdowns: [],
  themeMode: 'blue',
  lastActiveTab: 'home',
};

/**
 * Save sidebar state to localStorage
 */
export function saveSidebarState(state: Partial<SidebarState>): void {
  try {
    const current = loadSidebarState();
    const updated = { ...current, ...state };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (e) {
    console.error('Failed to save sidebar state:', e);
  }
}

/**
 * Load sidebar state from localStorage
 */
export function loadSidebarState(): SidebarState {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) {
      return DEFAULT_STATE;
    }
    return { ...DEFAULT_STATE, ...JSON.parse(stored) };
  } catch (e) {
    console.error('Failed to load sidebar state:', e);
    return DEFAULT_STATE;
  }
}

/**
 * Clear sidebar state
 */
export function clearSidebarState(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (e) {
    console.error('Failed to clear sidebar state:', e);
  }
}

/**
 * Toggle sidebar collapsed state
 */
export function toggleSidebarCollapse(): void {
  const state = loadSidebarState();
  saveSidebarState({ isCollapsed: !state.isCollapsed });
}

/**
 * Update theme mode
 */
export function updateThemeMode(mode: 'blue' | 'purple' | 'red'): void {
  saveSidebarState({ themeMode: mode });
}

/**
 * Add dropdown to open list
 */
export function addOpenDropdown(id: string): void {
  const state = loadSidebarState();
  if (!state.openDropdowns.includes(id)) {
    state.openDropdowns.push(id);
    saveSidebarState({ openDropdowns: state.openDropdowns });
  }
}

/**
 * Remove dropdown from open list
 */
export function removeOpenDropdown(id: string): void {
  const state = loadSidebarState();
  const index = state.openDropdowns.indexOf(id);
  if (index !== -1) {
    state.openDropdowns.splice(index, 1);
    saveSidebarState({ openDropdowns: state.openDropdowns });
  }
}

/**
 * Toggle dropdown open state
 */
export function toggleDropdown(id: string): void {
  const state = loadSidebarState();
  if (state.openDropdowns.includes(id)) {
    removeOpenDropdown(id);
  } else {
    addOpenDropdown(id);
  }
}

/**
 * Check if dropdown is open
 */
export function isDropdownOpen(id: string): boolean {
  const state = loadSidebarState();
  return state.openDropdowns.includes(id);
}

/**
 * Set active tab and persist
 */
export function setActiveTab(tabId: string): void {
  saveSidebarState({ lastActiveTab: tabId });
}

/**
 * Get active tab
 */
export function getActiveTab(): string {
  const state = loadSidebarState();
  return state.lastActiveTab;
}
