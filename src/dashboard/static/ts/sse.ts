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
  // Health stream — updates service indicators live
  _sseConnect('health', '/sse/health', (data: any) => {
    const db = data?.database || {};
    const px = data?.proxy || {};
    const dot = (id: string, status: string) => {
      const el = document.getElementById(id);
      if (el) el.className = 'svc-indicator ' + (status === 'ok' ? 'ok' : status === 'error' ? 'error' : 'unknown');
    };
    dot('health-db-dot', db.status);
    const dbDetail = document.getElementById('health-db-detail');
    if (dbDetail) dbDetail.textContent = db.table_count ? db.table_count + ' tables' : db.status || '—';
    dot('health-proxy-dot', 'ok');
    const proxyDetail = document.getElementById('health-proxy-detail');
    if (proxyDetail) proxyDetail.textContent = (px.providers_enabled || 0) + ' providers';
    const uptimeEl = document.getElementById('health-uptime');
    if (uptimeEl && px.uptime_seconds !== undefined) {
      const s = px.uptime_seconds;
      const h = Math.floor(s / 3600);
      const m = Math.floor((s % 3600) / 60);
      uptimeEl.textContent = h > 0 ? h + 'h ' + m + 'm' : m + 'm';
    }
  });

  // Telemetry stream
  _sseConnect('telemetry', '/sse/telemetry', (_data: any) => {
    // Telemetry data is handled by the telemetry tab renderer
  }, 'telemetry_update');

  // Cases stream
  _sseConnect('cases', '/sse/cases', (_data: any) => {
    // Case updates handled by cases tab
  });

  // Tasks stream
  _sseConnect('tasks', '/sse/tasks', (_data: any) => {
    // Task updates handled by tasks tab
  });

  _sseUpdateBadge();
}
