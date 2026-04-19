// Server-Sent Events (SSE) connection management

import { $ } from './core.js';

const _sseConns: Record<string, EventSource> = {};
const _sseConnected = new Set<string>();

export function _sseUpdateBadge(): void {
  const badge = $('sse-status');
  if (!badge) return;
  const n = _sseConnected.size;
  badge.textContent = n === 4 ? '\u25cf SSE Live' : '\u25cf SSE ' + n + '/4';
  badge.className = n === 4 ? 'badge badge-ok' : 'badge badge-standard';
}

type SSEHandler = (data: any) => void;

export function _sseConnect(
  key: string,
  path: string,
  onData: SSEHandler,
  eventName?: string
): void {
  if (_sseConns[key]) {
    try {
      _sseConns[key].close();
    } catch {
      /* ignore */
    }
  }

  const es = new EventSource(path);
  _sseConns[key] = es;

  const handler = (e: Event) => {
    try {
      const msgEvent = e as MessageEvent;
      onData(JSON.parse(msgEvent.data));
    } catch {
      /* ignore parse errors */
    }
  };

  if (eventName) {
    es.addEventListener(eventName, handler);
  } else {
    es.onmessage = handler as EventListener;
  }

  es.onopen = () => {
    _sseConnected.add(key);
    _sseUpdateBadge();
  };

  es.onerror = () => {
    _sseConnected.delete(key);
    _sseUpdateBadge();
    es.close();
    setTimeout(() => _sseConnect(key, path, onData, eventName), 3000);
  };
}

export function initSSE(): void {
  // These render functions are defined in refresh.ts and imported dynamically
  // For now, we register the SSE connections and they'll be hooked up in index.ts
  _updateBadge();
}

// Helper to re-export for use in other modules
function _updateBadge(): void {
  _sseUpdateBadge();
}
