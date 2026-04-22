/**
 * background.js — CyberSecSuite Agent v3.0 service worker
 *
 * Responsibilities:
 *  - Config management (local storage)
 *  - Domain activation: only AI features activate on configured domains
 *  - Message routing between content scripts and popup
 *  - Network request monitoring (optional telemetry)
 *
 * NOTE: WebSocket removed in v3.0. All streaming now via Anthropic SDK + dashboard endpoints.
 */

// ── State ─────────────────────────────────────────────────────────────────────

/** @type {{ dashboardUrl: string, activeDomains: string[], ajaxPatterns: string[], typingSpeedMs: number, autoSubmit: boolean, enabled: boolean }} */
let cfg = null;

/** @type {{ [tabId: number]: { url: string, hostname: string, form: any, timestamp: number } }} */
const detectedForms = {};  // Cache detected forms by tab ID

const DEFAULT_CFG = {
  dashboardUrl:  'http://localhost:8000',
  activeDomains: [
    'github.com',
    'claude.ai',
    'platform.openai.com',
    'chat.openai.com',
    'console.anthropic.com',
    'anthropic.com',
  ],
  ajaxPatterns: [
    '/v1/messages', '/v1/completions', '/v1/chat/completions',
    '/api/chat', '/api/generate', '/api/messages', '/api/completions',
    'api.anthropic.com', 'api.openai.com',
  ],
  typingSpeedMs: 28,
  autoSubmit:    false,
  enabled:       true,
};

// ── Config loading ─────────────────────────────────────────────────────────

async function loadCfg() {
  return new Promise(resolve => {
    chrome.storage.local.get(['css_cfg'], d => {
      cfg = { ...DEFAULT_CFG, ...(d.css_cfg || {}) };
      resolve(cfg);
    });
  });
}

async function saveCfg(patch) {
  cfg = { ...cfg, ...patch };
  return new Promise(resolve => chrome.storage.local.set({ css_cfg: cfg }, resolve));
}

// ── Domain activation ─────────────────────────────────────────────────────

function isDomainActive(hostname) {
  if (!cfg?.enabled) return false;
  return cfg.activeDomains.some(d => hostname === d || hostname.endsWith('.' + d));
}

// ── Auto-detection of forms on active domain tabs ──────────────────────────

async function autoDetectFormOnTab(tabId, url) {
  if (!url || !cfg?.enabled) return;
  
  try {
    const urlObj = new URL(url);
    if (!isDomainActive(urlObj.hostname)) return;
  } catch { return; }
  
  try {
    chrome.tabs.sendMessage(tabId, { action: 'detectForm' }, resp => {
      if (chrome.runtime.lastError) return;
      if (resp?.found) {
        detectedForms[tabId] = {
          url,
          hostname: new URL(url).hostname,
          form: resp.form,
          timestamp: Date.now(),
        };
        console.log(`[CCS] Form detected on tab ${tabId}: ${resp.form.placeholder || resp.form.tag}`);
      }
    });
  } catch (_) {}
}

function scanAllActiveDomainTabs() {
  if (!cfg?.enabled) return;
  
  chrome.tabs.query({}, tabs => {
    for (const tab of tabs) {
      if (!tab.url || !tab.id) continue;
      try {
        const url = new URL(tab.url);
        if (isDomainActive(url.hostname)) {
          autoDetectFormOnTab(tab.id, tab.url);
        }
      } catch (_) {}
    }
  });
}

// ── Message handler (from content + popup) ───────────────────────────────────

chrome.runtime.onMessage.addListener((req, sender, sendResponse) => {
  const respond = v => { try { sendResponse(v); } catch (_) {} };

  switch (req.action) {

    case 'getStatus':
      respond({ connected: true, cfg, version: '3.0', detectedForms });
      break;

    case 'getCfg':
      respond({ cfg });
      break;

    case 'saveCfg':
      saveCfg(req.cfg).then(() => {
        respond({ ok: true });
      });
      return true; // async

    case 'getTabInfo':
      chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        const tab = tabs[0];
        if (!tab?.url) { respond({ active: false }); return; }
        const url = new URL(tab.url);
        const formInfo = detectedForms[tab.id];
        respond({ 
          active: isDomainActive(url.hostname), 
          hostname: url.hostname, 
          title: tab.title,
          formDetected: !!formInfo,
          form: formInfo?.form,
        });
      });
      return true;

    // T025: list all tabs that have a detected form (incl. non-focused tabs)
    case 'listTargetTabs':
      chrome.tabs.query({}, tabs => {
        const targets = tabs
          .filter(t => t.id && detectedForms[t.id])
          .map(t => {
            let hostname = '';
            try { hostname = new URL(t.url || '').hostname; } catch (_) { hostname = t.url || ''; }
            return {
              tabId: t.id,
              title: t.title || '',
              hostname,
              active: t.active,
              form: detectedForms[t.id]?.form,
            };
          });
        respond({ tabs: targets });
      });
      return true;

    // T025: forward an inject/detect/abort message to a specific tab by ID
    case 'injectToTab':
      if (!req.tabId) { respond({ ok: false, error: 'no tabId' }); break; }
      chrome.tabs.sendMessage(req.tabId, req.msg, msgResp => {
        if (chrome.runtime.lastError) {
          respond({ ok: false, error: chrome.runtime.lastError.message });
        } else {
          respond(msgResp || { ok: false, error: 'no response' });
        }
      });
      return true;

    // Forward injectPromptManual to the active tab (keeps existing popup.js working)
    case 'injectPromptManual':
      chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        if (!tabs[0]?.id) { respond({ ok: false, error: 'no active tab' }); return; }
        chrome.tabs.sendMessage(tabs[0].id, {
          action: 'injectPrompt',
          prompt: req.prompt,
          options: req.options || {},
        }, msgResp => {
          if (chrome.runtime.lastError) {
            respond({ ok: false, error: chrome.runtime.lastError.message });
          } else {
            respond(msgResp || { ok: false });
          }
        });
      });
      return true;

    default:
      break;
  }

  return false;
});

// ── Tab events for auto-detection ────────────────────────────────────────────

// On tab created
chrome.tabs.onCreated.addListener(tab => {
  if (tab.url && tab.id) {
    autoDetectFormOnTab(tab.id, tab.url);
  }
});

// On tab updated (URL changed, page loaded)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.url) {
    autoDetectFormOnTab(tabId, tab.url);
  }
});

// On tab activated (switched to)
chrome.tabs.onActivated.addListener(({ tabId }) => {
  chrome.tabs.get(tabId, tab => {
    if (tab?.url) {
      autoDetectFormOnTab(tabId, tab.url);
    }
  });
});

// Clean up on tab closed
chrome.tabs.onRemoved.addListener(tabId => {
  delete detectedForms[tabId];
});

// ── Plugin registration ──────────────────────────────────────────────────────

async function registerPluginWithDashboard() {
  if (!cfg?.dashboardUrl) return;
  
  try {
    const resp = await fetch(`${cfg.dashboardUrl}/api/plugin/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        domain: 'browser-plugin',
        version: '3.0',
        timestamp: Date.now(),
      }),
    });
    
    if (resp.ok) {
      const data = await resp.json();
      console.log('[CCS] Registered with dashboard v' + data.dashboard_version);
    }
  } catch (e) {
    console.log('[CCS] Dashboard registration failed:', e.message);
  }
}

// Periodic heartbeat: re-register every 20 seconds
let heartbeatTimer = null;
function startHeartbeat() {
  if (heartbeatTimer) clearInterval(heartbeatTimer);
  heartbeatTimer = setInterval(registerPluginWithDashboard, 20000);
}

// ── Init ──────────────────────────────────────────────────────────────────────

loadCfg().then(() => {
  registerPluginWithDashboard();
  startHeartbeat();
  // Auto-detect forms on all active domain tabs on startup
  scanAllActiveDomainTabs();
  console.log('[CCS] Background worker ready v3.0 (auto-detecting forms)');
});

// Re-init on install/update
chrome.runtime.onInstalled.addListener(async () => {
  await loadCfg();
  scanAllActiveDomainTabs();
  console.log('[CCS] Config reloaded after install/update');
});
