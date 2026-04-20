// OpenObserve cluster and stream viewer

import { $ } from './core.js';
import { renderTable } from './table.js';

interface ClusterStatus {
  status?: string;
}

interface OpenSearchData {
  error?: string;
  cluster?: ClusterStatus;
  total_docs?: number;
  total_indices?: number;
  indices?: Array<{ index: string; docs: number; size_mb: number }>;
}

export async function loadOpenSearch(): Promise<void> {
  const clusterEl = $('os-cluster');
  if (!clusterEl) return;
  clusterEl.innerHTML = '<div class="loading text-gray-500">Fetching...</div>';
  const indicesEl = $('os-indices');
  if (indicesEl) indicesEl.innerHTML = '';

  try {
    const res = await fetch('/api/opensearch');
    const data: OpenSearchData = await res.json();
    if (data.error && !data.cluster) {
      clusterEl.innerHTML = '<div class="text-red-400">OpenObserve unavailable: ' + data.error + '</div>';
      return;
    }

    const c = data.cluster || {};
    const statusColor: Record<string, string> = {
      healthy: 'text-green-400',
      unavailable: 'text-red-400',
    };
    const colorClass = statusColor[(c.status as string) || ''] || 'text-gray-400';

    clusterEl.innerHTML =
      '<div class="flex gap-6 text-sm mb-3">' +
      '<span class="' +
      colorClass +
      ' font-semibold">&#x25cf; ' +
      ((c.status || 'unavailable').toUpperCase() as string) +
      '</span>' +
      '<span class="text-gray-400">Streams: <strong class="text-white">' +
      (data.total_indices || 0) +
      '</strong></span>' +
      '<span class="text-gray-400">Total docs: <strong class="text-white">' +
      ((data.total_docs || 0).toLocaleString() as string) +
      '</strong></span>' +
      '</div>';

    renderTable(
      'os-indices',
      [
        { key: 'index', label: 'Stream', type: 'string' },
        { key: 'docs', label: 'Docs', type: 'number' },
        { key: 'size_mb', label: 'Size (MB)', type: 'number' },
      ],
      data.indices || []
    );
  } catch (e) {
    clusterEl.innerHTML = '<div class="text-red-400">Error: ' + (e instanceof Error ? e.message : String(e)) + '</div>';
  }
}