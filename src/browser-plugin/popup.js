/**
 * popup.js — CyberSecSuite Agent v3.0 popup controller
 */

// ── State ─────────────────────────────────────────────────────────────────────

let stats = { ajax: 0, streams: 0, forms: 0 };
const logEntries = [];
const ajaxEntries = [];

const DEFAULT_CFG = {
  dashboardUrl:  'http://localhost:8000',
  activeDomains: ['github.com', 'claude.ai', 'platform.openai.com', 'chat.openai.com', 'console.anthropic.com', 'anthropic.com'],
  ajaxPatterns:  ['/v1/messages', '/v1/completions', '/v1/chat/completions', '/api/chat', '/api/generate', 'api.anthropic.com', 'api.openai.com'],
  typingSpeedMs: 28,
  autoSubmit:    false,
  enabled:       true,
};

// ── DOM helpers ───────────────────────────────────────────────────────────────

const $ = id => document.getElementById(id);
function setText(id, t) { const e = $(id); if (e) e.textContent = t; }

// ── Log ───────────────────────────────────────────────────────────────────────

function addLog(msg, kind = '') {
  const ts = new Date().toLocaleTimeString('en', { hour12: false });
  logEntries.unshift({ ts, msg, kind });
  if (logEntries.length > 60) logEntries.pop();
  renderLog();
}

function renderLog() {
  const el = $('event-log');
  if (!el) return;
  el.innerHTML = logEntries.slice(0, 20).map(e =>
    `<div class="log-entry ${e.kind}"><span class="ts">${e.ts}</span>${escHtml(e.msg)}</div>`
  ).join('');
}

function escHtml(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── Connection status ─────────────────────────────────────────────────────────

function setConnectionStatus(connected) {
  const el = $('ws-status');
  if (!el) return;
  if (connected) {
    el.textContent = '● Dashboard';
    el.className = 'ws-badge ws-on';
  } else {
    el.textContent = '● Offline';
    el.className = 'ws-badge ws-off';
  }
}

// ── Domain status ─────────────────────────────────────────────────────────────

function refreshTabInfo() {
  chrome.runtime.sendMessage({ action: 'getTabInfo' }, resp => {
    if (chrome.runtime.lastError || !resp) return;
    setText('domain-name', resp.hostname || '—');
    const badge = $('domain-active');
    if (badge) {
      badge.textContent = resp.active ? 'active' : 'not active';
      badge.className = `sc-badge ${resp.active ? 'badge-on' : 'badge-off'}`;
    }
    
    // Show detected form info
    const formBadge = $('form-detected');
    if (formBadge) {
      if (resp.formDetected && resp.form) {
        formBadge.textContent = `✓ Form found: ${resp.form.placeholder || resp.form.tag}`;
        formBadge.className = 'sc-badge badge-on';
      } else {
        formBadge.textContent = 'No form auto-detected';
        formBadge.className = 'sc-badge badge-off';
      }
    }
  });
}

// ── Stats ─────────────────────────────────────────────────────────────────────

function updateStats() {
  setText('stat-ajax', stats.ajax);
  setText('stat-streams', stats.streams);
  setText('stat-forms', stats.forms);
}

// ── AJAX log rendering ────────────────────────────────────────────────────────

function addAjaxEntry(ev) {
  ajaxEntries.unshift(ev);
  if (ajaxEntries.length > 50) ajaxEntries.pop();
  stats.ajax++;
  updateStats();
  renderAjaxLog();
  addLog(`AJAX ${ev.method} ${ev.status} ${shortUrl(ev.url)}`, ev.status >= 400 ? 'err' : '');
}

function shortUrl(url = '') {
  try {
    const u = new URL(url);
    return u.pathname.slice(0, 50);
  } catch { return url.slice(0, 50); }
}

function renderAjaxLog() {
  const el = $('ajax-log');
  if (!el) return;
  el.innerHTML = ajaxEntries.slice(0, 30).map((ev, i) => {
    const reqBody = ev.requestBody ? escHtml(ev.requestBody.slice(0, 400)) : '(empty)';
    const respBody = ev.responseBody ? escHtml(ev.responseBody.slice(0, 400)) : '(empty)';
    return `
      <div class="ajax-entry" data-idx="${i}" onclick="toggleAjax(this)">
        <span class="ajax-method">${escHtml(ev.method || 'GET')}</span>
        <span class="ajax-status">${ev.status || '?'}</span>
        <span class="ajax-url">${escHtml(shortUrl(ev.url))}</span>
        <div class="ajax-detail">REQUEST:\n${reqBody}\n\nRESPONSE:\n${respBody}</div>
      </div>`;
  }).join('');
}

window.toggleAjax = el => el.classList.toggle('expanded');

// ── Tab navigation ────────────────────────────────────────────────────────────

function initTabs() {
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const tab = `tab-${btn.dataset.tab}`;
      const el = $(tab);
      if (el) el.classList.add('active');
    };
  });
}

// ── Settings load/save ────────────────────────────────────────────────────────

function loadSettings(cfg) {
  if (!cfg) return;
  if ($('s-http-url')) $('s-http-url').value = cfg.dashboardUrl || DEFAULT_CFG.dashboardUrl;
  if ($('s-domains')) $('s-domains').value = (cfg.activeDomains || DEFAULT_CFG.activeDomains).join('\n');
  if ($('s-patterns')) $('s-patterns').value = (cfg.ajaxPatterns || DEFAULT_CFG.ajaxPatterns).join('\n');
  if ($('s-speed')) $('s-speed').value = cfg.typingSpeedMs ?? DEFAULT_CFG.typingSpeedMs;
  if ($('s-enabled')) $('s-enabled').checked = cfg.enabled !== false;
}

function readSettings() {
  return {
    dashboardUrl:  ($('s-http-url')?.value || DEFAULT_CFG.dashboardUrl).trim(),
    activeDomains: ($('s-domains')?.value || '').split('\n').map(s => s.trim()).filter(Boolean),
    ajaxPatterns:  ($('s-patterns')?.value || '').split('\n').map(s => s.trim()).filter(Boolean),
    typingSpeedMs: parseInt($('s-speed')?.value || '28', 10),
    autoSubmit:    $('inject-autosubmit')?.checked || false,
    enabled:       $('s-enabled')?.checked !== false,
  };
}

function saveSettings() {
  const cfg = readSettings();
  chrome.runtime.sendMessage({ action: 'saveCfg', cfg }, resp => {
    const st = $('settings-status');
    if (st) {
      st.textContent = resp?.ok ? '✓ Saved & applied' : '✗ Error saving';
      st.className = `status-line ${resp?.ok ? 'ok' : 'err'}`;
      setTimeout(() => { st.textContent = ''; st.className = 'status-line'; }, 2000);
    }
    addLog('Settings saved', 'ok');
  });
}

// ── Inject ────────────────────────────────────────────────────────────────────

function injectStream() {
  const prompt = $('inject-prompt')?.value?.trim();
  if (!prompt) { setInjectStatus('Enter a prompt first', 'err'); return; }

  const options = {
    typingSpeedMs: parseInt($('inject-speed')?.value || '28', 10),
    autoSubmit:    $('inject-autosubmit')?.checked || false,
  };

  setInjectStatus('Streaming…', 'info');
  chrome.runtime.sendMessage({ action: 'injectPromptManual', prompt, options }, resp => {
    if (chrome.runtime.lastError) {
      setInjectStatus('Error: ' + chrome.runtime.lastError.message, 'err');
      return;
    }
    if (resp?.ok) {
      stats.streams++;
      updateStats();
      setInjectStatus(`Done — ${resp.length ?? '?'} chars`, 'ok');
      addLog(`Stream inject: ${prompt.slice(0, 40)}…`, 'ok');
    } else {
      setInjectStatus('Error: ' + (resp?.error || 'unknown'), 'err');
    }
  });
}

function injectText() {
  const text = $('inject-prompt')?.value?.trim();
  if (!text) { setInjectStatus('Enter text first', 'err'); return; }

  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (!tabs[0]?.id) return;
    chrome.tabs.sendMessage(tabs[0].id, {
      action: 'injectText',
      text,
      options: { typingSpeedMs: parseInt($('inject-speed')?.value || '28', 10) },
    }, resp => {
      if (resp?.ok) {
        stats.streams++;
        updateStats();
        setInjectStatus(`Typed ${resp.length} chars`, 'ok');
      } else {
        setInjectStatus('Error: ' + (resp?.error || 'no active form'), 'err');
      }
    });
  });
}

function abortInject() {
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (tabs[0]?.id) chrome.tabs.sendMessage(tabs[0].id, { action: 'abortStream' });
  });
  setInjectStatus('Aborted', 'warn');
}

function setInjectStatus(msg, kind = '') {
  const el = $('inject-status');
  if (!el) return;
  el.textContent = msg;
  el.className = `status-line ${kind}`;
}

function detectForm() {
  chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
    if (!tabs[0]?.id) { setText('form-info', 'No active tab'); return; }
    chrome.tabs.sendMessage(tabs[0].id, { action: 'detectForm' }, resp => {
      if (chrome.runtime.lastError) { setText('form-info', 'Content script not ready'); return; }
      if (resp?.found) {
        const f = resp.form;
        $('form-info').textContent = `<${f.tag}${f.id ? ' #' + f.id : ''}${f.placeholder ? ` placeholder="${f.placeholder}"` : ''}>\n${JSON.stringify(f.rect, null, 2)}`;
        stats.forms++;
        updateStats();
        addLog(`Form detected: <${f.tag}> ${f.placeholder || ''}`, 'ok');
      } else {
        setText('form-info', 'No AI chat input found on this page');
      }
    });
  });
}

// ── Message listener (from background) ───────────────────────────────────────

chrome.runtime.onMessage.addListener(msg => {
  if (msg.action === 'dashboardStatus') {
    setConnectionStatus(msg.connected);
    addLog(`Dashboard ${msg.connected ? 'connected' : 'disconnected'}`, msg.connected ? 'ok' : 'warn');
  }
  if (msg.action === 'ajaxCapture' && msg.event) {
    addAjaxEntry(msg.event);
  }
  if (msg.action === 'newDetection' && msg.event) {
    addLog(`[detect] ${msg.event.event_type || 'event'}`, msg.event.severity === 'high' ? 'err' : '');
  }
});

// ── Toggle label sync ─────────────────────────────────────────────────────────

function initToggleLabels() {
  const toggle = $('inject-autosubmit');
  const lbl = $('inject-autosubmit-lbl');
  if (!toggle || !lbl) return;
  toggle.onchange = () => { lbl.textContent = toggle.checked ? 'On' : 'Off'; };
}

// ── Init ──────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  initTabs();
  initToggleLabels();

  // Wire buttons
  $('btn-clear-log')?.addEventListener('click', () => { logEntries.length = 0; renderLog(); });
  $('btn-clear-ajax')?.addEventListener('click', () => { ajaxEntries.length = 0; renderAjaxLog(); });
  $('btn-save-settings')?.addEventListener('click', saveSettings);
  $('btn-inject-stream')?.addEventListener('click', injectStream);
  $('btn-inject-text')?.addEventListener('click', injectText);
  $('btn-inject-abort')?.addEventListener('click', abortInject);
  $('btn-detect-form')?.addEventListener('click', detectForm);

  // Load current config from background
  chrome.runtime.sendMessage({ action: 'getStatus' }, resp => {
    if (chrome.runtime.lastError) {
      setConnectionStatus(false);
      addLog('Background not ready', 'err');
      loadSettings(DEFAULT_CFG);
      return;
    }
    setConnectionStatus(resp?.connected || false);
    loadSettings(resp?.cfg || DEFAULT_CFG);
    addLog('Popup ready', 'ok');
  });

  refreshTabInfo();
  updateStats();
});

