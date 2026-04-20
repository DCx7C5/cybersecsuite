/**
 * /ts/tools — betaTool runner endpoint
 *
 * POST body: { model?, messages, tools: [{name, description, input_schema, run_url?}], max_iterations? }
 *
 * Uses client.beta.messages.toolRunner with betaTool (JSON Schema) helpers.
 * Tools without a run_url return a canned "mock" result useful for demos;
 * tools with a run_url POST the input to that URL and return the response body.
 */

import {type Request, type Response, Router} from 'express';
import Anthropic from '@anthropic-ai/sdk';
import {betaTool} from '@anthropic-ai/sdk/helpers/beta/json-schema.js';

const router = Router();

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

interface ToolDef {
  name: string;
  description: string;
  input_schema: Record<string, unknown>;
  run_url?: string;
}

async function runTool(def: ToolDef, input: Record<string, unknown>): Promise<string> {
  if (def.run_url) {
    const resp = await fetch(def.run_url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
    });
    return await resp.text();
  }
  return JSON.stringify({ result: 'mock', tool: def.name, input });
}

router.post('/', async (req: Request, res: Response) => {
  const {
    model = 'claude-sonnet-4-5',
    messages,
    tools: toolDefs = [],
    max_iterations = 10,
  } = req.body as {
    model?: string;
    messages: Anthropic.Beta.BetaMessageParam[];
    tools: ToolDef[];
    max_iterations?: number;
  };

  if (!Array.isArray(messages) || messages.length === 0) {
    res.status(400).json({ error: 'messages array required' });
    return;
  }

  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.flushHeaders();

  const client = makeClient();
  const t0 = Date.now();

  const runnableTools = toolDefs.map((def) =>
    betaTool({
      name: def.name,
      description: def.description,
      inputSchema: def.input_schema as Parameters<typeof betaTool>[0]['inputSchema'],
      run: async (input: Record<string, unknown>) => {
        sseWrite(res, 'tool_start', { name: def.name });
        const t1 = Date.now();
        const result = await runTool(def, input);
        sseWrite(res, 'tool_done', { name: def.name, elapsed_ms: Date.now() - t1 });
        return result;
      },
    }),
  );

  try {
    const runner = client.beta.messages.toolRunner({
      model,
      max_tokens: 4096,
      messages,
      tools: runnableTools,
      max_iterations,
    });

    for await (const message of runner) {
      const textContent = message.content.find((b) => b.type === 'text');
      if (textContent && textContent.type === 'text') {
        sseWrite(res, 'message', {
          role: message.role,
          text: textContent.text,
          usage: message.usage,
        });
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

export default router;
