/**
 * Tests for Sidebar State Persistence
 */

import {
  saveSidebarState,
  loadSidebarState,
  clearSidebarState,
  toggleSidebarCollapse,
  updateThemeMode,
  addOpenDropdown,
  removeOpenDropdown,
  toggleDropdown,
  isDropdownOpen,
  setActiveTab,
  getActiveTab,
} from '../../src/dashboard/static/ts/utils/sidebarPersist';

describe('Sidebar State Persistence', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
  });

  describe('saveSidebarState and loadSidebarState', () => {
    it('should save and load state', () => {
      const state = { isCollapsed: true, themeMode: 'purple' as const };
      saveSidebarState(state);

      const loaded = loadSidebarState();
      expect(loaded.isCollapsed).toBe(true);
      expect(loaded.themeMode).toBe('purple');
    });

    it('should return default state when empty', () => {
      const state = loadSidebarState();
      expect(state.isCollapsed).toBe(false);
      expect(state.themeMode).toBe('blue');
      expect(state.openDropdowns).toEqual([]);
    });

    it('should merge with existing state', () => {
      saveSidebarState({ isCollapsed: true });
      saveSidebarState({ themeMode: 'red' as const });

      const loaded = loadSidebarState();
      expect(loaded.isCollapsed).toBe(true);
      expect(loaded.themeMode).toBe('red');
    });
  });

  describe('clearSidebarState', () => {
    it('should clear all state', () => {
      saveSidebarState({ isCollapsed: true });
      clearSidebarState();

      const state = loadSidebarState();
      expect(state.isCollapsed).toBe(false);
    });
  });

  describe('toggleSidebarCollapse', () => {
    it('should toggle collapse state', () => {
      let state = loadSidebarState();
      expect(state.isCollapsed).toBe(false);

      toggleSidebarCollapse();
      state = loadSidebarState();
      expect(state.isCollapsed).toBe(true);

      toggleSidebarCollapse();
      state = loadSidebarState();
      expect(state.isCollapsed).toBe(false);
    });
  });

  describe('updateThemeMode', () => {
    it('should update theme mode', () => {
      updateThemeMode('purple');
      const state = loadSidebarState();
      expect(state.themeMode).toBe('purple');
    });

    it('should persist theme mode change', () => {
      updateThemeMode('red');
      updateThemeMode('blue');

      const state = loadSidebarState();
      expect(state.themeMode).toBe('blue');
    });
  });

  describe('Dropdown management', () => {
    it('should add dropdown to open list', () => {
      addOpenDropdown('nav-1');
      expect(isDropdownOpen('nav-1')).toBe(true);
    });

    it('should not add duplicate dropdowns', () => {
      addOpenDropdown('nav-1');
      addOpenDropdown('nav-1');

      const state = loadSidebarState();
      expect(state.openDropdowns.filter((id) => id === 'nav-1')).toHaveLength(1);
    });

    it('should remove dropdown from open list', () => {
      addOpenDropdown('nav-1');
      removeOpenDropdown('nav-1');

      expect(isDropdownOpen('nav-1')).toBe(false);
    });

    it('should toggle dropdown', () => {
      toggleDropdown('nav-1');
      expect(isDropdownOpen('nav-1')).toBe(true);

      toggleDropdown('nav-1');
      expect(isDropdownOpen('nav-1')).toBe(false);
    });

    it('should handle multiple dropdowns', () => {
      addOpenDropdown('nav-1');
      addOpenDropdown('nav-2');

      expect(isDropdownOpen('nav-1')).toBe(true);
      expect(isDropdownOpen('nav-2')).toBe(true);

      removeOpenDropdown('nav-1');
      expect(isDropdownOpen('nav-1')).toBe(false);
      expect(isDropdownOpen('nav-2')).toBe(true);
    });
  });

  describe('Active tab management', () => {
    it('should set and get active tab', () => {
      setActiveTab('dashboard');
      expect(getActiveTab()).toBe('dashboard');
    });

    it('should default to home tab', () => {
      expect(getActiveTab()).toBe('home');
    });

    it('should persist tab changes', () => {
      setActiveTab('settings');
      setActiveTab('analysis');

      expect(getActiveTab()).toBe('analysis');
    });
  });

  describe('Error handling', () => {
    it('should handle corrupted storage gracefully', () => {
      localStorage.setItem('sidebar_state', 'invalid json');
      const state = loadSidebarState();

      expect(state).toBeDefined();
      expect(state.isCollapsed).toBe(false);
    });

    it('should handle save errors gracefully', () => {
      const spy = jest.spyOn(Storage.prototype, 'setItem').mockImplementation(() => {
        throw new Error('Storage error');
      });

      // Should not throw
      expect(() => {
        saveSidebarState({ isCollapsed: true });
      }).not.toThrow();

      spy.mockRestore();
    });
  });
});
