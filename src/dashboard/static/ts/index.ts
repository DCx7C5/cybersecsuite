// Dashboard main entry point and module wiring

import { showTab, fmt, tierBadge, costRange, fetchApi, currentTab } from './core.js';
import { renderTable } from './table.js';
import { initSSE, _sseConnect } from './sse.js';
import { refresh, cancelTask } from './refresh.js';
import { runAgentQuery, clearAgentHistory } from './agents.js';
import { loadOpenSearch } from './opensearch.js';
import { loadExplorerModels, loadExplorerTable } from './explorer.js';
import { toggleSidebar, setThemeMode, initSidebar } from './sidebar.js';
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
  loadLocalLlmStatus,
  activateLocalLlm,
  deactivateLocalLlm,
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
import {
  acChatSend,
  acChatStop,
  acChatExport,
  acChatClear,
  acChatAppendToken,
  acChatAppendMessage,
  acChatRenderTool,
  acChatRenderMarkdown,
  acChatAppendUserBubble,
  acChatAppendAssistantBubble,
  acChatScrollLock,
  acChatAutoScroll,
  acChatToggleStream,
  initChat,
} from './chat.js';

import {
  checkBootstrapStatus,
  bootstrapRun,
  bootstrapSkip,
} from './bootstrap.js';
import {
  loadUsageCharts,
  loadIocCharts,
  loadFindingsCharts,
  loadComplianceCharts,
  loadHealthCharts,
} from './charts.js';
import {
  initFlowgraph,
  fgLoadAgents,
  fgClear,
  fgExport,
  fgImport,
  fgExportDialog,
  fgImportDialog,
  fgExecute,
} from './flowgraph.js';
import {
  sdkStreamRun,
  sdkStructuredRun,
  sdkThinkingRun,
  sdkToolsRun,
  sdkMemoryRun,
  sdkMemoryRead,
  sdkApiHealth,
  initSdkPanel,
} from './sdk_panel.js';
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
    loadLocalLlmStatus: typeof loadLocalLlmStatus;
    activateLocalLlm: typeof activateLocalLlm;
    deactivateLocalLlm: typeof deactivateLocalLlm;

    // sidebar
    toggleSidebar: typeof toggleSidebar;
    setThemeMode: typeof setThemeMode;
    initSidebar: typeof initSidebar;

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

    // chat
    acChatSend: typeof acChatSend;
    acChatStop: typeof acChatStop;
    acChatExport: typeof acChatExport;
    acChatClear: typeof acChatClear;
    acChatAppendToken: typeof acChatAppendToken;
    acChatAppendMessage: typeof acChatAppendMessage;
    acChatRenderTool: typeof acChatRenderTool;
    acChatRenderMarkdown: typeof acChatRenderMarkdown;
    acChatAppendUserBubble: typeof acChatAppendUserBubble;
    acChatAppendAssistantBubble: typeof acChatAppendAssistantBubble;
    acChatScrollLock: typeof acChatScrollLock;
    acChatAutoScroll: typeof acChatAutoScroll;
    acChatToggleStream: typeof acChatToggleStream;

    // bootstrap modal (called from HTML onclick)
    _bootstrapRun: () => void;
    _bootstrapSkip: () => void;

    // charts
    loadUsageCharts: typeof loadUsageCharts;
    loadIocCharts: typeof loadIocCharts;
    loadFindingsCharts: typeof loadFindingsCharts;
    loadComplianceCharts: typeof loadComplianceCharts;
    loadHealthCharts: typeof loadHealthCharts;

    // flowgraph
    initFlowgraph: typeof initFlowgraph;
    fgLoadAgents: typeof fgLoadAgents;
    fgClear: typeof fgClear;
    fgExport: typeof fgExport;
    fgImport: typeof fgImport;
    fgExportDialog: typeof fgExportDialog;
    fgImportDialog: typeof fgImportDialog;
    fgExecute: typeof fgExecute;

    // sdk lab
    sdkStreamRun: typeof sdkStreamRun;
    sdkStructuredRun: typeof sdkStructuredRun;
    sdkThinkingRun: typeof sdkThinkingRun;
    sdkToolsRun: typeof sdkToolsRun;
    sdkMemoryRun: typeof sdkMemoryRun;
    sdkMemoryRead: typeof sdkMemoryRead;
    sdkApiHealth: typeof sdkApiHealth;
    sdkSubTab: (name: string) => void;
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
window.loadLocalLlmStatus = loadLocalLlmStatus;
window.activateLocalLlm = activateLocalLlm;
window.deactivateLocalLlm = deactivateLocalLlm;

// Sidebar
window.toggleSidebar = toggleSidebar;
window.setThemeMode = setThemeMode;
window.initSidebar = initSidebar;

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

window.acChatSend = acChatSend;
window.acChatStop = acChatStop;
window.acChatExport = acChatExport;
window.acChatClear = acChatClear;
window.acChatAppendToken = acChatAppendToken;
window.acChatAppendMessage = acChatAppendMessage;
window.acChatRenderTool = acChatRenderTool;
window.acChatRenderMarkdown = acChatRenderMarkdown;
window.acChatAppendUserBubble = acChatAppendUserBubble;
window.acChatAppendAssistantBubble = acChatAppendAssistantBubble;
window.acChatScrollLock = acChatScrollLock;
window.acChatAutoScroll = acChatAutoScroll;
window.acChatToggleStream = acChatToggleStream;

// Bootstrap modal — exposed for HTML onclick handlers
window._bootstrapRun = () => { bootstrapRun(); };
window._bootstrapSkip = () => { bootstrapSkip(); };

// Charts
window.loadUsageCharts = loadUsageCharts;
window.loadIocCharts = loadIocCharts;
window.loadFindingsCharts = loadFindingsCharts;
window.loadComplianceCharts = loadComplianceCharts;
window.loadHealthCharts = loadHealthCharts;

// Flowgraph
window.initFlowgraph = initFlowgraph;
window.fgLoadAgents = fgLoadAgents;
window.fgClear = fgClear;
window.fgExport = fgExport;
window.fgImport = fgImport;
window.fgExportDialog = fgExportDialog;
window.fgImportDialog = fgImportDialog;
window.fgExecute = fgExecute;

// SDK Lab
window.sdkStreamRun = sdkStreamRun;
window.sdkStructuredRun = sdkStructuredRun;
window.sdkThinkingRun = sdkThinkingRun;
window.sdkToolsRun = sdkToolsRun;
window.sdkMemoryRun = sdkMemoryRun;
window.sdkMemoryRead = sdkMemoryRead;
window.sdkApiHealth = sdkApiHealth;
window.sdkSubTab = (name: string) => {
  document.querySelectorAll('.sdk-sub').forEach((el) => {
    (el as HTMLElement).style.display = 'none';
  });
  const sub = document.getElementById(`sdk-sub-${name}`);
  if (sub) sub.style.display = '';
  // update active button styling
  document.querySelectorAll('#sdk-sub-tabs button').forEach((btn) => {
    const b = btn as HTMLButtonElement;
    b.className = b.textContent?.toLowerCase().trim() === name
      ? 'btn btn-accent text-xs'
      : 'btn btn-ghost text-xs';
  });
};

// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
  // Initialize sidebar (collapsible + theme mode)
  initSidebar();

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

  // Check first-run bootstrap status (shows modal if DB not seeded)
  await checkBootstrapStatus();

  // Fetch initial data
  await refresh();

  // Set up periodic refresh (every 15 seconds)
  setInterval(refresh, 15000);

  // Set up agent factory loader
  setupAgentFactoryLoader();
  setupTypeHints();
  await initChat();

  // Load health charts on initial tab
  loadHealthCharts().catch(() => {});

  // Patch showTab to lazy-load charts and init flowgraph on first visit
  const _origShowTab = window.showTab;
  window.showTab = (name: string) => {
    _origShowTab(name);
    if (name === 'usage')      { loadUsageCharts().catch(() => {}); }
    if (name === 'iocs')       { loadIocCharts().catch(() => {}); }
    if (name === 'findings')   { loadFindingsCharts().catch(() => {}); }
    if (name === 'compliance') { loadComplianceCharts().catch(() => {}); }
    if (name === 'health')     { loadHealthCharts().catch(() => {}); }
    if (name === 'flowgraph')  { initFlowgraph(); fgLoadAgents().catch(() => {}); }
    if (name === 'sdk-lab')    { initSdkPanel(); }
  };
});
