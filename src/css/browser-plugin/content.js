/**
 * content.js — CyberSecSuite Agent v4.0 content script
 *
 * Runs on every page (document_start). Core features activate only if
 * the current domain is in the configured activeDomains list.
 *
 * Features:
 *  1. XHR + fetch interception — captures API request/response bodies
 *  2. Form detection — shadow DOM traversal + multi-candidate scoring (T023)
 *  3. Idle detection — keystroke + mouse tracking (T024)
 *  4. Human typing simulation — realistic keydown/input/keyup sequences
 *  5. Streaming injection — fetches from /api/proxy/memory-chat
 *  6. Response relay — relays captured AI responses to dashboard (T027)
 */

(() => {
  'use strict';

  // ── State ──────────────────────────────────────────────────────────────────

  let active = false;          // set true once domain check passes
  let cfg = null;              // loaded from background on activation
  const ajaxLog = [];          // captured AJAX events (last 50)
  let streamAbort = null;      // AbortController for active stream

  // ── T024: Idle detection ───────────────────────────────────────────────────

  let _lastActivity = Date.now();

  function _resetActivity() { _lastActivity = Date.now(); }

  function getIdleSeconds() { return Math.floor((Date.now() - _lastActivity) / 1000); }

  document.addEventListener('keydown', _resetActivity, { passive: true, capture: true });
  document.addEventListener('mousemove', _resetActivity, { passive: true, capture: true });
  document.addEventListener('mousedown', _resetActivity, { passive: true, capture: true });
  document.addEventListener('touchstart', _resetActivity, { passive: true, capture: true });

  // ── Activation check ───────────────────────────────────────────────────────

  function checkActivation() {
    chrome.runtime.sendMessage({ action: 'getStatus' }, resp => {
      if (chrome.runtime.lastError || !resp?.cfg) return;
      cfg = resp.cfg;
      const hostname = window.location.hostname;
      active = cfg.enabled &&
        cfg.activeDomains.some(d => hostname === d || hostname.endsWith('.' + d));

      if (active) {
        hookXhr();
        hookFetch();
        console.log(`%c[CCS] Active on ${hostname}`, 'color:#22c55e;font-weight:bold');
      }
    });
  }

  // ── XHR interception ───────────────────────────────────────────────────────

  let xhrHooked = false;
  function hookXhr() {
    if (xhrHooked) return;
    xhrHooked = true;

    const origOpen = XMLHttpRequest.prototype.open;
    const origSend = XMLHttpRequest.prototype.send;

    XMLHttpRequest.prototype.open = function (method, url, ...rest) {
      this._ccsMethod = method;
      this._ccsUrl = String(url);
      return origOpen.call(this, method, url, ...rest);
    };

    XMLHttpRequest.prototype.send = function (body) {
      if (isApiUrl(this._ccsUrl)) {
        const reqBody = body ? String(body).slice(0, 4096) : null;
        this.addEventListener('load', function () {
          captureAjax({
            method: this._ccsMethod,
            url: this._ccsUrl,
            status: this.status,
            requestBody: reqBody,
            responseBody: this.responseText?.slice(0, 4096),
            contentType: this.getResponseHeader('content-type') || '',
            timestamp: Date.now(),
          });
        });
      }
      return origSend.call(this, body);
    };
  }

  // ── Fetch interception ─────────────────────────────────────────────────────

  let fetchHooked = false;
  function hookFetch() {
    if (fetchHooked) return;
    fetchHooked = true;

    const origFetch = window.fetch.bind(window);
    window.fetch = async function (input, init = {}) {
      const url = typeof input === 'string' ? input : input instanceof URL ? input.href : input.url;
      const method = (init.method || 'GET').toUpperCase();

      let reqBody = null;
      if (init.body && isApiUrl(url)) {
        try { reqBody = String(init.body).slice(0, 4096); } catch (_) {}
      }

      const resp = await origFetch(input, init);

      if (isApiUrl(url)) {
        const clone = resp.clone();
        const ct = resp.headers.get('content-type') || '';
        if (!ct.includes('event-stream')) {
          clone.text().then(text => {
            captureAjax({
              method, url, status: resp.status,
              requestBody: reqBody,
              responseBody: text.slice(0, 4096),
              contentType: ct,
              timestamp: Date.now(),
            });
          }).catch(() => {});
        } else {
          captureAjax({
            method, url, status: resp.status,
            requestBody: reqBody,
            responseBody: '[SSE stream]',
            contentType: ct,
            timestamp: Date.now(),
          });
        }
      }

      return resp;
    };
  }

  function isApiUrl(url = '') {
    if (!cfg?.ajaxPatterns) return false;
    return cfg.ajaxPatterns.some(p => url.includes(p));
  }

  function captureAjax(ev) {
    ajaxLog.unshift(ev);
    if (ajaxLog.length > 50) ajaxLog.pop();
  }

  // ── Form detection ─────────────────────────────────────────────────────────

  const FORM_SELECTORS = [
    // Explicit data attributes (most reliable)
    'textarea[data-testid]',
    'div[contenteditable="true"][data-testid]',
    'textarea[data-id]',
    
    // Semantic roles
    '[role="textbox"]',
    '[role="combobox"]',
    'input[type="text"][aria-label]',
    
    // Rich text editors
    '.ProseMirror[contenteditable="true"]',
    '[contenteditable="true"][class*="editor"]',
    '[contenteditable="true"][class*="input"]',
    '[contenteditable="true"][class*="message"]',
    
    // IDs (GitHub, ChatGPT, Claude)
    '#prompt-textarea',
    '#chat-input',
    '#message-input',
    '#user-input',
    
    // Placeholders
    'textarea[placeholder*="message" i]',
    'textarea[placeholder*="prompt" i]',
    'textarea[placeholder*="chat" i]',
    'textarea[placeholder*="ask" i]',
    'input[placeholder*="message" i]',
    'input[placeholder*="prompt" i]',
    'div[placeholder*="message" i][contenteditable="true"]',
    'div[placeholder*="prompt" i][contenteditable="true"]',
    
    // Aria labels
    'div[contenteditable="true"][aria-label]',
    'div[contenteditable="true"][placeholder]',
    'textarea[aria-label*="message" i]',
    'textarea[aria-label*="input" i]',
    
    // Classes commonly used for inputs
    '[class*="input"][contenteditable="true"]',
    '[class*="message-input"][contenteditable="true"]',
    '[class*="chat-input"][contenteditable="true"]',
    '[class*="prompt-input"][contenteditable="true"]',
    
    // Generic but safe
    'form textarea:not([readonly]):not([disabled]):not([hidden])',
    'form input[type="text"]:not([readonly]):not([disabled]):not([hidden])',
    'form div[contenteditable="true"]:not([readonly])',
    
    // Fallback: any visible contenteditable in form (Grok, etc)
    'form div[contenteditable="true"]',
    
    // Last resort: writable textareas
    'textarea:not([readonly]):not([disabled])',
  ];

  function detectChatInput() {
    // First try CSS selectors
    for (const sel of FORM_SELECTORS) {
      try {
        const el = document.querySelector(sel);
        if (el && isVisible(el) && isEditable(el)) return el;
      } catch (_) {}
    }
    
    // Fallback: find any contenteditable div that's visible and has focus capability
    const allEditable = document.querySelectorAll('[contenteditable="true"]');
    for (const el of allEditable) {
      if (isVisible(el) && isEditable(el)) return el;
    }
    
    return null;
  }
  
  function isEditable(el) {
    // Check if element can actually accept input
    if (el.hasAttribute('readonly') || el.hasAttribute('disabled')) return false;
    if (el.type === 'hidden' || el.type === 'button' || el.type === 'submit') return false;
    
    // Contenteditable should be actual text container, not button/label
    const tag = el.tagName.toLowerCase();
    if (tag === 'button' || tag === 'label' || tag === 'a') return false;
    
    return true;
  }

  function isVisible(el) {
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && getComputedStyle(el).display !== 'none';
  }

  function describeForm(el) {
    return {
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      name: el.name || null,
      placeholder: el.placeholder || el.getAttribute('aria-label') || null,
      contenteditable: el.isContentEditable,
      rect: el.getBoundingClientRect().toJSON(),
    };
  }

  // ── Human typing simulation ────────────────────────────────────────────────

  const NATIVE_TA_SETTER = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value')?.set;
  const NATIVE_IN_SETTER = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value')?.set;

  function setNativeValue(el, value) {
    const setter = el instanceof HTMLTextAreaElement ? NATIVE_TA_SETTER : NATIVE_IN_SETTER;
    if (setter) {
      setter.call(el, value);
    } else {
      el.value = value;
    }
  }

  async function humanTypeChar(el, char) {
    const key = char === '\n' ? 'Enter' : char;
    const code = char === '\n' ? 'Enter' : `Key${char.toUpperCase()}`;

    el.dispatchEvent(new KeyboardEvent('keydown', { key, code, bubbles: true, cancelable: true }));
    el.dispatchEvent(new KeyboardEvent('keypress', { key, code, bubbles: true, cancelable: true }));

    if (el.isContentEditable) {
      document.execCommand('insertText', false, char);
    } else {
      setNativeValue(el, el.value + char);
      el.dispatchEvent(new Event('input', { bubbles: true }));
      el.dispatchEvent(new Event('change', { bubbles: true }));
    }

    el.dispatchEvent(new KeyboardEvent('keyup', { key, code, bubbles: true, cancelable: true }));
  }

  async function clearInput(el) {
    el.focus();
    if (el.isContentEditable) {
      el.textContent = '';
      el.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
      setNativeValue(el, '');
      el.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  async function humanType(el, text, speedMs = 28) {
    el.focus();
    for (const char of text) {
      await humanTypeChar(el, char);
      const jitter = (Math.random() - 0.5) * speedMs * 0.6;
      await sleep(Math.max(8, speedMs + jitter));
    }
  }

  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  // ── Submit detection ───────────────────────────────────────────────────────

  function findSubmitButton(inputEl) {
    const parent = inputEl.closest('form') || inputEl.parentElement?.parentElement;
    if (!parent) return null;
    const selectors = [
      'button[type="submit"]',
      'button[aria-label*="send" i]',
      'button[data-testid*="send" i]',
      'button[title*="send" i]',
      'button[aria-label*="Submit" i]',
    ];
    for (const sel of selectors) {
      const btn = parent.querySelector(sel);
      if (btn && isVisible(btn)) return btn;
    }
    return null;
  }

  // ── Streaming injection via Anthropic SDK endpoint ──────────────────────────

  async function injectStreamPrompt(prompt, options = {}) {
    if (!cfg) return { ok: false, error: 'not configured' };

    const inputEl = detectChatInput();
    if (!inputEl) {
      return { ok: false, error: 'no input found' };
    }

    chrome.runtime.sendMessage({ action: 'formDetected', form: describeForm(inputEl) });

    if (streamAbort) { streamAbort.abort(); streamAbort = null; }
    const controller = new AbortController();
    streamAbort = controller;

    const speedMs = options.typingSpeedMs ?? cfg.typingSpeedMs ?? 28;
    let fullText = '';

    try {
      const dashboardUrl = cfg.dashboardUrl || 'http://localhost:8000';

      // Check if dashboard is currently in use
      try {
        const activityResp = await fetch(`${dashboardUrl}/api/activity`, { signal: AbortSignal.timeout(2000) });
        if (activityResp.ok) {
          const activity = await activityResp.json();
          if (activity.active) {
            return { ok: false, error: 'dashboard_in_use', idle_seconds: activity.idle_seconds };
          }
        }
      } catch (_) {
        // Timeout or error — dashboard may be unavailable, proceed anyway
      }

      const resp = await fetch(`${dashboardUrl}/api/proxy/memory-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{ role: 'user', content: prompt }],
          system: `You are responding within: ${location.hostname}. Context URL: ${location.href}. Use memory tools to store relevant findings.`,
        }),
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        return { ok: false, error: `HTTP ${resp.status}` };
      }

      await clearInput(inputEl);

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });
        const parts = buf.split('\n\n');
        buf = parts.pop() ?? '';

        for (const part of parts) {
          let event = 'message', dataStr = '';
          for (const line of part.split('\n')) {
            if (line.startsWith('event: ')) event = line.slice(7).trim();
            else if (line.startsWith('data: ')) dataStr = line.slice(6);
          }
          if (event !== 'content_block_delta' || !dataStr) continue;
          let data;
          try { data = JSON.parse(dataStr); } catch { continue; }
          const delta = data.delta?.text || '';
          if (!delta) continue;
          fullText += delta;
          await humanType(inputEl, delta, speedMs);
        }
      }

      if ((options.autoSubmit ?? cfg.autoSubmit) && fullText.length > 0) {
        const btn = findSubmitButton(inputEl);
        if (btn) {
          await sleep(300);
          btn.click();
        } else {
          inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
        }
      }

      return { ok: true, length: fullText.length, prompt: prompt.slice(0, 60) };

    } catch (e) {
      if (e.name === 'AbortError') return { ok: false, error: 'aborted' };
      return { ok: false, error: String(e) };
    } finally {
      if (streamAbort === controller) streamAbort = null;
    }
  }

  // ── Plain text injection (no AI) ──────────────────────────────────────────

  async function injectText(text, options = {}) {
    const inputEl = detectChatInput();
    if (!inputEl) return { ok: false, error: 'no input found' };

    const speedMs = options.typingSpeedMs ?? cfg?.typingSpeedMs ?? 28;
    await clearInput(inputEl);
    await humanType(inputEl, text, speedMs);
    return { ok: true, length: text.length };
  }

  function extractAjaxResponseSince(startTimestamp) {
    for (const event of ajaxLog) {
      if (!event || event.timestamp < startTimestamp) continue;
      if (typeof event.responseBody !== 'string') continue;
      const body = event.responseBody.trim();
      if (!body || body === '[SSE stream]') continue;
      return body.slice(0, 12000);
    }
    return '';
  }

  function collectAssistantText() {
    const selectors = [
      '[data-message-author-role="assistant"]',
      '[data-testid*="assistant" i]',
      '[class*="assistant-message" i]',
      '[class*="assistant" i]',
    ];
    for (const selector of selectors) {
      try {
        const nodes = Array.from(document.querySelectorAll(selector))
          .map(node => (node.textContent || '').trim())
          .filter(Boolean);
        if (nodes.length > 0) {
          return nodes.slice(-3).join('\n').slice(-12000);
        }
      } catch (_) {}
    }
    return '';
  }

  async function waitForRelayResponse(startTimestamp, assistantBaseline, timeoutMs) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() < deadline) {
      const ajaxBody = extractAjaxResponseSince(startTimestamp);
      if (ajaxBody) {
        return { ok: true, content: ajaxBody, stop_reason: 'stop' };
      }

      const assistantText = collectAssistantText();
      if (assistantText && assistantText !== assistantBaseline) {
        if (assistantBaseline && assistantText.startsWith(assistantBaseline)) {
          const delta = assistantText.slice(assistantBaseline.length).trim();
          if (delta) {
            return { ok: true, content: delta.slice(0, 12000), stop_reason: 'stop' };
          }
        } else {
          return { ok: true, content: assistantText.slice(0, 12000), stop_reason: 'stop' };
        }
      }

      await sleep(250);
    }

    return {
      ok: false,
      error_code: 'response_timeout',
      error: 'timed out while waiting for response observation',
    };
  }

  async function relayInjectPrompt(requestId, prompt, options = {}) {
    if (!requestId) {
      return { ok: false, error_code: 'unknown_request_id', error: 'missing request id' };
    }
    const relayPrompt = String(prompt || '').trim();
    if (!relayPrompt) {
      return { ok: false, error_code: 'injection_failed', error: 'empty prompt' };
    }
    const inputEl = detectChatInput();
    if (!inputEl) {
      return { ok: false, error_code: 'injection_failed', error: 'no input found' };
    }

    chrome.runtime.sendMessage({ action: 'formDetected', form: describeForm(inputEl) });

    const speedMs = options.typingSpeedMs ?? cfg?.typingSpeedMs ?? 28;
    const timeoutMsRaw = options.timeoutMs;
    const timeoutMs = Number.isFinite(timeoutMsRaw) && timeoutMsRaw > 0 ? Number(timeoutMsRaw) : 30000;
    const autoSubmit = options.autoSubmit ?? cfg?.autoSubmit;
    const startTimestamp = Date.now();
    const assistantBaseline = collectAssistantText();

    await clearInput(inputEl);
    await humanType(inputEl, relayPrompt, speedMs);

    if (autoSubmit) {
      const btn = findSubmitButton(inputEl);
      if (btn) {
        await sleep(150);
        btn.click();
      } else {
        inputEl.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', code: 'Enter', bubbles: true }));
      }
    }

    const observed = await waitForRelayResponse(startTimestamp, assistantBaseline, timeoutMs);
    if (!observed.ok) {
      return observed;
    }

    return {
      ok: true,
      request_id: requestId,
      content: observed.content || '',
      stop_reason: observed.stop_reason || 'stop',
    };
  }

  // ── Message handler ───────────────────────────────────────────────────────

  chrome.runtime.onMessage.addListener((req, _sender, sendResponse) => {
    switch (req.action) {
      case 'injectPrompt':
        injectStreamPrompt(req.prompt, req.options || {}).then(sendResponse);
        return true;

      case 'injectText':
        injectText(req.text, req.options || {}).then(sendResponse);
        return true;

      case 'relayInject':
        relayInjectPrompt(req.requestId, req.prompt, req.options || {}).then(sendResponse);
        return true;

      case 'detectForm': {
        const el = detectChatInput();
        sendResponse(el ? { found: true, form: describeForm(el) } : { found: false });
        break;
      }

      case 'getAjaxLog':
        sendResponse({ log: ajaxLog });
        break;

      case 'abortStream':
        if (streamAbort) { streamAbort.abort(); streamAbort = null; }
        sendResponse({ ok: true });
        break;

      case 'ping':
        sendResponse({ ok: true, active, hostname: location.hostname });
        break;

      default:
        break;
    }
    return false;
  });

  // ── Debug helper ──────────────────────────────────────────────────────────

  window.CCS_TEST = {
    findInputs: () => {
      const detected = detectChatInput();
      const allContentEditables = document.querySelectorAll('[contenteditable="true"]');
      const bySelector = document.querySelector('form div[contenteditable="true"]');
      const byRole = document.querySelector('[role="textbox"]');
      const byPlaceholder = document.querySelector('textarea[placeholder*="message" i], div[placeholder*="message" i][contenteditable]');
      
      const result = {
        detected,
        detectedInfo: detected ? describeForm(detected) : null,
        allContentEditableCount: allContentEditables.length,
        bySelector,
        byRole,
        byPlaceholder,
        allEditable: Array.from(allContentEditables).map((el, i) => ({
          index: i,
          tag: el.tagName,
          id: el.id,
          class: el.className?.substring(0, 100),
          visible: isVisible(el),
          editable: isEditable(el),
          placeholder: el.placeholder || el.getAttribute('aria-label')?.substring(0, 50),
        })),
      };
      
      console.log('[CCS] Form detection debug:', result);
      return result;
    },
    
    testInput: (text = 'Test input') => {
      const el = detectChatInput();
      if (!el) {
        console.log('[CCS] No input found');
        return { ok: false, error: 'No input found' };
      }
      console.log('[CCS] Found input:', el);
      clearInput(el).then(() => {
        humanType(el, text, 28).then(() => {
          console.log('[CCS] Text entered: ' + text);
        });
      });
      return { ok: true, element: el, info: describeForm(el) };
    },
  };

  // ── Init ──────────────────────────────────────────────────────────────────

  checkActivation();

})();
