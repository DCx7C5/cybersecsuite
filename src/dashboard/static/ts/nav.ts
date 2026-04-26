/**
 * Navigation with Lucide Icons Integration
 * Provides icon mappings and navigation helpers
 */

// Lucide icon imports
export type IconName =
  | 'home'
  | 'dashboard'
  | 'settings'
  | 'user'
  | 'users'
  | 'menu'
  | 'chevron-down'
  | 'chevron-up'
  | 'x'
  | 'search'
  | 'plus'
  | 'edit'
  | 'trash2'
  | 'check'
  | 'alert-circle'
  | 'info'
  | 'loader'
  | 'arrow-right'
  | 'arrow-left'
  | 'zap'
  | 'package'
  | 'git-branch'
  | 'play'
  | 'pause'
  | 'stop-circle'
  | 'phone'
  | 'mail'
  | 'map-pin'
  | 'calendar'
  | 'clock'
  | 'code'
  | 'command'
  | 'terminal'
  | 'bug'
  | 'target'
  | 'shield'
  | 'lock'
  | 'unlock'
  | 'eye'
  | 'eye-off'
  | 'filter'
  | 'download'
  | 'upload'
  | 'share'
  | 'star'
  | 'heart'
  | 'bookmark'
  | 'bell'
  | 'volume2'
  | 'volume-x'
  | 'sun'
  | 'moon'
  | 'cloud'
  | 'server'
  | 'database'
  | 'network'
  | 'wifi'
  | 'activity';

export interface NavItem {
  id: string;
  label: string;
  icon: IconName;
  href?: string;
  children?: NavItem[];
  badge?: number | string;
  disabled?: boolean;
}

export interface NavSection {
  title: string;
  items: NavItem[];
}

/**
 * Icon to SVG path mapping for Lucide icons
 * This is a subset of commonly used icons
 */
const ICON_PATHS: Record<IconName, string> = {
  home: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z',
  dashboard: 'M3 3h7v7H3z M13 3h7v7h-7z M3 13h7v7H3z M13 13h7v7h-7z',
  settings: 'M12 15a3 3 0 1 1 0-6 3 3 0 0 1 0 6z M19.4 15a1.65 1.65 0 0 0 .33-1.82l-.5-.84.74-.74.84.5a1.65 1.65 0 0 1 1.78-.33V15zM1 6v12a2 2 0 0 0 2 2h4.5M1 6a2 2 0 0 1 2-2h4',
  user: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2M12 3a4 4 0 1 0 0 8 4 4 0 0 0 0-8z',
  users: 'M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2M16 3.13a4 4 0 0 1 0 7.75M15 11h2a4 4 0 1 1 0-8h-1M9 5a4 4 0 1 0 0 8 4 4 0 0 0 0-8z',
  menu: 'M3 12h18M3 6h18M3 18h18',
  'chevron-down': 'M6 9l6 6 6-6',
  'chevron-up': 'M18 15l-6-6-6 6',
  x: 'M18 6L6 18M6 6l12 12',
  search: 'M11 3a8 8 0 1 1 0 16 8 8 0 0 1 0-16zM21 21l-4.35-4.35',
  plus: 'M12 5v14M5 12h14',
  edit: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7',
  trash2: 'M3 6h18M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M10 11v6M14 11v6M5 6h14l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2l-1-14z',
  check: 'M20 6L9 17l-5-5',
  'alert-circle': 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z',
  info: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z',
  loader: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z',
  'arrow-right': 'M5 12h14M12 5l7 7-7 7',
  'arrow-left': 'M19 12H5M12 19l-7-7 7-7',
  zap: 'M13 2L3 14h9l-1 8 10-12h-9l1-8z',
  package: 'M16.5 9.4l-9-5.19M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z',
  'git-branch': 'M6 3v12M18 9v12M6 15a3 3 0 0 1 3 3M18 21a3 3 0 0 1-3-3M9 6a3 3 0 1 1 0 6 3 3 0 0 1 0-6z',
  play: 'M5 3l14 9-14 9V3z',
  pause: 'M6 4h4v16H6V4zm8 0h4v16h-4V4z',
  'stop-circle': 'M8 8h8v8H8V8M2 12a10 10 0 1 0 20 0 10 10 0 0 0-20 0z',
  phone: 'M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z',
  mail: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z',
  'map-pin': 'M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z',
  calendar: 'M19 4H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2z',
  clock: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z',
  code: 'M16 18l-6-6 6-6M8 6l6 6-6 6',
  command: 'M18 3a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3 3 3 0 0 0-3 3V6a3 3 0 0 0 3 3 3 3 0 0 0 3-3 3 3 0 0 0-3-3z',
  terminal: 'M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z',
  bug: 'M9 2a7 7 0 0 0-7 7 7 7 0 0 0 7 7 7 7 0 0 0 7-7 7 7 0 0 0-7-7z',
  target: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z',
  shield: 'M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z',
  lock: 'M19 11H5c-1.1 0-2 .9-2 2v9c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2v-9c0-1.1-.9-2-2-2zm-5 6c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm5-8h-1V7c0-2.76-2.24-5-5-5s-5 2.24-5 5v2H5v2h14v-2z',
  unlock: 'M3 11c0-1.1.9-2 2-2h1V7c0-2.76 2.24-5 5-5s5 2.24 5 5v2h1c1.1 0 2 .9 2 2v9c0 1.1-.9 2-2 2H5c-1.1 0-2-.9-2-2v-9z',
  eye: 'M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5z',
  'eye-off': 'M11.83 9L5.5 2.62A9.147 9.147 0 0 1 12 2c5 0 9.27 3.11 11 7.5 0 .68-.07 1.35-.2 2M2 4.2l2.5 2.5M19.3 14c.8-1.2 1.4-2.5 1.7-4',
  filter: 'M3 4h18v2H3V4zm4 6h10v2H7v-2zm-2 6h14v2H5v-2z',
  download: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4',
  upload: 'M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4',
  share: 'M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8M16 6l-4-4-4 4M12 2v13',
  star: 'M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z',
  heart: 'M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z',
  bookmark: 'M19 21H5V5c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2v16z',
  bell: 'M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0',
  volume2: 'M23 12a11 11 0 0 1-11 11m0 0a11 11 0 0 1-11-11m11 11v-2a2 2 0 1 1-4 0v2m11-11a11 11 0 1 0-11-11m11 11h2m-12-1a1 1 0 1 1 2 0',
  'volume-x': 'M13 5l4 4m0-4l-4 4m11 7a11 11 0 0 1-11 11m11 11v2a2 2 0 1 1-4 0v-2M3 12a11 11 0 1 0 11-11M3 1v2m20 0v-2',
  sun: 'M12 18a6 6 0 1 0 0-12 6 6 0 0 0 0 12zM12 2v6m0 6v6m8-14.2l-4.2 4.2M5.8 19.2l4.2-4.2m2-13.4l-4.2 4.2m13.4 13.4l-4.2-4.2',
  moon: 'M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z',
  cloud: 'M18 10h-1.26A8 8 0 1 0 9 20h9a7 7 0 0 0 0-14z',
  server: 'M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z',
  database: 'M12 3c4.418 0 8-1.79 8-4s-3.582-4-8-4-8 1.79-8 4 3.582 4 8 4zm0 8c4.418 0 8-1.79 8-4m0 8c4.418 0 8-1.79 8-4',
  network: 'M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3z',
  wifi: 'M1 9l2 2c4.97-4.97 13.03-4.97 18 0l2-2C16.93 2.93 7.08 2.93 1 9zm8 8l3 3 3-3c-1.65-1.66-4.34-1.66-6 0zm-4-4l2 2c2.76-2.76 7.24-2.76 10 0l2-2C15.14 9.14 8.87 9.14 5 13z',
  activity: 'M22 12h-4l-3-9H9l-3 9H2M22 12a10 10 0 0 1-10 10 10 10 0 0 1-10-10 10 10 0 0 1 10-10 10 10 0 0 1 10 10z',
};

/**
 * Get SVG icon as string
 */
export function getIconSVG(
  name: IconName,
  size: number = 24,
  strokeWidth: number = 2,
  color: string = 'currentColor'
): string {
  const pathData = ICON_PATHS[name] || ICON_PATHS.home;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${strokeWidth}" stroke-linecap="round" stroke-linejoin="round">
    <path d="${pathData}"/>
  </svg>`;
}

/**
 * Build a navigation structure
 */
export function createNavSection(title: string, items: NavItem[]): NavSection {
  return { title, items };
}

/**
 * Create a nav item
 */
export function createNavItem(
  id: string,
  label: string,
  icon: IconName,
  href?: string,
  children?: NavItem[]
): NavItem {
  return {
    id,
    label,
    icon,
    href,
    children,
  };
}

/**
 * Filter nav items by search term
 */
export function filterNavItems(items: NavItem[], searchTerm: string): NavItem[] {
  const term = searchTerm.toLowerCase();

  return items
    .map((item) => ({
      ...item,
      children: item.children ? filterNavItems(item.children, searchTerm) : undefined,
    }))
    .filter((item) => item.label.toLowerCase().includes(term) || (item.children?.length ?? 0) > 0);
}
