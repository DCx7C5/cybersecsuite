// Table rendering: sortable, searchable, paginated tables

import { $ } from './core.js';

export interface Column {
  key: string;
  label?: string;
  type?: 'string' | 'number' | 'datetime' | 'bool' | 'json';
}

export interface RenderTableOptions {
  pageSize?: number;
  sortCol?: number | null;
  sortDir?: 'asc' | 'desc';
}

export function renderTable(
  containerId: string,
  schema: Column[],
  rows: Record<string, unknown>[],
  opts: RenderTableOptions = {}
): void {
  const el = $(containerId);
  if (!el) return;

  const pageSize = opts.pageSize || 25;
  let page = 0;
  let sortCol = opts.sortCol ?? null;
  let sortDir = opts.sortDir || 'asc';
  let filter = '';

  function formatCell(val: unknown, col: Column): string {
    if (val === null || val === undefined) return '<span style="color:var(--text-faint)">—</span>';
    const t = col.type || 'string';

    if (t === 'datetime' && val) {
      try {
        return new Date(String(val)).toLocaleString();
      } catch {
        return String(val);
      }
    }

    if (t === 'bool')
      return val ? '<span class="badge badge-ok">YES</span>' : '<span class="badge badge-err">NO</span>';

    if (t === 'json') {
      const s = typeof val === 'string' ? val : JSON.stringify(val);
      return s.length > 80
        ? '<span title="' + s.replace(/"/g, '&quot;') + '">' + s.slice(0, 77) + '&hellip;</span>'
        : s;
    }

    if (t === 'number')
      return typeof val === 'number' ? val.toLocaleString() : String(val);

    const s = String(val);
    return s.length > 120
      ? '<span title="' + s.replace(/"/g, '&quot;') + '">' + s.slice(0, 117) + '&hellip;</span>'
      : s;
  }

  function render(): void {
    let data = rows;

    if (filter) {
      const q = filter.toLowerCase();
      data = data.filter((r) =>
        schema.some((c) => String(r[c.key] || '').toLowerCase().includes(q))
      );
    }

    if (sortCol !== null) {
      const col = schema[sortCol];
      data = [...data].sort((a, b) => {
        let va: string | number = String(a[col.key] ?? '');
        let vb: string | number = String(b[col.key] ?? '');
        if (col.type === 'number') {
          va = Number(va) || 0;
          vb = Number(vb) || 0;
        } else {
          va = va.toLowerCase();
          vb = vb.toLowerCase();
        }
        return sortDir === 'asc'
          ? va < vb
            ? -1
            : va > vb
              ? 1
              : 0
          : va > vb
            ? -1
            : va < vb
              ? 1
              : 0;
      });
    }

    const totalPages = Math.max(1, Math.ceil(data.length / pageSize));
    if (page >= totalPages) page = totalPages - 1;
    const sliced = data.slice(page * pageSize, (page + 1) * pageSize);

    let h = '<div class="rt-bar">';
    const safeName = containerId.replace(/-/g, '_');
    h +=
      '<input type="text" class="rt-search" placeholder="Search…" value="' +
      filter.replace(/"/g, '&quot;') +
      '" ' +
      'oninput="window._rt_' +
      safeName +
      '_filter(this.value)">';
    h += '<span class="rt-count">' + data.length + ' rows</span>';
    h += '</div>';
    h += '<table><thead><tr>';
    schema.forEach((c, i) => {
      const arrow = sortCol === i ? (sortDir === 'asc' ? ' ▲' : ' ▼') : '';
      h +=
        '<th onclick="window._rt_' +
        safeName +
        '_sort(' +
        i +
        ')">' +
        (c.label || c.key) +
        arrow +
        '</th>';
    });
    h += '</tr></thead><tbody>';
    if (!sliced.length) {
      h +=
        '<tr><td colspan="' +
        schema.length +
        '" style="text-align:center;color:var(--text-muted);padding:24px">No data</td></tr>';
    } else {
      sliced.forEach((r) => {
        h += '<tr>';
        schema.forEach((c) => {
          h += '<td>' + formatCell(r[c.key], c) + '</td>';
        });
        h += '</tr>';
      });
    }
    h += '</tbody></table>';
    if (totalPages > 1) {
      h += '<div class="rt-pager">';
      h +=
        '<button class="rt-btn" onclick="window._rt_' +
        safeName +
        '_page(-1)"' +
        (page === 0 ? ' disabled' : '') +
        '>&laquo; Prev</button>';
      h += '<span class="rt-count">Page ' + (page + 1) + ' / ' + totalPages + '</span>';
      h +=
        '<button class="rt-btn" onclick="window._rt_' +
        safeName +
        '_page(1)"' +
        (page >= totalPages - 1 ? ' disabled' : '') +
        '>Next &raquo;</button>';
      h += '</div>';
    }
    el!.innerHTML = h;
  }

  (window as any)['_rt_' + (containerId.replace(/-/g, '_') as string) + '_sort'] = function (
    i: number
  ) {
    if (sortCol === i) sortDir = sortDir === 'asc' ? 'desc' : 'asc';
    else {
      sortCol = i;
      sortDir = 'asc';
    }
    render();
  };

  (window as any)['_rt_' + (containerId.replace(/-/g, '_') as string) + '_filter'] = function (
    v: string
  ) {
    filter = v;
    page = 0;
    render();
  };

  (window as any)['_rt_' + (containerId.replace(/-/g, '_') as string) + '_page'] = function (
    d: number
  ) {
    page += d;
    render();
  };

  render();
}
