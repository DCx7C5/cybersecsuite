/**
 * /ts/thinking — Extended thinking mode endpoint
 *
 * POST body: { model?, messages, budget_tokens?, stream? }
 * Returns { thinking_blocks, answer, usage, elapsed_ms }
 * or streams thinking + answer as SSE when stream=true.
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
    model = 'claude-sonnet-4-5-20250929',
    messages,
    budget_tokens = 5000,
    max_tokens,
    stream = false,
  } = req.body as {
    model?: string;
    messages: Anthropic.MessageParam[];
    budget_tokens?: number;
    max_tokens?: number;
    stream?: boolean;
  };

  if (!Array.isArray(messages) || messages.length === 0) {
    res.status(400).json({ error: 'messages array required' });
    return;
  }

  const effectiveBudget = Math.max(1024, Math.min(32000, budget_tokens));
  const effectiveMaxTokens = Math.max(effectiveBudget + 1024, max_tokens ?? effectiveBudget + 2048);

  const client = makeClient();
  const t0 = Date.now();

  if (stream) {
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.flushHeaders();

    try {
      const streamObj = client.messages.stream({
        model,
        max_tokens: effectiveMaxTokens,
        thinking: { type: 'enabled', budget_tokens: effectiveBudget },
        messages,
      });

      let thinkingBuffer = '';
      let answerBuffer = '';

      streamObj.on('streamEvent', (event) => {
        if (event.type === 'content_block_delta') {
          if (event.delta.type === 'thinking_delta') {
            thinkingBuffer += event.delta.thinking;
            sseWrite(res, 'thinking', { text: event.delta.thinking });
          } else if (event.delta.type === 'text_delta') {
            answerBuffer += event.delta.text;
            sseWrite(res, 'token', { text: event.delta.text });
          }
        }
      });

      const final = await streamObj.finalMessage();
      sseWrite(res, 'done', {
        elapsed_ms: Date.now() - t0,
        stop_reason: final.stop_reason,
        usage: final.usage,
        budget_tokens: effectiveBudget,
        thinking_length: thinkingBuffer.length,
        answer_length: answerBuffer.length,
      });
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      sseWrite(res, 'error', { error: msg });
    }

    res.end();
    return;
  }

  // Non-streaming
  try {
    const message = await client.messages.create({
      model,
      max_tokens: effectiveMaxTokens,
      thinking: { type: 'enabled', budget_tokens: effectiveBudget },
      messages,
    });

    const thinkingBlocks = message.content
      .filter((b) => b.type === 'thinking')
      .map((b) => (b as Anthropic.ThinkingBlock).thinking);

    const answerBlocks = message.content
      .filter((b) => b.type === 'text')
      .map((b) => (b as Anthropic.TextBlock).text);

    res.json({
      thinking_blocks: thinkingBlocks,
      answer: answerBlocks.join('\n'),
      usage: message.usage,
      stop_reason: message.stop_reason,
      elapsed_ms: Date.now() - t0,
      budget_tokens: effectiveBudget,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    res.status(500).json({ error: msg });
  }
});

export default router;
