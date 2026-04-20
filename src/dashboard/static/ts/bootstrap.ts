/**
 * bootstrap.ts — First-run database bootstrap modal logic.
 *
 * Exported to window:
 *   window._bootstrapRun()   — start bootstrap
 *   window._bootstrapSkip()  — skip and dismiss
 *
 * Called on DOMContentLoaded from index.ts via checkBootstrapStatus().
 */

import { fetchApi } from './core.js';

const POLL_INTERVAL_MS = 1500;
let _pollTimer: ReturnType<typeof setInterval> | null = null;

function overlay(): HTMLElement | null {
  return document.getElementById('bootstrap-overlay');
}

function logEl(): HTMLElement | null {
  return document.getElementById('bootstrap-log');
}

function setStatus(msg: string): void {
  const el = document.getElementById('bootstrap-status-text');
  if (el) el.textContent = msg;
}

function setRunning(running: boolean): void {
  const btn = document.getElementById('bootstrap-run-btn') as HTMLButtonElement | null;
  const skipBtn = document.getElementById('bootstrap-skip-btn') as HTMLButtonElement | null;
  const spinner = document.getElementById('bootstrap-spinner');
  const logWrap = document.getElementById('bootstrap-log-wrap');

  if (btn) btn.disabled = running;
  if (skipBtn) skipBtn.disabled = running;
  if (spinner) spinner.classList.toggle('visible', running);
  if (logWrap) logWrap.classList.toggle('visible', running);
}

function appendLog(lines: string[]): void {
  const el = logEl();
  if (!el) return;
  for (const line of lines) {
    const div = document.createElement('div');
    div.className = 'log-line' + (line.includes('✓') ? ' ok' : line.includes('ERROR') ? ' err' : '');
    div.textContent = line;
    el.appendChild(div);
  }
  el.scrollTop = el.scrollHeight;
}

function dismissModal(): void {
  const ov = overlay();
  if (ov) ov.classList.remove('visible');
  if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
}

async function pollStatus(): Promise<void> {
  try {
    const data = await fetchApi('/api/bootstrap/status');
    if (data.log && data.log.length) appendLog(data.log);

    if (data.done) {
      setStatus('Bootstrap complete ✓');
      setRunning(false);
      if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
      setTimeout(dismissModal, 1500);
      return;
    }
    if (data.error) {
      setStatus('Error: ' + data.error);
      setRunning(false);
      if (_pollTimer) { clearInterval(_pollTimer); _pollTimer = null; }
      return;
    }
    if (data.running) {
      setStatus('Running…');
    }
  } catch {
    setStatus('Connection error — retrying…');
  }
}

export async function checkBootstrapStatus(): Promise<void> {
  try {
    const data = await fetchApi('/api/bootstrap/status');
    if (data.done) return;

    // Not bootstrapped — show the modal
    const ov = overlay();
    if (ov) ov.classList.add('visible');

    if (data.running) {
      // Already running (e.g. CYBERSEC_BOOTSTRAP_INTEL_ON_START=true)
      setRunning(true);
      setStatus('Bootstrap in progress…');
      _pollTimer = setInterval(pollStatus, POLL_INTERVAL_MS);
    }
  } catch {
    // DB/network not ready — silently skip
  }
}

async function postApi(endpoint: string): Promise<any> {
  const r = await fetch(endpoint, { method: 'POST' });
  return r.json();
}

export async function bootstrapRun(): Promise<void> {
  setRunning(true);
  setStatus('Starting…');
  const logWrap = document.getElementById('bootstrap-log-wrap');
  if (logWrap) logWrap.classList.add('visible');
  const logElem = logEl();
  if (logElem) logElem.innerHTML = '';

  try {
    const data = await postApi('/api/bootstrap/run');
    if (!data.started && data.reason === 'already done') {
      dismissModal();
      return;
    }
    if (!data.started) {
      setStatus(data.reason || 'Could not start');
      setRunning(false);
      return;
    }
    _pollTimer = setInterval(pollStatus, POLL_INTERVAL_MS);
  } catch (e: unknown) {
    setStatus('Error: ' + String(e));
    setRunning(false);
  }
}

export async function bootstrapSkip(): Promise<void> {
  try {
    await postApi('/api/bootstrap/skip');
  } catch { /* ignore */ }
  dismissModal();
}
