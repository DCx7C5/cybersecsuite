// Dashboard main entry point and module wiring

import { showTab, fmt, tierBadge, costRange, fetchApi, currentTab } from './core.js';
import { renderTable } from './table.js';
import { initSSE, _sseConnect } from './sse.js';
import { refresh, cancelTask } from './refresh.js';
import { runAgentQuery, clearAgentHistory } from './agents.js';
import { loadOpenSearch } from './opensearch.js';
import { loadExplorerModels, loadExplorerTable } from './explorer.js';
import {
  loadSettings,
  saveSettingsAgent,
  saveSettingsEnv,
  switchSettingsScope,
  loadSettingsToggles,
  toggleMcp,
  toggleGlobalMcp,
  toggleSkillDomain,
  togglePlugin,
  installMcp,
  removeMcp,
  loadGlobalHooks,
  addHook,
  removeHook,
  settingsAddEnvRow,
} from './settings.js';
import {
  loadTeamBuilder,
  tbFilterAgents,
  tbLoadSkills,
  tbAddMember,
  tbGenerateTeam,
  tbCopyTeam,
  tbSaveTeam,
  tbLoadSavedTeams,
  tbDeleteTeam,
} from './team.js';
import {
  acLoadAgents,
  acFilterAgents,
  acCreateAgent,
  acEditAgent,
  acCloseEdit,
  acSaveEdit,
  acDeleteAgent,
} from './craft.js';
import {
  wfAddStep,
  wfClear,
  wfExecute,
  wfRenderResult,
  wfLoadAgentList,
} from './workflows.js';
import {
  afLoadTemplates,
  afAddTemplate,
  afLoadSkillOptions,
  afAddSkill,
  setupTypeHints,
  afGenerate,
  setupAgentFactoryLoader,
} from './factory.js';

// Assign all functions to window for global access from HTML onclick handlers
declare global {
  interface Window {
    // core
    showTab: typeof showTab;
    fmt: typeof fmt;
    tierBadge: typeof tierBadge;
    costRange: typeof costRange;
    fetchApi: typeof fetchApi;
    currentTab: typeof currentTab;

    // table
    renderTable: typeof renderTable;

    // sse
    initSSE: typeof initSSE;
    _sseConnect: typeof _sseConnect;

    // refresh
    refresh: typeof refresh;
    cancelTask: typeof cancelTask;

    // agents
    runAgentQuery: typeof runAgentQuery;
    clearAgentHistory: typeof clearAgentHistory;

    // opensearch
    loadOpenSearch: typeof loadOpenSearch;

    // explorer
    loadExplorerModels: typeof loadExplorerModels;
    loadExplorerTable: typeof loadExplorerTable;

    // settings
    loadSettings: typeof loadSettings;
    saveSettingsAgent: typeof saveSettingsAgent;
    saveSettingsEnv: typeof saveSettingsEnv;
    switchSettingsScope: typeof switchSettingsScope;
    loadSettingsToggles: typeof loadSettingsToggles;
    toggleMcp: typeof toggleMcp;
    toggleGlobalMcp: typeof toggleGlobalMcp;
    toggleSkillDomain: typeof toggleSkillDomain;
    togglePlugin: typeof togglePlugin;
    installMcp: typeof installMcp;
    removeMcp: typeof removeMcp;
    loadGlobalHooks: typeof loadGlobalHooks;
    addHook: typeof addHook;
    removeHook: typeof removeHook;
    settingsAddEnvRow: typeof settingsAddEnvRow;

    // team
    loadTeamBuilder: typeof loadTeamBuilder;
    tbFilterAgents: typeof tbFilterAgents;
    tbLoadSkills: typeof tbLoadSkills;
    tbAddMember: typeof tbAddMember;
    tbGenerateTeam: typeof tbGenerateTeam;
    tbCopyTeam: typeof tbCopyTeam;
    tbSaveTeam: typeof tbSaveTeam;
    tbLoadSavedTeams: typeof tbLoadSavedTeams;
    tbDeleteTeam: typeof tbDeleteTeam;

    // craft
    acLoadAgents: typeof acLoadAgents;
    acFilterAgents: typeof acFilterAgents;
    acCreateAgent: typeof acCreateAgent;
    acEditAgent: typeof acEditAgent;
    acCloseEdit: typeof acCloseEdit;
    acSaveEdit: typeof acSaveEdit;
    acDeleteAgent: typeof acDeleteAgent;

    // workflows
    wfAddStep: typeof wfAddStep;
    wfClear: typeof wfClear;
    wfExecute: typeof wfExecute;
    wfRenderResult: typeof wfRenderResult;
    wfLoadAgentList: typeof wfLoadAgentList;

    // factory
    afLoadTemplates: typeof afLoadTemplates;
    afAddTemplate: typeof afAddTemplate;
    afLoadSkillOptions: typeof afLoadSkillOptions;
    afAddSkill: typeof afAddSkill;
    setupTypeHints: typeof setupTypeHints;
    afGenerate: typeof afGenerate;
    setupAgentFactoryLoader: typeof setupAgentFactoryLoader;
  }
}

// Assign all functions to window
window.showTab = showTab;
window.fmt = fmt;
window.tierBadge = tierBadge;
window.costRange = costRange;
window.fetchApi = fetchApi;
window.currentTab = currentTab;

window.renderTable = renderTable;

window.initSSE = initSSE;
window._sseConnect = _sseConnect;

window.refresh = refresh;
window.cancelTask = cancelTask;

window.runAgentQuery = runAgentQuery;
window.clearAgentHistory = clearAgentHistory;

window.loadOpenSearch = loadOpenSearch;

window.loadExplorerModels = loadExplorerModels;
window.loadExplorerTable = loadExplorerTable;

window.loadSettings = loadSettings;
window.saveSettingsAgent = saveSettingsAgent;
window.saveSettingsEnv = saveSettingsEnv;
window.switchSettingsScope = switchSettingsScope;
window.loadSettingsToggles = loadSettingsToggles;
window.toggleMcp = toggleMcp;
window.toggleGlobalMcp = toggleGlobalMcp;
window.toggleSkillDomain = toggleSkillDomain;
window.togglePlugin = togglePlugin;
window.installMcp = installMcp;
window.removeMcp = removeMcp;
window.loadGlobalHooks = loadGlobalHooks;
window.addHook = addHook;
window.removeHook = removeHook;
window.settingsAddEnvRow = settingsAddEnvRow;

window.loadTeamBuilder = loadTeamBuilder;
window.tbFilterAgents = tbFilterAgents;
window.tbLoadSkills = tbLoadSkills;
window.tbAddMember = tbAddMember;
window.tbGenerateTeam = tbGenerateTeam;
window.tbCopyTeam = tbCopyTeam;
window.tbSaveTeam = tbSaveTeam;
window.tbLoadSavedTeams = tbLoadSavedTeams;
window.tbDeleteTeam = tbDeleteTeam;

window.acLoadAgents = acLoadAgents;
window.acFilterAgents = acFilterAgents;
window.acCreateAgent = acCreateAgent;
window.acEditAgent = acEditAgent;
window.acCloseEdit = acCloseEdit;
window.acSaveEdit = acSaveEdit;
window.acDeleteAgent = acDeleteAgent;

window.wfAddStep = wfAddStep;
window.wfClear = wfClear;
window.wfExecute = wfExecute;
window.wfRenderResult = wfRenderResult;
window.wfLoadAgentList = wfLoadAgentList;

window.afLoadTemplates = afLoadTemplates;
window.afAddTemplate = afAddTemplate;
window.afLoadSkillOptions = afLoadSkillOptions;
window.afAddSkill = afAddSkill;
window.setupTypeHints = setupTypeHints;
window.afGenerate = afGenerate;
window.setupAgentFactoryLoader = setupAgentFactoryLoader;

// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
  // Activate first sidebar tab on load
  document.querySelectorAll('[id^="tab-"]').forEach((el) => {
    (el as HTMLElement).style.display = 'none';
  });
  const first = document.getElementById('tab-health') as HTMLElement | null;
  if (first) first.style.display = '';
  const nav = document.getElementById('nav-health') as HTMLElement | null;
  if (nav) nav.classList.add('active');
  const crumb = document.querySelector('#topbar-title') as HTMLElement | null;
  if (crumb) crumb.textContent = '▶ HEALTH';

  // Initialize SSE connection
  await initSSE();

  // Fetch initial data
  await refresh();

  // Set up periodic refresh (every 15 seconds)
  setInterval(refresh, 15000);

  // Set up agent factory loader
  setupAgentFactoryLoader();
  setupTypeHints();
});
