/**
 * Utils Index
 * Central export point for all utilities
 */

export {
  parseCommand,
  validateCommand,
  executeCommand,
  CommandRegistryBuilder,
  createCommand,
} from './commandEngine';
export type { Command, CommandRegistry, ExecutionResult } from './commandEngine';

export {
  parseMentions,
  checkOverlappingMentions,
  validateMentionReferences,
  replaceMentions,
  extractMentionsByType,
} from './mentionValidation';
export type { MentionMatch, ValidationResult } from './mentionValidation';

export {
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
} from './sidebarPersist';
export type { SidebarState } from './sidebarPersist';
