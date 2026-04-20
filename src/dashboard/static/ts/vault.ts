// vault.ts — Memory Vault panel: status display + memory-enhanced chat

interface VaultStatus {
  vault_path: string;
  exists: boolean;
  memories: { total: number; by_type: Record<string, number> };
  wiki: { total: number; [k: string]: number };
  canvases: string[];
  hot_cache: { exists: boolean; words: number; last_updated: string | null };
  recent_memories: Array<{ id: string; type: string; path: string }>;
}

export async function loadVaultStatus(): Promise<void> {
  const el = (id: string) => document.getElementById(id);
  try {
    const resp = await fetch('/api/vault/status');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data: VaultStatus = await resp.json();

    const pathEl = el('vault-path');
    if (pathEl) pathEl.textContent = data.vault_path;

    const memEl = el('vault-mem-total');
    if (memEl) memEl.textContent = String(data.memories.total);

    const wikiEl = el('vault-wiki-total');
    if (wikiEl) wikiEl.textContent = String(data.wiki.total);

    const cvEl = el('vault-canvas-total');
    if (cvEl) cvEl.textContent = String(data.canvases.length);

    const hotEl = el('vault-hot-info');
    if (hotEl) {
      if (data.hot_cache.exists) {
        hotEl.textContent = `Hot cache: ${data.hot_cache.words} words · updated ${data.hot_cache.last_updated?.slice(0, 19) ?? '?'}`;
      } else {
        hotEl.textContent = 'Hot cache: not initialised';
      }
    }

    const typeEl = el('vault-type-table');
    if (typeEl) {
      const rows = Object.entries(data.memories.by_type)
        .map(([t, n]) => `<div style="display:flex;justify-content:space-between;padding:2px 0;border-bottom:1px solid var(--border)"><span style="color:var(--text-muted)">${t}</span><span>${n}</span></div>`)
        .join('');
      typeEl.innerHTML = rows || '<span style="color:var(--text-muted)">No memories yet</span>';
    }

    const cvListEl = el('vault-canvas-list');
    if (cvListEl) {
      if (data.canvases.length > 0) {
        cvListEl.innerHTML = data.canvases
          .map(name => `<div style="padding:2px 0;border-bottom:1px solid var(--border);color:var(--accent)">⬡ ${name}</div>`)
          .join('');
      } else {
        cvListEl.innerHTML = '<span style="color:var(--text-muted)">No canvases yet</span>';
      }
    }

    const recentEl = el('vault-recent-list');
    if (recentEl) {
      if (data.recent_memories.length > 0) {
        recentEl.innerHTML = data.recent_memories
          .map(m => `<div style="padding:2px 0;border-bottom:1px solid var(--border)"><span style="color:var(--amber)">[${m.type}]</span> <span style="color:var(--text-muted)">${m.id}</span></div>`)
          .join('');
      } else {
        recentEl.innerHTML = '<span style="color:var(--text-muted)">No memories yet</span>';
      }
    }
  } catch (err) {
    const errMsg = err instanceof Error ? err.message : String(err);
    const pathEl = document.getElementById('vault-path');
    if (pathEl) pathEl.textContent = `Error: ${errMsg}`;
  }
}

export async function vaultChatSend(): Promise<void> {
  const promptEl = document.getElementById('vault-chat-prompt') as HTMLTextAreaElement | null;
  const modelEl = document.getElementById('vault-chat-model') as HTMLInputElement | null;
  const resultEl = document.getElementById('vault-chat-result');
  const spinnerEl = document.getElementById('vault-chat-spinner');

  const prompt = promptEl?.value?.trim();
  if (!prompt) return;

  if (spinnerEl) spinnerEl.style.display = 'inline';
  if (resultEl) { resultEl.style.display = 'none'; resultEl.textContent = ''; }

  try {
    const model = modelEl?.value?.trim() || 'claude-opus-4-5';
    const resp = await fetch('/api/proxy/memory-chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: 2048,
      }),
    });

    const data = await resp.json();

    if (resultEl) {
      resultEl.style.display = 'block';
      if (!resp.ok) {
        resultEl.textContent = `Error: ${data.error ?? resp.statusText}`;
        resultEl.style.color = 'var(--red)';
        return;
      }
      resultEl.style.color = 'var(--text-primary)';
      // Extract text from Anthropic message response
      const content = data.content ?? [];
      const text = content
        .filter((b: any) => b.type === 'text')
        .map((b: any) => b.text)
        .join('\n\n');
      resultEl.textContent = text || JSON.stringify(data, null, 2);
    }

    // Reload vault status to show new memories
    await loadVaultStatus();
  } catch (err) {
    if (resultEl) {
      resultEl.style.display = 'block';
      resultEl.style.color = 'var(--red)';
      resultEl.textContent = `Error: ${err instanceof Error ? err.message : String(err)}`;
    }
  } finally {
    if (spinnerEl) spinnerEl.style.display = 'none';
  }
}
