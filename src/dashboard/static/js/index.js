// Dashboard main entry point and module wiring
import { showTab, fmt, tierBadge, costRange, fetchApi, currentTab } from './core.js';
import { renderTable } from './table.js';
import { initSSE, _sseConnect } from './sse.js';
import { refresh, cancelTask } from './refresh.js';
import { runAgentQuery, clearAgentHistory } from './agents.js';
import { loadOpenSearch } from './opensearch.js';
import { loadExplorerModels, loadExplorerTable } from './explorer.js';
import { toggleSidebar, setThemeMode, initSidebar, toggleNavDropdown } from './sidebar.js';
import { loadSettings, saveSettingsAgent, saveSettingsEnv, switchSettingsScope, loadSettingsToggles, toggleMcp, toggleGlobalMcp, toggleSkillDomain, togglePlugin, installMcp, removeMcp, loadGlobalHooks, addHook, removeHook, settingsAddEnvRow, loadLocalLlmStatus, activateLocalLlm, deactivateLocalLlm, } from './settings.js';
import { loadTeamBuilder, tbFilterAgents, tbLoadSkills, tbAddMember, tbGenerateTeam, tbCopyTeam, tbSaveTeam, tbLoadSavedTeams, tbDeleteTeam, } from './team.js';
import { acLoadAgents, acFilterAgents, acCreateAgent, acEditAgent, acCloseEdit, acSaveEdit, acDeleteAgent, } from './craft.js';
import { wfAddStep, wfClear, wfExecute, wfRenderResult, wfLoadAgentList, } from './workflows.js';
import { afLoadTemplates, afAddTemplate, afLoadSkillOptions, afAddSkill, setupTypeHints, afGenerate, setupAgentFactoryLoader, } from './factory.js';
import { acChatSend, acChatStop, acChatExport, acChatClear, acChatAppendToken, acChatAppendMessage, acChatRenderTool, acChatRenderMarkdown, acChatAppendUserBubble, acChatAppendAssistantBubble, acChatScrollLock, acChatAutoScroll, acChatToggleStream, initChat, } from './chat.js';
import { checkBootstrapStatus, bootstrapRun, bootstrapSkip, } from './bootstrap.js';
import { loadUsageCharts, loadIocCharts, loadFindingsCharts, loadComplianceCharts, loadHealthCharts, } from './charts.js';
import { initFlowgraph, fgLoadAgents, fgClear, fgExport, fgImport, fgExportDialog, fgImportDialog, fgExecute, } from './flowgraph.js';
import { sdkStreamRun, sdkStructuredRun, sdkThinkingRun, sdkToolsRun, sdkMemoryRun, sdkMemoryRead, sdkApiHealth, initSdkPanel, } from './sdk_panel.js';
import { loadProvidersHub, phOpenModal, phSaveAccount, phCloseModal, phFilterProviders, phSetProviderEnabled, } from './providers_hub.js';
import { loadVaultStatus, vaultChatSend, } from './vault.js';
import { loadQolControls, qolToggle, qolApplyPreset, qolReset, } from './qol.js';
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
window.toggleNavDropdown = toggleNavDropdown;
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
// Providers Hub
window.loadProvidersHub = loadProvidersHub;
window.phOpenModal = phOpenModal;
window.phSaveAccount = phSaveAccount;
window.phCloseModal = phCloseModal;
window.phFilterProviders = phFilterProviders;
window.phSetProviderEnabled = phSetProviderEnabled;
// Vault
window.loadVaultStatus = loadVaultStatus;
window.vaultChatSend = vaultChatSend;
// QoL Controls
window.loadQolControls = loadQolControls;
window.qolToggle = qolToggle;
window.qolApplyPreset = qolApplyPreset;
window.qolReset = qolReset;
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
window.sdkSubTab = (name) => {
    document.querySelectorAll('.sdk-sub').forEach((el) => {
        el.style.display = 'none';
    });
    const sub = document.getElementById(`sdk-sub-${name}`);
    if (sub)
        sub.style.display = '';
    // update active button styling
    document.querySelectorAll('#sdk-sub-tabs button').forEach((btn) => {
        const b = btn;
        b.className = b.textContent?.toLowerCase().trim() === name
            ? 'btn btn-accent text-xs'
            : 'btn btn-ghost text-xs';
    });
};
// Initialize dashboard on DOM ready
document.addEventListener('DOMContentLoaded', async () => {
    // Initialize sidebar (collapsible + theme mode)
    initSidebar();
    // Restore last active tab (or default to first tab)
    const savedTab = localStorage.getItem('activeTab') || 'health';
    document.querySelectorAll('[id^="tab-"]').forEach((el) => {
        el.style.display = 'none';
    });
    const firstPanel = document.getElementById(`tab-${savedTab}`);
    if (firstPanel)
        firstPanel.style.display = '';
    const firstNav = document.getElementById(`nav-${savedTab}`);
    if (firstNav)
        firstNav.classList.add('active');
    const crumb = document.querySelector('#topbar-title');
    if (crumb && firstNav)
        crumb.textContent = '▶ ' + firstNav.textContent.trim().toUpperCase();
    // currentTab is updated via showTab — set module var via re-export trick
    window.showTab(savedTab);
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
    loadHealthCharts().catch(() => { });
    // Patch showTab to lazy-load charts and init flowgraph on first visit
    const _origShowTab = window.showTab;
    window.showTab = (name) => {
        _origShowTab(name);
        if (name === 'usage') {
            loadUsageCharts().catch(() => { });
        }
        if (name === 'iocs') {
            loadIocCharts().catch(() => { });
        }
        if (name === 'findings') {
            loadFindingsCharts().catch(() => { });
        }
        if (name === 'compliance') {
            loadComplianceCharts().catch(() => { });
        }
        if (name === 'health') {
            loadHealthCharts().catch(() => { });
        }
        if (name === 'flowgraph') {
            initFlowgraph();
            fgLoadAgents().catch(() => { });
        }
        if (name === 'sdk-lab') {
            initSdkPanel();
        }
        if (name === 'providers-hub') {
            loadProvidersHub().catch(() => { });
        }
        if (name === 'settings') {
            loadSettings().catch(() => { });
        }
        if (name === 'settings-cybersecsuite') {
            loadSettingsToggles().catch(() => { });
        }
        if (name === 'vault') {
            loadVaultStatus().catch(() => { });
        }
        if (name === 'qol-controls') {
            loadQolControls().catch(() => { });
        }
        if (name === 'agent-factory') {
            afLoadTemplates().catch(() => { });
        }
        if (name === 'agent-crafter') {
            acLoadAgents().catch(() => { });
        }
        if (name === 'team-builder') {
            loadTeamBuilder().catch(() => { });
        }
        if (name === 'opensearch') {
            loadOpenSearch().catch(() => { });
        }
        if (name === 'explorer') {
            loadExplorerModels().catch(() => { });
        }
        if (name === 'workflows') {
            wfLoadAgentList().catch(() => { });
        }
    };
    if (savedTab === 'settings') {
        loadSettings().catch(() => { });
    }
    if (savedTab === 'settings-cybersecsuite') {
        loadSettingsToggles().catch(() => { });
    }
});
//# sourceMappingURL=index.js.map