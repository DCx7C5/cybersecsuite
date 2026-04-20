/**
 * CyberSecSuite TypeScript API Server
 *
 * Lightweight Express server exposing Anthropic SDK capabilities:
 *   POST /ts/stream      — streaming messages via MessageStream
 *   POST /ts/tools       — tool runner with betaTool helpers
 *   POST /ts/structured  — structured outputs with Zod
 *   POST /ts/thinking    — extended thinking mode
 *   POST /ts/memory      — memory tool + context management
 *   GET  /ts/health      — server health
 *
 * All Anthropic calls route through the local AI proxy (port 8000)
 * so API keys never reach the browser.
 */

import express from 'express';
import cors from 'cors';

import streamRouter from './routes/stream.js';
import toolsRouter from './routes/tools.js';
import structuredRouter from './routes/structured.js';
import thinkingRouter from './routes/thinking.js';
import memoryRouter from './routes/memory.js';

const PORT = parseInt(process.env['TS_API_PORT'] ?? '8765', 10);

const app = express();

app.use(cors({ origin: true, credentials: true }));
app.use(express.json({ limit: '4mb' }));

app.use('/ts/stream', streamRouter);
app.use('/ts/tools', toolsRouter);
app.use('/ts/structured', structuredRouter);
app.use('/ts/thinking', thinkingRouter);
app.use('/ts/memory', memoryRouter);

app.get('/ts/health', (_req, res) => {
  res.json({
    status: 'ok',
    service: 'cybersecsuite-ts-api',
    sdk_version: '@anthropic-ai/sdk',
    base_url: process.env['ANTHROPIC_BASE_URL'] ?? 'https://api.anthropic.com',
    ts: new Date().toISOString(),
  });
});

app.listen(PORT, '127.0.0.1', () => {
  console.log(`[ts-api] CyberSecSuite TypeScript API server running on http://127.0.0.1:${PORT}`);
  console.log(`[ts-api] Anthropic base: ${process.env['ANTHROPIC_BASE_URL'] ?? 'https://api.anthropic.com'}`);
});

export default app;
