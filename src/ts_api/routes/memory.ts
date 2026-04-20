/**
 * /ts/memory — Memory tool + context management session
 *
 * POST /ts/memory/run    — run a full memory-aware agent session (SSE)
 * POST /ts/memory/store  — store a fact in the memory file
 * GET  /ts/memory/read   — read current memory file contents
 *
 * Uses BetaLocalFilesystemMemoryTool from @anthropic-ai/sdk/tools/memory/node
 * with context management to auto-clear old tool uses at 30k tokens.
 */

import { Router, type Request, type Response } from 'express';
import path from 'path';
import fs from 'fs/promises';
import Anthropic from '@anthropic-ai/sdk';
import { betaMemoryTool } from '@anthropic-ai/sdk/helpers/beta/memory.js';
import { BetaLocalFilesystemMemoryTool } from '@anthropic-ai/sdk/tools/memory/node.js';
import type { BetaContextManagementConfig } from '@anthropic-ai/sdk/resources/beta/messages/messages.js';

const router = Router();

const MEMORY_DIR = process.env['CYBERSEC_MEMORY_DIR'] ?? path.join(process.cwd(), 'data', 'memory');
const MEMORY_FILE = path.join(MEMORY_DIR, 'memories.md');

const CONTEXT_MANAGEMENT: BetaContextManagementConfig = {
  edits: [
    {
      type: 'clear_tool_uses_20250919',
      trigger: { type: 'input_tokens', value: 30000 },
      keep: { type: 'tool_uses', value: 3 },
    },
  ],
};

function makeClient(): Anthropic {
  return new Anthropic({
    apiKey: process.env['ANTHROPIC_API_KEY'] ?? '',
    baseURL: process.env['ANTHROPIC_BASE_URL'],
    maxRetries: 2,
  });
}

function sseWrite(res: Response, event: string, data: unknown): void {
  res.write(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`);
}

// Run a memory-aware agent session
router.post('/run', async (req: Request, res: Response) => {
  const {
    model = 'claude-sonnet-4-5',
    message,
    max_iterations = 10,
  } = req.body as {
    model?: string;
    message: string;
    max_iterations?: number;
  };

  if (!message) {
    res.status(400).json({ error: 'message required' });
    return;
  }

  await fs.mkdir(MEMORY_DIR, { recursive: true });

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const client = makeClient();
  const t0 = Date.now();

  try {
    const fsMemory = await BetaLocalFilesystemMemoryTool.init(MEMORY_DIR);
    const memory = betaMemoryTool(fsMemory);

    const runner = client.beta.messages.toolRunner({
      model,
      max_tokens: 4096,
      messages: [{ role: 'user', content: message }],
      tools: [memory],
      context_management: CONTEXT_MANAGEMENT,
      betas: ['context-management-2025-06-27'],
      max_iterations,
    });

    for await (const msg of runner) {
      const textBlock = msg.content.find((b) => b.type === 'text');
      if (textBlock && textBlock.type === 'text') {
        sseWrite(res, 'token', { text: textBlock.text });
      }
      const toolUses = msg.content.filter((b) => b.type === 'tool_use');
      for (const t of toolUses) {
        if (t.type === 'tool_use') {
          sseWrite(res, 'memory_op', { op: t.name, input: t.input });
        }
      }
    }

    const final = await runner;
    const finalText = final.content.find((b) => b.type === 'text');
    sseWrite(res, 'done', {
      elapsed_ms: Date.now() - t0,
      stop_reason: final.stop_reason,
      text: finalText && finalText.type === 'text' ? finalText.text : '',
      usage: final.usage,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    sseWrite(res, 'error', { error: msg });
  }

  res.end();
});

// Store a fact directly
router.post('/store', async (req: Request, res: Response) => {
  const { content } = req.body as { content: string };
  if (!content) {
    res.status(400).json({ error: 'content required' });
    return;
  }
  await fs.mkdir(MEMORY_DIR, { recursive: true });
  const ts = new Date().toISOString();
  await fs.appendFile(MEMORY_FILE, `\n<!-- stored at ${ts} -->\n${content}\n`);
  res.json({ stored: true, ts });
});

// Read memory file
router.get('/read', async (_req, res) => {
  try {
    await fs.mkdir(MEMORY_DIR, { recursive: true });
    let content = '';
    try {
      content = await fs.readFile(MEMORY_FILE, 'utf-8');
    } catch {
      content = '(empty)';
    }
    res.json({ content, path: MEMORY_FILE });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    res.status(500).json({ error: msg });
  }
});

export default router;
