/**
 * Sidebar collapsible + theme mode system
 * - toggleSidebar()         — collapse/expand; drives body.sidebar-collapsed class
 * - setThemeMode(mode)      — switch blue/purple/red; drives body.theme-* class
 * - toggleNavDropdown(id)   — open/close sidebar dropdown; state persisted
 * - initSidebar()           — restore all persisted state on page load
 */

declare const document: Document;
declare const window: any;

let sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true';
let themeMode: 'blue' | 'purple' | 'red' = (localStorage.getItem('themeMode') as any) || 'blue';

const THEME_COLORS: Record<string, string> = {
  blue:   '#3574f0',
  purple: '#a855f7',
  red:    '#ef4444',
};

// ── Sidebar collapse ──────────────────────────────────────────────────────────

export function toggleSidebar() {
  sidebarCollapsed = !sidebarCollapsed;
  localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed));
  applySidebarState();
}

function applySidebarState() {
  document.body.classList.toggle('sidebar-collapsed', sidebarCollapsed);
}

// ── Theme mode ────────────────────────────────────────────────────────────────

export function setThemeMode(mode: 'blue' | 'purple' | 'red') {
  themeMode = mode;
  localStorage.setItem('themeMode', mode);
  applyTheme();
}

function applyTheme() {
  document.body.classList.remove('theme-blue', 'theme-purple', 'theme-red');
  document.body.classList.add(`theme-${themeMode}`);

  // --mode-color drives all mode-aware CSS (mode-button borders, active nav items, etc.)
  document.documentElement.style.setProperty('--mode-color', THEME_COLORS[themeMode] || THEME_COLORS.blue);

  const modeLabels: Record<string, string> = { blue: 'BLUE MODE', purple: 'PURPLE MODE', red: 'RED MODE' };
  const sidebarStatus = document.getElementById('sidebar-status');
  if (sidebarStatus) {
    sidebarStatus.innerHTML = `<span class="status-dot"></span>${modeLabels[themeMode]}`;
  }

  ['blue', 'purple', 'red'].forEach(m => {
    const btn = document.getElementById(`mode-btn-${m}`);
    if (btn) btn.classList.toggle('active', m === themeMode);
  });
}

// ── Nav dropdowns ─────────────────────────────────────────────────────────────

export function toggleNavDropdown(id: string) {
  const hdr  = document.getElementById(id + '-hdr');
  const body = document.getElementById(id + '-body');
  if (!hdr || !body) return;
  const open = body.classList.toggle('open');
  hdr.classList.toggle('open', open);
  _persistDropdown(id, open);
}

function _persistDropdown(id: string, open: boolean) {
  const stored: string[] = JSON.parse(localStorage.getItem('openDropdowns') || '[]');
  if (open && !stored.includes(id)) { stored.push(id); }
  if (!open) { const i = stored.indexOf(id); if (i !== -1) stored.splice(i, 1); }
  localStorage.setItem('openDropdowns', JSON.stringify(stored));
}

function _restoreDropdowns() {
  const stored: string[] = JSON.parse(localStorage.getItem('openDropdowns') || '[]');
  stored.forEach(id => {
    const hdr  = document.getElementById(id + '-hdr');
    const body = document.getElementById(id + '-body');
    if (hdr && body) { body.classList.add('open'); hdr.classList.add('open'); }
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────

export function initSidebar() {
  applySidebarState();
  applyTheme();
  _restoreDropdowns();
}
