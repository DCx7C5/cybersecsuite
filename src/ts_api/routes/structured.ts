/**
 * /ts/structured — Structured outputs via Zod + client.messages.parse()
 *
 * POST body: { model?, messages, schema_name }
 *
 * schema_name options: "ioc_extraction" | "finding_classification" |
 *   "threat_actor" | "cve_context" | "generic_json"
 *
 * Returns { parsed_output, usage, elapsed_ms }
 */

import { Router, type Request, type Response } from 'express';
import Anthropic from '@anthropic-ai/sdk';
import { zodOutputFormat } from '@anthropic-ai/sdk/helpers/zod.js';
import { z } from 'zod';

const router = Router();

function makeClient(): Anthropic {
  return new Anthropic({
    apiKey: process.env['ANTHROPIC_API_KEY'] ?? '',
    baseURL: process.env['ANTHROPIC_BASE_URL'],
    maxRetries: 2,
  });
}

// ── Forensic Zod schemas ──────────────────────────────────────────────────

const IocExtractionSchema = z.object({
  iocs: z.array(
    z.object({
      type: z.enum(['ip', 'domain', 'url', 'hash_md5', 'hash_sha256', 'email', 'cve', 'other']),
      value: z.string(),
      context: z.string().optional(),
      confidence: z.number().min(0).max(1).optional(),
    }),
  ),
  summary: z.string(),
});

const FindingClassificationSchema = z.object({
  severity: z.enum(['critical', 'high', 'medium', 'low', 'info']),
  category: z.string(),
  mitre_techniques: z.array(z.string()),
  cwe_ids: z.array(z.number()),
  description: z.string(),
  recommendation: z.string(),
  cvss_score: z.number().min(0).max(10).optional(),
});

const ThreatActorSchema = z.object({
  name: z.string(),
  aliases: z.array(z.string()),
  motivation: z.enum(['financial', 'espionage', 'hacktivism', 'destruction', 'unknown']),
  origin: z.string().optional(),
  ttps: z.array(z.string()),
  targeted_sectors: z.array(z.string()),
  active_since: z.string().optional(),
  confidence: z.number().min(0).max(1),
});

const CveContextSchema = z.object({
  cve_id: z.string(),
  description: z.string(),
  cvss_score: z.number().min(0).max(10),
  cvss_vector: z.string().optional(),
  affected_products: z.array(z.string()),
  exploit_available: z.boolean(),
  patch_available: z.boolean(),
  remediation: z.string(),
});

const GenericJsonSchema = z.object({
  result: z.record(z.unknown()),
  reasoning: z.string(),
});

const SCHEMAS = {
  ioc_extraction: IocExtractionSchema,
  finding_classification: FindingClassificationSchema,
  threat_actor: ThreatActorSchema,
  cve_context: CveContextSchema,
  generic_json: GenericJsonSchema,
} as const;

type SchemaName = keyof typeof SCHEMAS;

router.post('/', async (req: Request, res: Response) => {
  const {
    model = 'claude-sonnet-4-5',
    messages,
    schema_name = 'generic_json',
    max_tokens = 2048,
  } = req.body as {
    model?: string;
    messages: Anthropic.MessageParam[];
    schema_name?: string;
    max_tokens?: number;
  };

  if (!Array.isArray(messages) || messages.length === 0) {
    res.status(400).json({ error: 'messages array required' });
    return;
  }

  const schema = SCHEMAS[schema_name as SchemaName];
  if (!schema) {
    res.status(400).json({
      error: `Unknown schema "${schema_name}". Available: ${Object.keys(SCHEMAS).join(', ')}`,
    });
    return;
  }

  const client = makeClient();
  const t0 = Date.now();

  try {
    const message = await client.messages.parse({
      model,
      max_tokens,
      messages,
      output_config: { format: zodOutputFormat(schema) },
    });

    res.json({
      parsed_output: message.parsed_output,
      usage: message.usage,
      stop_reason: message.stop_reason,
      elapsed_ms: Date.now() - t0,
      schema_name,
    });
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    res.status(500).json({ error: msg });
  }
});

router.get('/schemas', (_req, res) => {
  res.json({ schemas: Object.keys(SCHEMAS) });
});

export default router;
