// Streaming chat panel: send prompts, consume SSE tokens, export history

import { $ } from './core.js';

interface ChatHistoryEntry {
  role: 'user' | 'assistant';
  content: string;
  ts: string;
}

interface ChatDonePayload {
  elapsed_ms?: number;
  stop_reason?: string;
  text?: string;
}

declare global {
  interface Window {
    acChatHistory: ChatHistoryEntry[];
    acChatStreamMode: boolean;
    _acChatEventSource: EventSource | null;
    _acChatTaskId: string | null;
    _acChatCurrentEl: HTMLElement | null;
    _acChatScrollLocked: boolean;
  }
}

let _assistantBuffer = '';
let _startAbort: AbortController | null = null;

function _ensureState(): void {
  if (!Array.isArray(window.acChatHistory)) window.acChatHistory = [];
  if (typeof window.acChatStreamMode !== 'boolean') window.acChatStreamMode = true;
  window._acChatEventSource = window._acChatEventSource ?? null;
  window._acChatTaskId = window._acChatTaskId ?? null;
  window._acChatCurrentEl = window._acChatCurrentEl ?? null;
  if (typeof window._acChatScrollLocked !== 'boolean') window._acChatScrollLocked = false;
}

function _chatOutput(): HTMLElement | null {
  return $('chat-output');
}

function _chatStatus(): HTMLElement | null {
  return $('chat-status');
}

function _setStatus(text: string, color = 'var(--text-muted)'): void {
  const el = _chatStatus();
  if (!el) return;
  el.textContent = text;
  el.style.color = color;
}

function _setBusy(busy: boolean): void {
  const send = $('chat-send') as HTMLButtonElement | null;
  const stop = $('chat-stop') as HTMLButtonElement | null;
  const input = $('chat-input') as HTMLTextAreaElement | null;
  if (send) send.disabled = busy;
  if (input) input.disabled = busy;
  if (stop) stop.style.display = busy ? '' : 'none';
}

function _escapeHtml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

export function acChatRenderMarkdown(text: string): string {
  const escaped = _escapeHtml(text);
  const lines = escaped.split('\n');
  const htmlLines: string[] = [];

  for (const line of lines) {
    if (line.startsWith('# ')) {
      htmlLines.push('<h4 style="margin:6px 0;font-size:14px">' + line.slice(2) + '</h4>');
      continue;
    }
    if (line.startsWith('- ')) {
      htmlLines.push('<li style="margin-left:18px">' + line.slice(2) + '</li>');
      continue;
    }
    htmlLines.push('<p style="margin:2px 0">' + line + '</p>');
  }

  return htmlLines
    .join('')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code style="background:var(--surface);padding:1px 4px;border-radius:4px">$1</code>');
}

function _bubbleWrap(role: 'user' | 'assistant', html: string): string {
  const isUser = role === 'user';
  const align = isUser ? 'flex-end' : 'flex-start';
  const bg = isUser ? 'var(--accent-glow)' : 'var(--surface)';
  const border = isUser ? 'var(--accent)' : 'var(--border)';
  return (
    '<div style="display:flex;justify-content:' +
    align +
    ';margin-bottom:10px">' +
    '<div style="max-width:82%;padding:10px 12px;background:' +
    bg +
    ';border:1px solid ' +
    border +
    ';border-radius:8px;font-size:13px;line-height:1.45">' +
    html +
    '</div></div>'
  );
}

export function acChatAppendMessage(role: 'user' | 'assistant', content: string): HTMLElement | null {
  const output = _chatOutput();
  if (!output) return null;
  const host = document.createElement('div');
  host.innerHTML = _bubbleWrap(role, acChatRenderMarkdown(content));
  const el = host.firstElementChild as HTMLElement | null;
  if (!el) return null;
  output.appendChild(el);
  acChatAutoScroll();
  return el;
}

function _assistantContentEl(): HTMLElement | null {
  if (!window._acChatCurrentEl) return null;
  const payload = window._acChatCurrentEl.querySelector('div > div');
  return payload as HTMLElement | null;
}

export function acChatAppendUserBubble(text: string): HTMLElement | null {
  return acChatAppendMessage('user', text);
}

export function acChatAppendAssistantBubble(): HTMLElement | null {
  const output = _chatOutput();
  if (!output) return null;
  const host = document.createElement('div');
  host.innerHTML = _bubbleWrap('assistant', '<p style="margin:2px 0;color:var(--text-muted)">...</p>');
  const el = host.firstElementChild as HTMLElement | null;
  if (!el) return null;
  output.appendChild(el);
  window._acChatCurrentEl = el;
  acChatAutoScroll();
  return el;
}

export function acChatAppendToken(text: string): void {
  _assistantBuffer += text;
  const payload = _assistantContentEl();
  if (!payload) return;
  payload.innerHTML = acChatRenderMarkdown(_assistantBuffer + '|');
  acChatAutoScroll();
}

function _findPendingTool(name: string): HTMLElement | null {
  const output = _chatOutput();
  if (!output) return null;
  const pills = output.querySelectorAll<HTMLElement>('[data-tool-name]');
  for (const pill of pills) {
    const pName = pill.dataset.toolName || '';
    const done = pill.dataset.toolDone === '1';
    if (pName === name && !done) return pill;
  }
  return null;
}

export function acChatRenderTool(name: string, elapsedMs?: number): void {
  const output = _chatOutput();
  if (!output) return;

  if (typeof elapsedMs === 'number') {
    const existing = _findPendingTool(name);
    if (existing) {
      existing.textContent = '[tool] ' + name + ' done (' + elapsedMs + 'ms)';
      existing.dataset.toolDone = '1';
    }
    return;
  }

  const pill = document.createElement('div');
  pill.dataset.toolName = name;
  pill.dataset.toolDone = '0';
  pill.textContent = '[tool] using ' + name + '...';
  pill.style.fontSize = '11px';
  pill.style.fontFamily = 'var(--font-mono)';
  pill.style.color = 'var(--text-muted)';
  pill.style.padding = '4px 8px';
  pill.style.border = '1px dashed var(--border)';
  pill.style.borderRadius = '999px';
  pill.style.display = 'inline-block';
  pill.style.margin = '0 0 8px 0';
  output.appendChild(pill);
  acChatAutoScroll();
}

function _closeStream(): void {
  if (window._acChatEventSource) {
    try {
      window._acChatEventSource.close();
    } catch {
      // ignore
    }
  }
  window._acChatEventSource = null;
}

function _finishAssistant(done: ChatDonePayload | null, errorText: string | null): void {
  if (done && typeof done.text === 'string' && !_assistantBuffer) {
    _assistantBuffer = done.text;
  }

  const payload = _assistantContentEl();
  if (payload) {
    const rendered = _assistantBuffer || (errorText ? 'Error: ' + errorText : '');
    payload.innerHTML = acChatRenderMarkdown(rendered);
  }

  if (_assistantBuffer) {
    window.acChatHistory.push({
      role: 'assistant',
      content: _assistantBuffer,
      ts: new Date().toISOString(),
    });
  }

  if (errorText) {
    _setStatus('Error: ' + errorText, 'var(--red)');
  } else {
    const ms = done?.elapsed_ms ?? 0;
    _setStatus('Done in ' + ms + 'ms', 'var(--success)');
  }

  _assistantBuffer = '';
  window._acChatCurrentEl = null;
  window._acChatTaskId = null;
  _closeStream();
  _setBusy(false);
}

function _parseData(e: Event): Record<string, unknown> | null {
  if (!(e instanceof MessageEvent)) return null;
  if (typeof e.data !== 'string') return null;
  try {
    const parsed = JSON.parse(e.data);
    if (parsed && typeof parsed === 'object') {
      return parsed as Record<string, unknown>;
    }
  } catch {
    // ignore parse errors
  }
  return null;
}

function _toggleStreamLabel(): void {
  const btn = $('chat-stream-toggle');
  if (!btn) return;
  btn.textContent = window.acChatStreamMode ? 'Streaming: ON' : 'Streaming: OFF';
}

async function _loadAgents(): Promise<void> {
  const sel = $('chat-agent') as HTMLSelectElement | null;
  if (!sel) return;
  try {
    const res = await fetch('/api/agents');
    const data = await res.json();
    const agents = Array.isArray(data.agents) ? data.agents : [];
    if (!agents.length) return;

    sel.innerHTML = '';
    for (const agent of agents) {
      if (!agent || typeof agent !== 'object') continue;
      const name = String((agent as Record<string, unknown>).name || '').trim();
      if (!name) continue;
      const opt = document.createElement('option');
      opt.value = name;
      opt.textContent = name;
      sel.appendChild(opt);
    }
  } catch {
    // leave default option
  }
}

export async function acChatSend(): Promise<void> {
  _ensureState();
  if (window._acChatTaskId) return;

  const input = $('chat-input') as HTMLTextAreaElement | null;
  const sel = $('chat-agent') as HTMLSelectElement | null;
  if (!input || !sel) return;

  const prompt = input.value.trim();
  const agent = sel.value || 'cybersec-agent';
  if (!prompt) {
    _setStatus('Prompt is empty', 'var(--amber)');
    return;
  }

  acChatAppendUserBubble(prompt);
  window.acChatHistory.push({ role: 'user', content: prompt, ts: new Date().toISOString() });
  input.value = '';

  _assistantBuffer = '';
  acChatAppendAssistantBubble();
  _setBusy(true);
  _setStatus('Starting stream...', 'var(--accent)');

  _startAbort = new AbortController();

  try {
    const res = await fetch('/api/agent-run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        agent,
        prompt,
        stream: window.acChatStreamMode,
      }),
      signal: _startAbort.signal,
    });
    if (!res.ok) throw new Error('start failed: HTTP ' + res.status);
    const data = await res.json();
    const taskId = String(data.task_id || '').trim();
    if (!taskId) throw new Error('missing task_id');

    window._acChatTaskId = taskId;
    _setStatus('Streaming…', 'var(--accent)');

    const es = new EventSource('/sse/agent-run/' + taskId);
    window._acChatEventSource = es;

    es.addEventListener('token', (e) => {
      const dataMap = _parseData(e);
      const text = typeof dataMap?.text === 'string' ? dataMap.text : '';
      if (text) acChatAppendToken(text);
    });

    es.addEventListener('tool_start', (e) => {
      const dataMap = _parseData(e);
      const name = typeof dataMap?.name === 'string' ? dataMap.name : 'tool';
      acChatRenderTool(name);
    });

    es.addEventListener('tool_done', (e) => {
      const dataMap = _parseData(e);
      const name = typeof dataMap?.name === 'string' ? dataMap.name : 'tool';
      const elapsedMs = typeof dataMap?.elapsed_ms === 'number' ? dataMap.elapsed_ms : 0;
      acChatRenderTool(name, elapsedMs);
    });

    es.addEventListener('done', (e) => {
      const dataMap = _parseData(e) || {};
      _finishAssistant(
        {
          elapsed_ms: typeof dataMap.elapsed_ms === 'number' ? dataMap.elapsed_ms : 0,
          stop_reason: typeof dataMap.stop_reason === 'string' ? dataMap.stop_reason : 'end_turn',
          text: typeof dataMap.text === 'string' ? dataMap.text : undefined,
        },
        null
      );
    });

    es.addEventListener('error', (e) => {
      const dataMap = _parseData(e);
      if (dataMap && typeof dataMap.error === 'string' && dataMap.error) {
        _finishAssistant(null, dataMap.error);
      }
    });

    es.onerror = () => {
      if (window._acChatTaskId) {
        _finishAssistant(null, 'stream disconnected');
      }
    };
  } catch (e) {
    const msg = e instanceof Error ? e.message : String(e);
    _finishAssistant(null, msg);
  } finally {
    _startAbort = null;
  }
}

export async function acChatStop(): Promise<void> {
  _ensureState();
  if (_startAbort) {
    _startAbort.abort();
    _startAbort = null;
  }

  const taskId = window._acChatTaskId;
  _closeStream();

  if (taskId) {
    try {
      await fetch('/api/agent-run/' + taskId, { method: 'DELETE' });
    } catch {
      // ignore
    }
  }

  window._acChatTaskId = null;
  window._acChatCurrentEl = null;
  _assistantBuffer = '';
  _setBusy(false);
  _setStatus('Stopped', 'var(--amber)');
}

export function acChatExport(): void {
  _ensureState();
  const lines: string[] = ['# Agent Chat Export', ''];
  for (const item of window.acChatHistory) {
    const role = item.role === 'assistant' ? 'Assistant' : 'User';
    lines.push('## ' + role);
    lines.push(item.content || '');
    lines.push('');
  }
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'chat-' + new Date().toISOString().replace(/[:.]/g, '-') + '.md';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

export function acChatClear(): void {
  _ensureState();
  window.acChatHistory = [];
  const output = _chatOutput();
  if (output) output.innerHTML = '';
  _setStatus('Ready');
}

export function acChatScrollLock(): void {
  const output = _chatOutput();
  if (!output) return;
  const atBottom = output.scrollTop + output.clientHeight >= output.scrollHeight - 8;
  window._acChatScrollLocked = !atBottom;
}

export function acChatAutoScroll(): void {
  const output = _chatOutput();
  if (!output || window._acChatScrollLocked) return;
  output.scrollTop = output.scrollHeight;
}

export function acChatToggleStream(): void {
  _ensureState();
  window.acChatStreamMode = !window.acChatStreamMode;
  _toggleStreamLabel();
}

export async function initChat(): Promise<void> {
  _ensureState();
  _toggleStreamLabel();
  await _loadAgents();

  const input = $('chat-input') as HTMLTextAreaElement | null;
  const output = _chatOutput();

  if (input) {
    input.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        void acChatSend();
      }
    });
  }

  if (output) {
    output.addEventListener('scroll', acChatScrollLock);
  }
}
