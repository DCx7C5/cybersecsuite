/**
 * SDK Panel — TypeScript SDK features panel for the CyberSecSuite dashboard
 *
 * Sub-tabs:
 *   sdk-stream     — streaming via /ts/stream (SDK MessageStream)
 *   sdk-tools      — tool runner via /ts/tools (betaTool)
 *   sdk-structured — structured outputs via /ts/structured (Zod)
 *   sdk-thinking   — extended thinking via /ts/thinking
 *   sdk-memory     — memory tool via /ts/memory
 */

import { $ } from './core.js';

// ── Shared helpers ────────────────────────────────────────────────────────────

const TS_API_BASE = '/ts';

function sseAppend(el: HTMLElement, text: string): void {
  el.textContent += text;
  el.scrollTop = el.scrollHeight;
}

function pre(el: HTMLElement, text: string): void {
  el.textContent = text;
  el.scrollTop = el.scrollHeight;
}

function setStatus(id: string, msg: string, color = 'var(--text-muted)'): void {
  const el = $(id);
  if (!el) return;
  el.textContent = msg;
  (el as HTMLElement).style.color = color;
}

interface SseListener {
  [event: string]: (data: Record<string, unknown>) => void;
}

async function consumeSse(
  url: string,
  body: unknown,
  listeners: SseListener,
): Promise<void> {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!resp.ok || !resp.body) {
    const text = await resp.text();
    listeners['error']?.({ error: text });
    return;
  }

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
      const lines = part.split('\n');
      let event = 'message';
      let dataStr = '';
      for (const line of lines) {
        if (line.startsWith('event: ')) event = line.slice(7).trim();
        else if (line.startsWith('data: ')) dataStr = line.slice(6);
      }
      if (!dataStr) continue;
      let parsed: Record<string, unknown> = {};
      try { parsed = JSON.parse(dataStr) as Record<string, unknown>; } catch { /* skip */ }
      listeners[event]?.(parsed);
    }
  }
}

// ── Stream sub-tab ────────────────────────────────────────────────────────────

export async function sdkStreamRun(): Promise<void> {
  const inputEl = $('sdk-stream-input') as HTMLTextAreaElement | null;
  const outputEl = $('sdk-stream-output');
  if (!inputEl || !outputEl) return;

  const prompt = inputEl.value.trim();
  if (!prompt) return;

  pre(outputEl, '');
  setStatus('sdk-stream-status', 'Streaming…', 'var(--accent)');

  try {
    await consumeSse(`${TS_API_BASE}/stream`, {
      messages: [{ role: 'user', content: prompt }],
    }, {
      token: (d) => sseAppend(outputEl, String(d.text ?? '')),
      tool_start: (d) => sseAppend(outputEl, `\n[tool: ${d.name}]\n`),
      done: (d) => {
        setStatus('sdk-stream-status',
          `Done in ${d.elapsed_ms}ms · ${(d.usage as { output_tokens?: number })?.output_tokens ?? 0} tokens`,
          'var(--success)');
      },
      error: (d) => setStatus('sdk-stream-status', `Error: ${d.error}`, 'var(--red)'),
    });
  } catch (e) {
    setStatus('sdk-stream-status', `Error: ${e instanceof Error ? e.message : String(e)}`, 'var(--red)');
  }
}

// ── Structured sub-tab ────────────────────────────────────────────────────────

export async function sdkStructuredRun(): Promise<void> {
  const inputEl = $('sdk-struct-input') as HTMLTextAreaElement | null;
  const schemaSel = $('sdk-struct-schema') as HTMLSelectElement | null;
  const outputEl = $('sdk-struct-output');
  if (!inputEl || !outputEl || !schemaSel) return;

  const prompt = inputEl.value.trim();
  const schema_name = schemaSel.value;
  if (!prompt) return;

  pre(outputEl, '');
  setStatus('sdk-struct-status', 'Extracting…', 'var(--accent)');

  try {
    const resp = await fetch(`${TS_API_BASE}/structured`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages: [{ role: 'user', content: prompt }], schema_name }),
    });
    const data = await resp.json() as Record<string, unknown>;
    if (data.error) {
      setStatus('sdk-struct-status', `Error: ${data.error}`, 'var(--red)');
    } else {
      pre(outputEl, JSON.stringify(data.parsed_output, null, 2));
      const usage = data.usage as { input_tokens?: number; output_tokens?: number } | undefined;
      setStatus('sdk-struct-status',
        `Done in ${data.elapsed_ms}ms · i:${usage?.input_tokens ?? 0} o:${usage?.output_tokens ?? 0}`,
        'var(--success)');
    }
  } catch (e) {
    setStatus('sdk-struct-status', `Error: ${e instanceof Error ? e.message : String(e)}`, 'var(--red)');
  }
}

// ── Thinking sub-tab ─────────────────────────────────────────────────────────

export async function sdkThinkingRun(): Promise<void> {
  const inputEl = $('sdk-think-input') as HTMLTextAreaElement | null;
  const budgetEl = $('sdk-think-budget') as HTMLInputElement | null;
  const thinkEl = $('sdk-think-thinking');
  const answerEl = $('sdk-think-answer');
  if (!inputEl || !thinkEl || !answerEl) return;

  const prompt = inputEl.value.trim();
  const budget_tokens = parseInt(budgetEl?.value ?? '5000', 10);
  if (!prompt) return;

  pre(thinkEl, '');
  pre(answerEl, '');
  setStatus('sdk-think-status', 'Thinking…', 'var(--accent)');

  try {
    await consumeSse(`${TS_API_BASE}/thinking`, {
      messages: [{ role: 'user', content: prompt }],
      budget_tokens,
      stream: true,
    }, {
      thinking: (d) => sseAppend(thinkEl, String(d.text ?? '')),
      token: (d) => sseAppend(answerEl, String(d.text ?? '')),
      done: (d) => {
        setStatus('sdk-think-status',
          `Done in ${d.elapsed_ms}ms · budget: ${d.budget_tokens} · thinking: ${d.thinking_length}c`,
          'var(--success)');
      },
      error: (d) => setStatus('sdk-think-status', `Error: ${d.error}`, 'var(--red)'),
    });
  } catch (e) {
    setStatus('sdk-think-status', `Error: ${e instanceof Error ? e.message : String(e)}`, 'var(--red)');
  }
}

// ── Tools sub-tab ─────────────────────────────────────────────────────────────

const _defaultTools = [
  {
    name: 'web_search',
    description: 'Search the web for information about a topic.',
    input_schema: {
      type: 'object',
      properties: { query: { type: 'string', description: 'The search query' } },
      required: ['query'],
    },
  },
  {
    name: 'get_iocs',
    description: 'Retrieve indicators of compromise for a threat actor or campaign.',
    input_schema: {
      type: 'object',
      properties: {
        threat_actor: { type: 'string', description: 'Threat actor name or alias' },
        type: { type: 'string', enum: ['ip', 'domain', 'hash', 'all'], description: 'IOC type filter' },
      },
      required: ['threat_actor'],
    },
  },
];

export async function sdkToolsRun(): Promise<void> {
  const promptEl = $('sdk-tools-input') as HTMLTextAreaElement | null;
  const outputEl = $('sdk-tools-output');
  const toolsEl = $('sdk-tools-config') as HTMLTextAreaElement | null;
  if (!promptEl || !outputEl) return;

  const prompt = promptEl.value.trim();
  if (!prompt) return;

  let tools = _defaultTools;
  if (toolsEl?.value.trim()) {
    try { tools = JSON.parse(toolsEl.value) as typeof _defaultTools; } catch { /* keep default */ }
  }

  pre(outputEl, '');
  setStatus('sdk-tools-status', 'Running tool loop…', 'var(--accent)');

  try {
    await consumeSse(`${TS_API_BASE}/tools`, {
      messages: [{ role: 'user', content: prompt }],
      tools,
    }, {
      tool_start: (d) => sseAppend(outputEl, `[→ ${d.name}]\n`),
      tool_done: (d) => sseAppend(outputEl, `[← ${d.name} ${d.elapsed_ms}ms]\n`),
      message: (d) => sseAppend(outputEl, String(d.text ?? '') + '\n'),
      done: (d) => {
        if (d.text) sseAppend(outputEl, '\n--- Final ---\n' + String(d.text));
        setStatus('sdk-tools-status', `Done in ${d.elapsed_ms}ms`, 'var(--success)');
      },
      error: (d) => setStatus('sdk-tools-status', `Error: ${d.error}`, 'var(--red)'),
    });
  } catch (e) {
    setStatus('sdk-tools-status', `Error: ${e instanceof Error ? e.message : String(e)}`, 'var(--red)');
  }
}

// ── Memory sub-tab ────────────────────────────────────────────────────────────

export async function sdkMemoryRun(): Promise<void> {
  const inputEl = $('sdk-mem-input') as HTMLTextAreaElement | null;
  const outputEl = $('sdk-mem-output');
  if (!inputEl || !outputEl) return;

  const message = inputEl.value.trim();
  if (!message) return;

  pre(outputEl, '');
  setStatus('sdk-mem-status', 'Running memory session…', 'var(--accent)');

  try {
    await consumeSse(`${TS_API_BASE}/memory/run`, { message }, {
      token: (d) => sseAppend(outputEl, String(d.text ?? '')),
      memory_op: (d) => sseAppend(outputEl, `\n[memory:${d.op}]\n`),
      done: (d) => {
        setStatus('sdk-mem-status', `Done in ${d.elapsed_ms}ms`, 'var(--success)');
      },
      error: (d) => setStatus('sdk-mem-status', `Error: ${d.error}`, 'var(--red)'),
    });
  } catch (e) {
    setStatus('sdk-mem-status', `Error: ${e instanceof Error ? e.message : String(e)}`, 'var(--red)');
  }
}

export async function sdkMemoryRead(): Promise<void> {
  const outputEl = $('sdk-mem-content');
  if (!outputEl) return;
  try {
    const resp = await fetch(`${TS_API_BASE}/memory/read`);
    const data = await resp.json() as { content: string };
    pre(outputEl, data.content);
  } catch (e) {
    pre(outputEl, `Error: ${e instanceof Error ? e.message : String(e)}`);
  }
}

// ── TS API health ─────────────────────────────────────────────────────────────

export async function sdkApiHealth(): Promise<void> {
  const el = $('sdk-api-health');
  if (!el) return;
  try {
    const resp = await fetch(`${TS_API_BASE}/health`);
    const data = await resp.json() as Record<string, unknown>;
    el.textContent = `TS API ${data.status ?? 'ok'} · SDK: ${data.sdk_version ?? '?'} · base: ${data.base_url ?? '?'}`;
    (el as HTMLElement).style.color = 'var(--success)';
  } catch {
    el.textContent = 'TS API unreachable (start with: cd src/ts_api && npm start)';
    (el as HTMLElement).style.color = 'var(--amber)';
  }
}

export function initSdkPanel(): void {
  sdkApiHealth().catch(() => {});
}
