/**
 * Sidebar collapsible + theme mode system
 * - toggleSidebar() — collapse/expand sidebar
 * - setThemeMode(mode) — switch between blue/purple/red themes
 * - State persisted in localStorage
 */

declare const document: Document;
declare const window: any;

let sidebarCollapsed = localStorage.getItem('sidebarCollapsed') === 'true' || false;
let themeMode: 'blue' | 'purple' | 'red' = (localStorage.getItem('themeMode') as any) || 'blue';

function getSidebarWidth(): string {
  const value = getComputedStyle(document.documentElement).getPropertyValue('--sidebar-w').trim();
  return value || '240px';
}

export function toggleSidebar() {
  sidebarCollapsed = !sidebarCollapsed;
  localStorage.setItem('sidebarCollapsed', String(sidebarCollapsed));
  updateSidebarLayout();
  updateToggleButton();
}

export function setThemeMode(mode: 'blue' | 'purple' | 'red') {
  themeMode = mode;
  localStorage.setItem('themeMode', mode);
  updateThemeColors();
  updateModeButtons();
}

function updateSidebarLayout() {
  const sidebar = document.getElementById('sidebar');
  const content = document.getElementById('main-content');
  const toggleBtn = document.getElementById('sidebar-toggle');
  const statusbar = document.getElementById('statusbar');
  const sidebarWidth = getSidebarWidth();

  if (sidebar) {
    if (sidebarCollapsed) {
      sidebar.style.left = `calc(-1 * ${sidebarWidth})`;
    } else {
      sidebar.style.left = '0';
    }
  }

  if (content) {
    if (sidebarCollapsed) {
      content.style.marginLeft = '0';
    } else {
      content.style.marginLeft = sidebarWidth;
    }
  }

  if (statusbar) {
    if (sidebarCollapsed) {
      statusbar.style.left = '0';
    } else {
      statusbar.style.left = sidebarWidth;
    }
  }

  if (toggleBtn) {
    toggleBtn.style.display = sidebarCollapsed ? 'inline-flex' : 'none';
  }
}

function updateToggleButton() {
  const toggleBtn = document.getElementById('sidebar-toggle');
  if (toggleBtn) {
    toggleBtn.textContent = sidebarCollapsed ? '☰' : '✕';
  }
}

function updateThemeColors() {
  const root = document.documentElement;
  const body = document.body;
  const modeButtonBlue = document.getElementById('mode-btn-blue');
  const modeButtonPurple = document.getElementById('mode-btn-purple');
  const modeButtonRed = document.getElementById('mode-btn-red');
  const sidebarStatus = document.getElementById('sidebar-status');

  switch (themeMode) {
    case 'blue':
      root.style.setProperty('--mode-color', '#3574f0');
      root.style.setProperty('--accent', '#3574f0');
      if (sidebarStatus) sidebarStatus.innerHTML = '<span class="status-dot"></span>BLUE MODE';
      break;
    case 'purple':
      root.style.setProperty('--mode-color', '#a855f7');
      root.style.setProperty('--accent', '#a855f7');
      if (sidebarStatus) sidebarStatus.innerHTML = '<span class="status-dot"></span>PURPLE MODE';
      break;
    case 'red':
      root.style.setProperty('--mode-color', '#ef4444');
      root.style.setProperty('--accent', '#ef4444');
      if (sidebarStatus) sidebarStatus.innerHTML = '<span class="status-dot"></span>RED MODE';
      break;
  }
  body.classList.remove('theme-blue', 'theme-purple', 'theme-red');
  body.classList.add(`theme-${themeMode}`);

  if (modeButtonBlue) modeButtonBlue.classList.toggle('active', themeMode === 'blue');
  if (modeButtonPurple) modeButtonPurple.classList.toggle('active', themeMode === 'purple');
  if (modeButtonRed) modeButtonRed.classList.toggle('active', themeMode === 'red');
}

function updateModeButtons() {
  const modeButtonBlue = document.getElementById('mode-btn-blue');
  const modeButtonPurple = document.getElementById('mode-btn-purple');
  const modeButtonRed = document.getElementById('mode-btn-red');

  if (modeButtonBlue) modeButtonBlue.classList.toggle('active', themeMode === 'blue');
  if (modeButtonPurple) modeButtonPurple.classList.toggle('active', themeMode === 'purple');
  if (modeButtonRed) modeButtonRed.classList.toggle('active', themeMode === 'red');
}

export function initSidebar() {
  updateSidebarLayout();
  updateThemeColors();
  updateToggleButton();
  updateModeButtons();
}
