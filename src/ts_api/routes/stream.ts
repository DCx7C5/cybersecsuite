/**
 * /ts/stream — SDK MessageStream SSE endpoint
 *
 * POST body: { model?, system?, messages, max_tokens? }
 * Streams Anthropic SDK events as SSE to the browser.
 */

import { Router, type Request, type Response } from 'express';
import Anthropic from '@anthropic-ai/sdk';

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

router.post('/', async (req: Request, res: Response) => {
  const {
    model = 'claude-sonnet-4-5',
    system,
    messages,
    max_tokens = 2048,
  } = req.body as {
    model?: string;
    system?: string;
    messages: Anthropic.MessageParam[];
    max_tokens?: number;
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

  try {
    const params: Anthropic.MessageStreamParams = {
      model,
      max_tokens,
      messages,
    };
    if (system) params.system = system;

    const stream = client.messages.stream(params);

    stream.on('text', (text) => {
      sseWrite(res, 'token', { text });
    });

    stream.on('contentBlock', (block) => {
      if (block.type === 'tool_use') {
        sseWrite(res, 'tool_start', { name: block.name, id: block.id });
      }
    });

    stream.on('message', (message) => {
      sseWrite(res, 'message', {
        id: message.id,
        stop_reason: message.stop_reason,
        usage: message.usage,
      });
    });

    stream.on('error', (err) => {
      sseWrite(res, 'error', { error: err.message });
      res.end();
    });

    const final = await stream.finalMessage();
    sseWrite(res, 'done', {
      elapsed_ms: Date.now() - t0,
      stop_reason: final.stop_reason,
      usage: final.usage,
      request_id: (final as unknown as { _request_id?: string })._request_id ?? null,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    sseWrite(res, 'error', { error: msg });
  }

  res.end();
});

export default router;
