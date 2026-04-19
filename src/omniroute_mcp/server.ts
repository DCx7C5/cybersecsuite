/**
 * OmniRoute MCP Server — Self-contained version for CyberSecSuite.
 *
 * This is a standalone copy of OmniRoute's MCP server with all cross-repo
 * imports inlined. Zero dependencies on the OmniRoute source tree.
 *
 * Changes from original:
 *  - resolveOmniRouteBaseUrl, normalizeQuotaResponse, combo step helpers inlined
 *  - Memory tools use HTTP calls to /api/memory/* instead of internal DB imports
 *  - Skill tools use HTTP calls to /api/skills/* instead of internal DB imports
 *  - Audit, scope enforcement, and heartbeat inlined verbatim
 *
 * Configuration (env vars):
 *  OMNIROUTE_BASE_URL          — OmniRoute API base (default: http://localhost:20128)
 *  OMNIROUTE_API_KEY           — Optional API key
 *  OMNIROUTE_MCP_ENFORCE_SCOPES — "true" to block calls missing required scopes
 *  OMNIROUTE_MCP_SCOPES        — Comma-separated allowed scopes
 *  DATA_DIR                    — Override OmniRoute data dir (~/.omniroute)
 */

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { promises as fs } from "node:fs";
import { homedir } from "node:os";
import { join } from "node:path";
import { existsSync } from "node:fs";
import crypto from "node:crypto";

// ============ Configuration ============

function resolveOmniRouteBaseUrl(): string {
  const env = process.env.OMNIROUTE_BASE_URL;
  if (typeof env === "string" && env.trim().length > 0) return env.trim().replace(/\/$/, "");
  return "http://localhost:20128";
}

const OMNIROUTE_BASE_URL = resolveOmniRouteBaseUrl();
const OMNIROUTE_API_KEY = process.env.OMNIROUTE_API_KEY || "";
const MCP_ENFORCE_SCOPES = process.env.OMNIROUTE_MCP_ENFORCE_SCOPES === "true";
const MCP_ALLOWED_SCOPES = new Set(
  (process.env.OMNIROUTE_MCP_SCOPES || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean)
);

const VERSION = "1.9.0"; // bumped for cybersecsuite embedding

// ============ Shared Types ============

type JsonRecord = Record<string, unknown>;

type TextToolResult = {
  content: Array<{ type: "text"; text: string }>;
  isError?: boolean;
};

// ============ Utility Helpers ============

function toRecord(value: unknown): JsonRecord {
  return value && typeof value === "object" && !Array.isArray(value) ? (value as JsonRecord) : {};
}

function toArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function toArrayOfRecords(value: unknown): JsonRecord[] {
  return Array.isArray(value) ? value.filter((v): v is JsonRecord =>
    !!v && typeof v === "object" && !Array.isArray(v)
  ) : [];
}

function toString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function toNumber(value: unknown, fallback = 0): number {
  const parsed =
    typeof value === "number"
      ? value
      : typeof value === "string" && value.trim().length > 0
        ? Number(value)
        : Number.NaN;
  return Number.isFinite(parsed) ? parsed : fallback;
}

function toBoolean(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function toPositiveInt(value: unknown, fallback: number): number {
  const parsed = toNumber(value, fallback);
  return Number.isFinite(parsed) ? Math.max(0, Math.floor(parsed)) : fallback;
}

function toStringArray(value: unknown, fallback: string[] = []): string[] {
  const values = toArray(value).filter((e): e is string => typeof e === "string");
  return values.length > 0 ? values : fallback;
}

// ============ Combo Step Helpers (inlined from OmniRoute lib/combos/steps.ts) ============

function getComboModelString(step: unknown): string {
  const s = toRecord(step);
  // Direct model string
  if (typeof s.model === "string" && s.model.trim()) return s.model.trim();
  // Nested model field
  const nested = toRecord(s.model);
  if (typeof nested.id === "string" && nested.id.trim()) return nested.id.trim();
  return "";
}

function getComboModelProvider(step: unknown): string {
  const s = toRecord(step);
  if (typeof s.provider === "string" && s.provider.trim()) return s.provider.trim();
  const nested = toRecord(s.model);
  if (typeof nested.provider === "string" && nested.provider.trim()) return nested.provider.trim();
  return "";
}

function getComboStepTarget(step: unknown): string {
  const s = toRecord(step);
  // "target" is used when step points to another combo
  if (typeof s.target === "string" && s.target.trim()) return s.target.trim();
  return "";
}

function normalizeComboModels(
  rawModels: unknown
): Array<{ provider: string; model: string; priority: number }> {
  return toArray(rawModels).map((rawModel, index) => {
    const modelRecord = toRecord(rawModel);
    const modelString = getComboModelString(rawModel);
    const target = getComboStepTarget(rawModel);
    const provider =
      getComboModelProvider(rawModel) ||
      (modelString ? "unknown" : target ? "combo" : toString(modelRecord.provider, "unknown"));
    return {
      provider,
      model: modelString || target || toString(modelRecord.model, "unknown"),
      priority: toNumber(modelRecord.priority, index + 1),
    };
  });
}

interface ComboModel {
  provider: string;
  model: string;
  inputCostPer1M: number;
}

function getComboModels(combo: JsonRecord): ComboModel[] {
  const directModels = toArrayOfRecords(combo.models);
  const nestedModels = toArrayOfRecords(toRecord(combo.data).models);
  const sourceModels = directModels.length > 0 ? directModels : nestedModels;
  return sourceModels.map((model) => ({
    provider: getComboModelProvider(model) || (getComboModelString(model) ? "unknown" : "combo"),
    model: getComboModelString(model) || getComboStepTarget(model) || "",
    inputCostPer1M: toNumber(model.inputCostPer1M, 3.0),
  }));
}

function normalizeCombosResponse(raw: unknown): JsonRecord[] {
  if (Array.isArray(raw)) return raw.filter((v): v is JsonRecord =>
    !!v && typeof v === "object" && !Array.isArray(v)
  );
  const source = toRecord(raw);
  return Array.isArray(source.combos)
    ? source.combos.filter((v): v is JsonRecord =>
        !!v && typeof v === "object" && !Array.isArray(v)
      )
    : [];
}

// ============ Quota Normalizer (inlined from OmniRoute shared/contracts/quota.ts) ============

interface QuotaProvider {
  name: string;
  provider: string;
  connectionId: string;
  quotaUsed: number;
  quotaTotal: number | null;
  percentRemaining: number;
  resetAt: string | null;
  tokenStatus: "valid" | "expiring" | "expired" | "refreshing";
}

interface NormalizedQuota {
  providers: QuotaProvider[];
  meta?: {
    generatedAt: string;
    filters: { provider: string | null; connectionId: string | null };
    totalProviders: number;
  };
}

function normalizeQuotaResponse(
  raw: unknown,
  filters?: { provider?: string | null; connectionId?: string | null }
): NormalizedQuota {
  const rawRecord = toRecord(raw);
  const providers: QuotaProvider[] = [];

  const rawProviders = Array.isArray(rawRecord.providers)
    ? rawRecord.providers
    : Array.isArray(raw)
      ? raw
      : [];

  for (const p of rawProviders) {
    const pr = toRecord(p);
    const quotaUsed = toNumber(pr.quotaUsed, 0);
    const quotaTotal = pr.quotaTotal != null ? toNumber(pr.quotaTotal, 0) : null;
    const percentRemaining =
      quotaTotal != null && quotaTotal > 0
        ? Math.max(0, Math.round(((quotaTotal - quotaUsed) / quotaTotal) * 100))
        : pr.quotaTotal == null
          ? 100
          : 0;
    const rawStatus = toString(pr.tokenStatus, "valid");
    const validStatuses = ["valid", "expiring", "expired", "refreshing"] as const;
    const tokenStatus = validStatuses.includes(rawStatus as typeof validStatuses[number])
      ? (rawStatus as QuotaProvider["tokenStatus"])
      : "valid";

    providers.push({
      name: toString(pr.name, toString(pr.provider, "unknown")),
      provider: toString(pr.provider, "unknown"),
      connectionId: toString(pr.connectionId, ""),
      quotaUsed,
      quotaTotal,
      percentRemaining,
      resetAt: pr.resetAt != null ? toString(pr.resetAt) : null,
      tokenStatus,
    });
  }

  return {
    providers,
    meta: {
      generatedAt: new Date().toISOString(),
      filters: {
        provider: filters?.provider ?? null,
        connectionId: filters?.connectionId ?? null,
      },
      totalProviders: providers.length,
    },
  };
}

// ============ HTTP Fetch Helper ============

async function apiFetch(path: string, options: RequestInit = {}): Promise<unknown> {
  const url = `${OMNIROUTE_BASE_URL}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(OMNIROUTE_API_KEY ? { Authorization: `Bearer ${OMNIROUTE_API_KEY}` } : {}),
    ...((options.headers as Record<string, string>) || {}),
  };
  const signal = (options.signal as AbortSignal) ?? AbortSignal.timeout(15000);
  const response = await fetch(url, { ...options, headers, signal });
  if (!response.ok) {
    const errorText = await response.text().catch(() => "Unknown error");
    throw new Error(`OmniRoute API error [${response.status}]: ${errorText}`);
  }
  return response.json();
}

// ============ Audit Logger (inlined from mcp-server/audit.ts) ============

interface AuditDatabase {
  prepare: <TRow = unknown>(sql: string) => {
    get: (...params: unknown[]) => TRow | undefined;
    all: (...params: unknown[]) => TRow[];
    run: (...params: unknown[]) => unknown;
  };
}

function hashInput(input: unknown): string {
  const str = typeof input === "string" ? input : JSON.stringify(input ?? null);
  return crypto.createHash("sha256").update(str).digest("hex").slice(0, 16);
}

function summarizeOutput(output: unknown): string {
  const str = typeof output === "string" ? output : JSON.stringify(output ?? null);
  return str.length > 200 ? str.slice(0, 197) + "..." : str;
}

let _auditDb: AuditDatabase | null = null;
let _auditDbResolved = false;

async function getAuditDb(): Promise<AuditDatabase | null> {
  if (_auditDbResolved) return _auditDb;
  _auditDbResolved = true;
  try {
    const dataDir = process.env.DATA_DIR?.trim() || join(homedir(), ".omniroute");
    const dbPath = join(dataDir, "storage.sqlite");
    if (!existsSync(dbPath)) return null;
    const Database = (await import("better-sqlite3")).default as unknown as new (
      path: string
    ) => AuditDatabase;
    _auditDb = new Database(dbPath);
    // Ensure audit table exists (non-fatal if not)
    try {
      _auditDb.prepare(
        `CREATE TABLE IF NOT EXISTS mcp_tool_audit (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          tool_name TEXT NOT NULL,
          input_hash TEXT NOT NULL,
          output_summary TEXT,
          duration_ms INTEGER,
          api_key_id TEXT,
          success INTEGER NOT NULL DEFAULT 1,
          error_code TEXT,
          created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )`
      ).run();
    } catch { /* non-fatal */ }
    return _auditDb;
  } catch {
    return null;
  }
}

async function logToolCall(
  toolName: string,
  input: unknown,
  output: unknown,
  durationMs: number,
  success: boolean,
  errorCode?: string
): Promise<void> {
  try {
    const db = await getAuditDb();
    if (!db) return;
    db.prepare(
      `INSERT INTO mcp_tool_audit (tool_name, input_hash, output_summary, duration_ms, api_key_id, success, error_code)
       VALUES (?, ?, ?, ?, ?, ?, ?)`
    ).run(
      toolName,
      hashInput(input),
      summarizeOutput(output),
      durationMs,
      process.env.OMNIROUTE_API_KEY_ID ?? null,
      success ? 1 : 0,
      errorCode ?? null
    );
  } catch { /* never block tool execution on audit failure */ }
}

// ============ Scope Enforcement (inlined from mcp-server/scopeEnforcement.ts) ============

type McpToolExtraLike = {
  authInfo?: { clientId?: string; scopes?: string[] };
  sessionId?: string;
  _meta?: unknown;
};

type ScopeSource = "authInfo" | "meta" | "env" | "none";

interface CallerScopeContext {
  callerId: string;
  scopes: string[];
  source: ScopeSource;
}

interface ScopeCheckResult {
  allowed: boolean;
  required: string[];
  provided: string[];
  missing: string[];
  reason?: string;
}

// tool → required scopes map
const TOOL_SCOPES: Record<string, string[]> = {
  omniroute_get_health: ["read:health"],
  omniroute_list_combos: ["read:combos"],
  omniroute_get_combo_metrics: ["read:combos"],
  omniroute_switch_combo: ["write:combos"],
  omniroute_check_quota: ["read:quota"],
  omniroute_route_request: ["execute:completions"],
  omniroute_cost_report: ["read:usage"],
  omniroute_list_models_catalog: ["read:models"],
  omniroute_web_search: ["execute:search"],
  omniroute_simulate_route: ["read:routing"],
  omniroute_set_budget_guard: ["write:budget"],
  omniroute_set_routing_strategy: ["write:combos"],
  omniroute_set_resilience_profile: ["write:resilience"],
  omniroute_test_combo: ["execute:completions", "read:combos"],
  omniroute_get_provider_metrics: ["read:metrics"],
  omniroute_best_combo_for_task: ["read:combos"],
  omniroute_explain_route: ["read:routing"],
  omniroute_get_session_snapshot: ["read:session"],
  omniroute_db_health_check: ["read:admin"],
  omniroute_sync_pricing: ["write:admin"],
  omniroute_memory_search: ["read:memory"],
  omniroute_memory_add: ["write:memory"],
  omniroute_memory_clear: ["write:memory"],
  omniroute_skills_list: ["read:skills"],
  omniroute_skills_enable: ["write:skills"],
  omniroute_skills_execute: ["execute:skills"],
  omniroute_skills_executions: ["read:skills"],
};

function normalizeScopeList(raw: unknown): string[] {
  if (!Array.isArray(raw)) return [];
  return Array.from(
    new Set(
      raw
        .filter((v): v is string => typeof v === "string")
        .map((v) => v.trim())
        .filter(Boolean)
    )
  );
}

function scopeMatches(granted: string, required: string): boolean {
  if (granted === "*" || granted === required) return true;
  if (granted.endsWith("*")) return required.startsWith(granted.slice(0, -1));
  return false;
}

function resolveCallerScopeContext(
  extra: McpToolExtraLike | undefined,
  fallbackScopes: readonly string[] = []
): CallerScopeContext {
  const callerId =
    (typeof extra?.authInfo?.clientId === "string" && extra.authInfo.clientId.trim()) ||
    (typeof extra?.sessionId === "string" && extra.sessionId.trim()) ||
    "anonymous";

  const fromAuthInfo = normalizeScopeList(extra?.authInfo?.scopes);
  if (fromAuthInfo.length > 0)
    return { callerId, scopes: fromAuthInfo, source: "authInfo" };

  const meta = extra?._meta;
  if (meta && typeof meta === "object") {
    const m = meta as Record<string, unknown>;
    const fromMeta = normalizeScopeList(m.scopes)
      || normalizeScopeList((m.auth as Record<string, unknown>)?.scopes)
      || normalizeScopeList((m.omniroute as Record<string, unknown>)?.scopes);
    if (fromMeta.length > 0)
      return { callerId, scopes: fromMeta, source: "meta" };
  }

  if (fallbackScopes.length > 0)
    return { callerId, scopes: [...fallbackScopes], source: "env" };

  return { callerId, scopes: [], source: "none" };
}

function evaluateToolScopes(
  toolName: string,
  provided: string[],
  enforcing: boolean
): ScopeCheckResult {
  const required = TOOL_SCOPES[toolName] || [];
  if (!enforcing || required.length === 0)
    return { allowed: true, required, provided, missing: [] };
  const missing = required.filter(
    (req) => !provided.some((granted) => scopeMatches(granted, req))
  );
  return {
    allowed: missing.length === 0,
    required,
    provided,
    missing,
    reason: missing.length > 0 ? "missing_required_scopes" : undefined,
  };
}

function withScopeEnforcement(
  toolName: string,
  handler: (args: unknown, extra?: McpToolExtraLike) => Promise<TextToolResult>
) {
  return async (args: unknown, extra?: McpToolExtraLike): Promise<TextToolResult> => {
    const ctx = resolveCallerScopeContext(extra, Array.from(MCP_ALLOWED_SCOPES));
    const check = evaluateToolScopes(toolName, ctx.scopes, MCP_ENFORCE_SCOPES);
    if (!check.allowed) {
      const missing = check.missing.join(", ") || "unavailable";
      const msg =
        `Insufficient MCP scopes for ${toolName}. ` +
        `Missing: ${missing}. Caller=${ctx.callerId}, source=${ctx.source}.`;
      await logToolCall(toolName, args, null, 0, false, `scope_denied:${check.reason}`);
      return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
    }
    return handler(args, extra);
  };
}

// ============ Runtime Heartbeat (inlined from mcp-server/runtimeHeartbeat.ts) ============

const HEARTBEAT_INTERVAL_MS = 5000;

async function writeHeartbeat(snapshot: {
  pid: number;
  startedAt: string;
  lastHeartbeatAt: string;
  version: string;
  transport: string;
  scopesEnforced: boolean;
  allowedScopes: string[];
  toolCount: number;
}): Promise<void> {
  const dataDir = process.env.DATA_DIR?.trim() || join(homedir(), ".omniroute");
  const runtimeDir = join(dataDir, "runtime");
  await fs.mkdir(runtimeDir, { recursive: true });
  await fs.writeFile(
    join(runtimeDir, "mcp-heartbeat.json"),
    JSON.stringify(snapshot, null, 2),
    "utf-8"
  );
}

function startMcpHeartbeat(config: {
  version: string;
  scopesEnforced: boolean;
  allowedScopes: string[];
  toolCount: number;
}): () => void {
  const startedAt = new Date().toISOString();
  let stopped = false;

  const tick = async () => {
    if (stopped) return;
    try {
      await writeHeartbeat({
        pid: process.pid,
        startedAt,
        lastHeartbeatAt: new Date().toISOString(),
        version: config.version,
        transport: "stdio",
        scopesEnforced: config.scopesEnforced,
        allowedScopes: [...config.allowedScopes],
        toolCount: config.toolCount,
      });
    } catch {
      /* non-fatal */
    }
  };

  void tick();
  const timer = setInterval(() => void tick(), HEARTBEAT_INTERVAL_MS);

  return () => {
    if (stopped) return;
    stopped = true;
    clearInterval(timer);
    void tick();
  };
}

// ============ Budget Guard State ============

interface BudgetGuardState {
  sessionId: string;
  maxCost: number;
  action: "degrade" | "block" | "alert";
  degradeToTier?: "cheap" | "free";
  spent: number;
  createdAt: string;
}

let activeBudgetGuard: BudgetGuardState | null = null;

// ============ Resilience Profiles ============

const RESILIENCE_PROFILES = {
  aggressive: {
    profiles: {
      oauth: { transientCooldown: 3000, rateLimitCooldown: 30000, maxBackoffLevel: 4, circuitBreakerThreshold: 2, circuitBreakerReset: 30000 },
      apikey: { transientCooldown: 2000, rateLimitCooldown: 0, maxBackoffLevel: 3, circuitBreakerThreshold: 3, circuitBreakerReset: 15000 },
    },
    defaults: { requestsPerMinute: 180, minTimeBetweenRequests: 100, concurrentRequests: 16 },
  },
  balanced: {
    profiles: {
      oauth: { transientCooldown: 5000, rateLimitCooldown: 60000, maxBackoffLevel: 8, circuitBreakerThreshold: 3, circuitBreakerReset: 60000 },
      apikey: { transientCooldown: 3000, rateLimitCooldown: 0, maxBackoffLevel: 5, circuitBreakerThreshold: 5, circuitBreakerReset: 30000 },
    },
    defaults: { requestsPerMinute: 100, minTimeBetweenRequests: 200, concurrentRequests: 10 },
  },
  conservative: {
    profiles: {
      oauth: { transientCooldown: 8000, rateLimitCooldown: 120000, maxBackoffLevel: 10, circuitBreakerThreshold: 8, circuitBreakerReset: 120000 },
      apikey: { transientCooldown: 5000, rateLimitCooldown: 30000, maxBackoffLevel: 8, circuitBreakerThreshold: 8, circuitBreakerReset: 60000 },
    },
    defaults: { requestsPerMinute: 60, minTimeBetweenRequests: 350, concurrentRequests: 6 },
  },
} as const;

// ============ Task Fitness Map ============

const TASK_FITNESS: Record<string, { preferred: string[]; traits: string[] }> = {
  coding:        { preferred: ["claude", "deepseek", "codex"], traits: ["fast", "code-optimized"] },
  review:        { preferred: ["claude", "gemini", "openai"], traits: ["analytical", "thorough"] },
  planning:      { preferred: ["gemini", "claude", "openai"], traits: ["reasoning", "structured"] },
  analysis:      { preferred: ["gemini", "claude"], traits: ["deep-reasoning", "large-context"] },
  debugging:     { preferred: ["claude", "deepseek", "codex"], traits: ["code-aware", "fast"] },
  documentation: { preferred: ["gemini", "claude", "openai"], traits: ["clear", "structured"] },
};

// ============ Input Schemas ============

const getHealthInput = z.object({}).describe("No parameters required");
const listCombosInput = z.object({
  includeMetrics: z.boolean().optional().describe("Include request count, success rate, latency, and cost metrics per combo"),
});
const getComboMetricsInput = z.object({
  comboId: z.string().describe("ID of the combo to get metrics for"),
});
const switchComboInput = z.object({
  comboId: z.string().describe("ID of the combo to activate/deactivate"),
  active: z.boolean().describe("Whether to enable or disable the combo"),
});
const checkQuotaInput = z.object({
  provider: z.string().optional().describe("Filter by provider name (e.g., 'claude', 'gemini'). Omit for all."),
  connectionId: z.string().optional().describe("Filter by specific connection ID"),
});
const routeRequestInput = z.object({
  model: z.string().describe("Model identifier (e.g., 'claude-sonnet-4', 'gpt-4o')"),
  messages: z.array(z.object({ role: z.string(), content: z.string() })).describe("Chat messages in OpenAI format"),
  combo: z.string().optional().describe("Specific combo to route through"),
  budget: z.number().optional().describe("Maximum cost in USD for this request"),
  role: z.enum(["coding", "review", "planning", "analysis"]).optional().describe("Task role hint for intelligent routing"),
  stream: z.boolean().optional().default(false).describe("Whether to stream the response"),
});
const costReportInput = z.object({
  period: z.enum(["session", "day", "week", "month"]).optional().default("session").describe("Time period for the cost report"),
});
const listModelsCatalogInput = z.object({
  provider: z.string().optional().describe("Filter by provider name"),
  capability: z.enum(["chat", "embedding", "image", "audio", "video", "rerank", "moderation"]).optional().describe("Filter by model capability"),
});
const webSearchInput = z.object({
  query: z.string().describe("Search query"),
  max_results: z.number().int().min(1).max(20).optional().default(5).describe("Maximum number of results"),
  search_type: z.enum(["web", "news"]).optional().default("web"),
  provider: z.enum(["serper-search", "brave-search", "perplexity-search", "exa-search", "tavily-search"]).optional().describe("Preferred search provider"),
});
const simulateRouteInput = z.object({
  model: z.string().describe("Model identifier to simulate routing for"),
  promptTokenEstimate: z.number().int().min(1).describe("Estimated number of prompt tokens"),
  combo: z.string().optional().describe("Specific combo to simulate"),
});
const setBudgetGuardInput = z.object({
  maxCost: z.number().positive().describe("Maximum cost in USD for the session"),
  action: z.enum(["degrade", "block", "alert"]).describe("Action when budget is exceeded"),
  degradeToTier: z.enum(["cheap", "free"]).optional().describe("Tier to degrade to (when action=degrade)"),
});
const setRoutingStrategyInput = z.object({
  comboId: z.string().describe("Combo ID or name to update"),
  strategy: z.enum(["priority", "weighted", "round-robin", "context-relay", "strict-random", "random", "least-used", "cost-optimized", "auto"]).describe("New routing strategy"),
  autoRoutingStrategy: z.enum(["rules", "cost", "eco", "latency", "fast"]).optional().describe("Sub-strategy when strategy=auto"),
});
const setResilienceProfileInput = z.object({
  profile: z.enum(["aggressive", "balanced", "conservative"]).describe("Resilience profile to apply"),
});
const testComboInput = z.object({
  comboId: z.string().describe("Combo ID or name to test"),
  testPrompt: z.string().max(200).optional().default("Say hello").describe("Prompt to use for testing each provider"),
});
const getProviderMetricsInput = z.object({
  provider: z.string().describe("Provider name (e.g., 'claude', 'gemini', 'openai')"),
});
const bestComboForTaskInput = z.object({
  taskType: z.enum(["coding", "review", "planning", "analysis", "debugging", "documentation"]).describe("Task type to optimize for"),
  budgetConstraint: z.number().optional().describe("Maximum cost per request in USD"),
  latencyConstraint: z.number().optional().describe("Maximum acceptable latency in ms"),
});
const explainRouteInput = z.object({
  requestId: z.string().describe("Request ID to explain routing decision for"),
});
const getSessionSnapshotInput = z.object({}).describe("No parameters required");
const dbHealthCheckInput = z.object({
  autoRepair: z.boolean().optional().default(false).describe("Whether to automatically repair detected issues"),
});
const syncPricingInput = z.object({
  sources: z.array(z.string()).optional().describe("Pricing sources to sync (default: LiteLLM)"),
  dryRun: z.boolean().optional().default(false).describe("Preview changes without applying"),
});
const memorySearchInput = z.object({
  apiKeyId: z.string().describe("API key ID to scope memory retrieval"),
  query: z.string().optional().describe("Search query for semantic retrieval"),
  type: z.enum(["factual", "episodic", "procedural", "semantic"]).optional().describe("Memory type filter"),
  maxTokens: z.number().int().positive().max(8000).optional().describe("Maximum tokens to return"),
  limit: z.number().int().positive().max(100).optional().describe("Maximum number of memories to return"),
});
const memoryAddInput = z.object({
  apiKeyId: z.string().describe("API key ID to scope this memory"),
  sessionId: z.string().optional().describe("Session ID to associate memory with"),
  type: z.enum(["factual", "episodic", "procedural", "semantic"]).describe("Memory type"),
  key: z.string().min(1).describe("Unique key for this memory"),
  content: z.string().min(1).describe("Memory content"),
  metadata: z.record(z.string(), z.unknown()).optional().describe("Optional metadata"),
});
const memoryClearInput = z.object({
  apiKeyId: z.string().describe("API key ID whose memories to clear"),
  type: z.enum(["factual", "episodic", "procedural", "semantic"]).optional().describe("Memory type to clear (all if omitted)"),
  olderThan: z.string().optional().describe("ISO date — clear memories older than this date"),
});
const skillsListInput = z.object({
  apiKeyId: z.string().optional().describe("Filter by API key ID"),
  name: z.string().optional().describe("Filter by skill name (substring match)"),
  enabled: z.boolean().optional().describe("Filter by enabled state"),
});
const skillsEnableInput = z.object({
  apiKeyId: z.string().describe("API key ID to scope the operation"),
  skillId: z.string().describe("Skill ID to enable/disable"),
  enabled: z.boolean().describe("Whether to enable or disable the skill"),
});
const skillsExecuteInput = z.object({
  apiKeyId: z.string().describe("API key ID to scope execution"),
  skillName: z.string().describe("Name of the skill to execute"),
  input: z.record(z.string(), z.unknown()).describe("Input parameters for the skill"),
  sessionId: z.string().optional().describe("Session ID for context"),
});
const skillsExecutionsInput = z.object({
  apiKeyId: z.string().optional().describe("Filter by API key ID"),
  limit: z.number().int().positive().max(100).optional().describe("Maximum number of executions to return"),
});

// ============ Tool Handlers ============

async function handleGetHealth(): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const [healthRaw, resilienceRaw, rateLimitsRaw] = await Promise.allSettled([
      apiFetch("/api/monitoring/health"),
      apiFetch("/api/resilience"),
      apiFetch("/api/rate-limits"),
    ]);

    const health = healthRaw.status === "fulfilled" ? toRecord(healthRaw.value) : {};
    const resilience = resilienceRaw.status === "fulfilled" ? toRecord(resilienceRaw.value) : {};
    const rateLimits = rateLimitsRaw.status === "fulfilled" ? toRecord(rateLimitsRaw.value) : {};

    const result = {
      uptime: toString(health.uptime, "unknown"),
      version: toString(health.version, "unknown"),
      memoryUsage: {
        heapUsed: toNumber(toRecord(health.memoryUsage).heapUsed, 0),
        heapTotal: toNumber(toRecord(health.memoryUsage).heapTotal, 0),
      },
      circuitBreakers: toArray(resilience.circuitBreakers),
      rateLimits: toArray(rateLimits.limits),
      cacheStats: Object.keys(toRecord(health.cacheStats)).length > 0
        ? {
            hits: toNumber(toRecord(health.cacheStats).hits, 0),
            misses: toNumber(toRecord(health.cacheStats).misses, 0),
            hitRate: toNumber(toRecord(health.cacheStats).hitRate, 0),
          }
        : undefined,
      cryptography: health.cryptography
        ? {
            status: toString(toRecord(health.cryptography).status, "missing_or_invalid"),
            provider: toString(toRecord(health.cryptography).provider, "unknown"),
          }
        : undefined,
    };

    await logToolCall("omniroute_get_health", {}, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_get_health", {}, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleListCombos(args: z.infer<typeof listCombosInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const combosRaw = await apiFetch("/api/combos");
    const combosRecord = toRecord(combosRaw);
    const combos = Array.isArray(combosRecord.combos)
      ? combosRecord.combos
      : Array.isArray(combosRaw) ? combosRaw : [];

    let metrics: JsonRecord = {};
    if (args.includeMetrics) {
      metrics = toRecord(await apiFetch("/api/combos/metrics").catch(() => ({})));
    }

    const result = {
      combos: toArray(combos).map((rawCombo) => {
        const combo = toRecord(rawCombo);
        const comboData = toRecord(combo.data);
        const comboId = toString(combo.id, "");
        const modelsSource = Array.isArray(combo.models) && combo.models.length > 0
          ? combo.models
          : comboData.models;
        return {
          id: comboId,
          name: toString(combo.name, comboId || "unnamed"),
          models: normalizeComboModels(modelsSource),
          strategy: toString(combo.strategy, toString(comboData.strategy, "priority")),
          enabled: combo.enabled !== false,
          ...(args.includeMetrics ? { metrics: metrics[comboId] ?? null } : {}),
        };
      }),
    };

    await logToolCall("omniroute_list_combos", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_list_combos", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleGetComboMetrics(args: z.infer<typeof getComboMetricsInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = await apiFetch(`/api/combos/metrics?comboId=${encodeURIComponent(args.comboId)}`);
    await logToolCall("omniroute_get_combo_metrics", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_get_combo_metrics", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSwitchCombo(args: z.infer<typeof switchComboInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = await apiFetch(`/api/combos/${encodeURIComponent(args.comboId)}`, {
      method: "PUT",
      body: JSON.stringify({ isActive: args.active }),
    });
    await logToolCall("omniroute_switch_combo", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_switch_combo", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleCheckQuota(args: z.infer<typeof checkQuotaInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    let path = "/api/usage/quota";
    if (args.connectionId) path += `?connectionId=${encodeURIComponent(args.connectionId)}`;
    else if (args.provider) path += `?provider=${encodeURIComponent(args.provider)}`;

    const result = normalizeQuotaResponse(await apiFetch(path), {
      provider: args.provider ?? null,
      connectionId: args.connectionId ?? null,
    });

    await logToolCall("omniroute_check_quota", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_check_quota", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleRouteRequest(args: z.infer<typeof routeRequestInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const body: JsonRecord = { model: args.model, messages: args.messages, stream: false };
    if (args.combo) body["x-combo"] = args.combo;

    const raw = toRecord(await apiFetch("/v1/chat/completions", {
      method: "POST",
      body: JSON.stringify(body),
    }));
    const choices = toArray(raw.choices);
    const firstMessage = toRecord(toRecord(choices[0]).message);
    const usage = toRecord(raw.usage);

    const result = {
      response: {
        content: toString(firstMessage.content, ""),
        model: toString(raw.model, args.model),
        tokens: {
          prompt: toNumber(usage.prompt_tokens, 0),
          completion: toNumber(usage.completion_tokens, 0),
        },
      },
      routing: {
        provider: toString(raw.provider, "unknown"),
        combo: raw.combo ?? null,
        fallbacksTriggered: toNumber(raw.fallbacksTriggered, 0),
        cost: toNumber(raw.cost, 0),
        latencyMs: Date.now() - start,
        routingExplanation: toString(raw.routingExplanation, "Request routed through primary provider"),
      },
    };

    await logToolCall("omniroute_route_request", { model: args.model, messageCount: args.messages.length }, result.routing, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_route_request", { model: args.model }, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleCostReport(args: z.infer<typeof costReportInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const period = args.period || "session";
    const rangeMap: Record<string, string> = { session: "1d", day: "1d", week: "7d", month: "30d" };
    const range = rangeMap[period] || "30d";
    const raw = toRecord(await apiFetch(`/api/usage/analytics?range=${encodeURIComponent(range)}`));
    const tokenCount = toRecord(raw.tokenCount);
    const budget = toRecord(raw.budget);

    const result = {
      period,
      totalCost: toNumber(raw.totalCost, 0),
      requestCount: toNumber(raw.requestCount, 0),
      tokenCount: { prompt: toNumber(tokenCount.prompt, 0), completion: toNumber(tokenCount.completion, 0) },
      byProvider: toArray(raw.byProvider),
      byModel: toArray(raw.byModel),
      budget: { limit: budget.limit ?? null, remaining: budget.remaining ?? null },
    };

    await logToolCall("omniroute_cost_report", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_cost_report", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleListModelsCatalog(args: z.infer<typeof listModelsCatalogInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    let path = "/v1/models";
    let isProviderSpecific = false;
    let source = "local_catalog";
    let warning: string | undefined;

    if (args.provider && !args.capability) {
      path = `/api/providers/${encodeURIComponent(args.provider)}/models?excludeHidden=true`;
      isProviderSpecific = true;
    } else {
      const params = new URLSearchParams();
      if (args.provider) params.set("provider", args.provider);
      if (args.capability) params.set("capability", args.capability);
      if (params.toString()) path += `?${params.toString()}`;
    }

    const raw = toRecord(await apiFetch(path));
    let rawModels: unknown[];

    if (isProviderSpecific) {
      rawModels = Array.isArray(raw.models) ? raw.models : [];
      source = typeof raw.source === "string" ? raw.source : "api";
      if (raw.warning) warning = String(raw.warning);
    } else {
      rawModels = Array.isArray(raw.data) ? raw.data : [];
    }

    const result = {
      models: rawModels.map((rawModel) => {
        const model = toRecord(rawModel);
        return {
          id: toString(model.id, ""),
          provider: toString(model.owned_by, toString(model.provider, args.provider || "unknown")),
          capabilities: toStringArray(model.capabilities, ["chat"]),
          status: toString(model.status, "available"),
          pricing: model.pricing,
        };
      }),
      source,
      ...(warning ? { warning } : {}),
    };

    await logToolCall("omniroute_list_models_catalog", args, { modelCount: result.models.length }, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_list_models_catalog", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleWebSearch(args: z.infer<typeof webSearchInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const body: JsonRecord = {
      query: args.query,
      max_results: args.max_results ?? 5,
      search_type: args.search_type ?? "web",
    };
    if (args.provider) body.provider = args.provider;

    const result = await apiFetch("/v1/search", {
      method: "POST",
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(60000),
    });
    await logToolCall("omniroute_web_search", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_web_search", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

// ── Advanced Tools ────────────────────────────────────────────────────────────

async function handleSimulateRoute(args: z.infer<typeof simulateRouteInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const [combosRaw, healthRaw, quotaRaw] = await Promise.allSettled([
      apiFetch("/api/combos"),
      apiFetch("/api/monitoring/health"),
      apiFetch("/api/usage/quota"),
    ]);

    const combos = combosRaw.status === "fulfilled" ? normalizeCombosResponse(combosRaw.value) : [];
    const health = healthRaw.status === "fulfilled" ? toRecord(healthRaw.value) : {};
    const quota = quotaRaw.status === "fulfilled"
      ? normalizeQuotaResponse(quotaRaw.value)
      : normalizeQuotaResponse({});

    const targetCombo = args.combo
      ? combos.find((c) => toString(c.id) === args.combo || toString(c.name) === args.combo)
      : combos.find((c) => c.enabled !== false);

    if (!targetCombo) {
      return { content: [{ type: "text" as const, text: JSON.stringify({ error: "No matching combo found" }) }], isError: true };
    }

    const models = getComboModels(targetCombo);
    const breakers = toArrayOfRecords(health.circuitBreakers);
    const providers = quota.providers;

    const simulatedPath = models.map((model, idx) => {
      const cb = breakers.find((b) => toString(b.provider) === model.provider);
      const q = providers.find((p) => p.provider === model.provider);
      const estimatedCost = (args.promptTokenEstimate / 1_000_000) * model.inputCostPer1M;
      return {
        provider: model.provider,
        model: model.model || args.model,
        probability: idx === 0 ? 0.85 : 0.15 / Math.max(models.length - 1, 1),
        estimatedCost: Math.round(estimatedCost * 10000) / 10000,
        healthStatus: toString(cb?.state, "CLOSED"),
        quotaAvailable: q?.percentRemaining ?? 100,
      };
    });

    const costs = simulatedPath.map((p) => p.estimatedCost);
    const result = {
      simulatedPath,
      fallbackTree: {
        primary: simulatedPath[0]?.provider || "unknown",
        fallbacks: simulatedPath.slice(1).map((p) => p.provider),
        worstCaseCost: Math.max(...costs, 0),
        bestCaseCost: Math.min(...costs, 0),
      },
    };

    await logToolCall("omniroute_simulate_route", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_simulate_route", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSetBudgetGuard(args: z.infer<typeof setBudgetGuardInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    let spent = 0;
    try {
      const analytics = toRecord(await apiFetch("/api/usage/analytics?period=session"));
      spent = toNumber(analytics.totalCost, 0);
    } catch { /* ok if analytics unavailable */ }

    activeBudgetGuard = {
      sessionId: `budget_${Date.now()}`,
      maxCost: args.maxCost,
      action: args.action,
      degradeToTier: args.degradeToTier,
      spent,
      createdAt: new Date().toISOString(),
    };

    const remaining = Math.max(0, args.maxCost - spent);
    const result = {
      sessionId: activeBudgetGuard.sessionId,
      budgetTotal: args.maxCost,
      budgetSpent: Math.round(spent * 10000) / 10000,
      budgetRemaining: Math.round(remaining * 10000) / 10000,
      action: args.action,
      status: remaining <= 0 ? "exceeded" : remaining < args.maxCost * 0.2 ? "warning" : "active",
    };

    await logToolCall("omniroute_set_budget_guard", { maxCost: args.maxCost, action: args.action }, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_set_budget_guard", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSetRoutingStrategy(args: z.infer<typeof setRoutingStrategyInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const combos = normalizeCombosResponse(await apiFetch("/api/combos"));
    const combo = combos.find(
      (c) => toString(c.id) === args.comboId || toString(c.name) === args.comboId
    );

    if (!combo) {
      const msg = `Combo '${args.comboId}' not found`;
      await logToolCall("omniroute_set_routing_strategy", args, null, Date.now() - start, false, msg);
      return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
    }

    const comboId = toString(combo.id);
    const comboData = toRecord(combo.data);
    const currentConfig = toRecord(
      Object.keys(toRecord(combo.config)).length > 0 ? combo.config : comboData.config
    );

    let nextConfig: JsonRecord | undefined;
    if (args.strategy === "auto" && args.autoRoutingStrategy) {
      nextConfig = {
        ...currentConfig,
        auto: { ...toRecord(currentConfig.auto), routingStrategy: args.autoRoutingStrategy },
      };
    }

    const payload: JsonRecord = { strategy: args.strategy };
    if (nextConfig && Object.keys(nextConfig).length > 0) payload.config = nextConfig;

    const updatedCombo = toRecord(
      await apiFetch(`/api/combos/${encodeURIComponent(comboId)}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      })
    );

    const updatedConfig = toRecord(updatedCombo.config);
    const resolvedAutoStrategy =
      toString(toRecord(updatedConfig.auto).routingStrategy) ||
      (args.strategy === "auto" ? (args.autoRoutingStrategy ?? "rules") : "");

    const result = {
      success: true,
      combo: {
        id: toString(updatedCombo.id, comboId),
        name: toString(updatedCombo.name, toString(combo.name, comboId)),
        strategy: toString(updatedCombo.strategy, args.strategy),
        autoRoutingStrategy:
          toString(updatedCombo.strategy, args.strategy) === "auto" ? resolvedAutoStrategy : null,
      },
    };

    await logToolCall("omniroute_set_routing_strategy", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_set_routing_strategy", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSetResilienceProfile(args: z.infer<typeof setResilienceProfileInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const settings = RESILIENCE_PROFILES[args.profile];
    await apiFetch("/api/resilience", {
      method: "PATCH",
      body: JSON.stringify({ profiles: settings.profiles, defaults: settings.defaults }),
    });
    const result = { applied: true, profile: args.profile, settings };
    await logToolCall("omniroute_set_resilience_profile", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_set_resilience_profile", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleTestCombo(args: z.infer<typeof testComboInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const combos = normalizeCombosResponse(await apiFetch("/api/combos"));
    const combo = combos.find(
      (c) => toString(c.id) === args.comboId || toString(c.name) === args.comboId
    );
    if (!combo) {
      return { content: [{ type: "text" as const, text: JSON.stringify({ error: `Combo "${args.comboId}" not found` }) }], isError: true };
    }

    const models = getComboModels(combo);
    const prompt = (args.testPrompt || "Say hello").slice(0, 200);

    const results = await Promise.allSettled(
      models.map(async (model) => {
        const t0 = Date.now();
        try {
          const resp = toRecord(await apiFetch("/v1/chat/completions", {
            method: "POST",
            body: JSON.stringify({
              model: model.model || "auto",
              messages: [{ role: "user", content: prompt }],
              max_tokens: 50,
              stream: false,
              "x-provider": model.provider,
            }),
          }));
          const usage = toRecord(resp.usage);
          return {
            provider: model.provider,
            model: model.model || toString(resp.model, "unknown"),
            success: true,
            latencyMs: Date.now() - t0,
            cost: toNumber(resp.cost, 0),
            tokenCount: toNumber(usage.prompt_tokens, 0) + toNumber(usage.completion_tokens, 0),
          };
        } catch (err) {
          return {
            provider: model.provider,
            model: model.model || "unknown",
            success: false,
            latencyMs: Date.now() - t0,
            cost: 0,
            tokenCount: 0,
            error: err instanceof Error ? err.message : String(err),
          };
        }
      })
    );

    const providerResults = results.map((r) =>
      r.status === "fulfilled"
        ? r.value
        : { provider: "unknown", model: "unknown", success: false, latencyMs: 0, cost: 0, tokenCount: 0, error: "Promise rejected" }
    );
    const successful = providerResults.filter((r) => r.success);
    const fastest = [...successful].sort((a, b) => a.latencyMs - b.latencyMs)[0];
    const cheapest = [...successful].sort((a, b) => a.cost - b.cost)[0];

    const result = {
      results: providerResults,
      summary: {
        totalProviders: providerResults.length,
        successful: successful.length,
        fastestProvider: fastest?.provider || "none",
        cheapestProvider: cheapest?.provider || "none",
      },
    };

    await logToolCall("omniroute_test_combo", { comboId: args.comboId }, result.summary, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_test_combo", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleGetProviderMetrics(args: z.infer<typeof getProviderMetricsInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const [healthRaw, quotaRaw, analyticsRaw] = await Promise.allSettled([
      apiFetch("/api/monitoring/health"),
      apiFetch(`/api/usage/quota?provider=${encodeURIComponent(args.provider)}`),
      apiFetch(`/api/usage/analytics?period=session&provider=${encodeURIComponent(args.provider)}`),
    ]);

    const health = healthRaw.status === "fulfilled" ? toRecord(healthRaw.value) : {};
    const quota = quotaRaw.status === "fulfilled"
      ? normalizeQuotaResponse(quotaRaw.value, { provider: args.provider })
      : normalizeQuotaResponse({});
    const analytics = analyticsRaw.status === "fulfilled" ? toRecord(analyticsRaw.value) : {};

    const cb = toArrayOfRecords(health.circuitBreakers).find((b) => toString(b.provider) === args.provider);
    const providerQuota = quota.providers.find((p) => p.provider === args.provider) ?? null;

    const result = {
      provider: args.provider,
      successRate: toNumber(analytics.successRate, 1.0),
      requestCount: toNumber(analytics.requestCount, 0),
      avgLatencyMs: toNumber(analytics.avgLatencyMs, 0),
      p50LatencyMs: toNumber(analytics.p50LatencyMs, 0),
      p95LatencyMs: toNumber(analytics.p95LatencyMs, 0),
      p99LatencyMs: toNumber(analytics.p99LatencyMs, 0),
      errorRate: toNumber(analytics.errorRate, 0),
      lastError: toString(analytics.lastError) || null,
      circuitBreakerState: toString(cb?.state, "CLOSED"),
      quotaInfo: providerQuota
        ? { used: providerQuota.quotaUsed, total: providerQuota.quotaTotal, resetAt: providerQuota.resetAt }
        : { used: 0, total: null, resetAt: null },
    };

    await logToolCall("omniroute_get_provider_metrics", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_get_provider_metrics", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleBestComboForTask(args: z.infer<typeof bestComboForTaskInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const fitness = TASK_FITNESS[args.taskType] || TASK_FITNESS.coding;
    const combos = normalizeCombosResponse(await apiFetch("/api/combos"));
    const enabledCombos = combos.filter((c) => c.enabled !== false);

    if (enabledCombos.length === 0) {
      return { content: [{ type: "text" as const, text: JSON.stringify({ error: "No enabled combos available" }) }], isError: true };
    }

    const scored = enabledCombos.map((combo) => {
      const models = getComboModels(combo);
      let score = 0;
      for (const model of models) {
        const prefIdx = fitness.preferred.indexOf(model.provider);
        if (prefIdx >= 0) score += (fitness.preferred.length - prefIdx) * 10;
      }
      const name = toString(combo.name).toLowerCase();
      for (const trait of fitness.traits) {
        if (name.includes(trait)) score += 5;
      }
      const isFree = name.includes("free") || models.every((m) => m.provider.toLowerCase().includes("free"));
      return { combo, score, isFree };
    });
    scored.sort((a, b) => b.score - a.score);

    const best = scored[0];
    const alternatives = scored.slice(1, 4).map((s) => ({
      id: s.combo.id,
      name: s.combo.name,
      tradeoff: s.isFree
        ? "free but may have limits"
        : s.score < best.score * 0.5
          ? "cheaper but slower"
          : "similar quality, different providers",
    }));
    const freeAlt = scored.find((s) => s.isFree && s !== best);

    const result = {
      recommendedCombo: {
        id: best.combo.id,
        name: best.combo.name,
        reason: `Best match for "${args.taskType}": preferred providers (${fitness.preferred.slice(0, 3).join(", ")})`,
      },
      alternatives,
      freeAlternative: freeAlt ? { id: freeAlt.combo.id, name: freeAlt.combo.name } : null,
    };

    await logToolCall("omniroute_best_combo_for_task", args, result.recommendedCombo, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_best_combo_for_task", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleExplainRoute(args: z.infer<typeof explainRouteInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    let decision: JsonRecord | null = null;
    try {
      decision = toRecord(await apiFetch(`/api/routing/decisions/${encodeURIComponent(args.requestId)}`));
    } catch { /* fallback to generic explanation */ }

    const defaultFactors = [
      { name: "health",   value: 1,   weight: 0.30, contribution: 0.300 },
      { name: "quota",    value: 1,   weight: 0.25, contribution: 0.250 },
      { name: "cost",     value: 0.8, weight: 0.20, contribution: 0.160 },
      { name: "latency",  value: 0.9, weight: 0.15, contribution: 0.135 },
      { name: "task_fit", value: 0.7, weight: 0.10, contribution: 0.070 },
    ];

    const result = decision
      ? {
          requestId: args.requestId,
          decision: {
            comboUsed:          decision.comboUsed          || "default",
            providerSelected:   decision.providerSelected   || "unknown",
            modelUsed:          decision.modelUsed          || "unknown",
            score:              decision.score              || 0,
            factors:            decision.factors            || defaultFactors,
            fallbacksTriggered: decision.fallbacksTriggered || [],
            costActual:         decision.costActual         || 0,
            latencyActual:      decision.latencyActual      || 0,
          },
        }
      : {
          requestId: args.requestId,
          decision: {
            comboUsed: "unknown", providerSelected: "unknown", modelUsed: "unknown",
            score: 0, factors: [], fallbacksTriggered: [], costActual: 0, latencyActual: 0,
          },
          note: "Routing decision not found — requestId may be invalid or endpoint not yet available.",
        };

    await logToolCall("omniroute_explain_route", args, { requestId: args.requestId }, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_explain_route", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleGetSessionSnapshot(): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const analytics = toRecord(await apiFetch("/api/usage/analytics?period=session").catch(() => ({})));
    const tokenCount = toRecord(analytics.tokenCount);

    const result = {
      sessionStart: toString(analytics.sessionStart, new Date().toISOString()),
      duration: toString(analytics.duration, "unknown"),
      requestCount: toNumber(analytics.requestCount, 0),
      costTotal: toNumber(analytics.totalCost, 0),
      tokenCount: { prompt: toNumber(tokenCount.prompt, 0), completion: toNumber(tokenCount.completion, 0) },
      topModels: toArrayOfRecords(analytics.byModel).slice(0, 5).map((m) => ({
        model: toString(m.model, "unknown"),
        count: toNumber(m.requests, 0),
      })),
      topProviders: toArrayOfRecords(analytics.byProvider).slice(0, 5).map((p) => ({
        provider: toString(p.name, "unknown"),
        count: toNumber(p.requests, 0),
      })),
      errors: toNumber(analytics.errorCount, 0),
      fallbacks: toNumber(analytics.fallbackCount, 0),
      budgetGuard: activeBudgetGuard
        ? {
            active: true,
            remaining: Math.max(0, activeBudgetGuard.maxCost - activeBudgetGuard.spent),
            action: activeBudgetGuard.action,
          }
        : null,
    };

    await logToolCall("omniroute_get_session_snapshot", {}, { requestCount: result.requestCount }, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_get_session_snapshot", {}, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleDbHealthCheck(args: z.infer<typeof dbHealthCheckInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = toRecord(await apiFetch("/api/v1/db/health", {
      method: args.autoRepair ? "POST" : "GET",
    }));
    await logToolCall("omniroute_db_health_check", args, { isHealthy: toBoolean(result.isHealthy), repairedCount: toNumber(result.repairedCount) }, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_db_health_check", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSyncPricing(args: z.infer<typeof syncPricingInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = toRecord(await apiFetch("/api/pricing/sync", {
      method: "POST",
      body: JSON.stringify({ sources: args.sources, dryRun: args.dryRun ?? false }),
    }));
    await logToolCall("omniroute_sync_pricing", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_sync_pricing", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

// ── Memory Tools (HTTP-based — replaces OmniRoute internal @/lib/memory/* imports) ──

async function handleMemorySearch(args: z.infer<typeof memorySearchInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const params = new URLSearchParams({ apiKeyId: args.apiKeyId });
    if (args.query) params.set("query", args.query);
    if (args.type) params.set("type", args.type);
    if (args.limit) params.set("limit", String(args.limit));
    if (args.maxTokens) params.set("maxTokens", String(args.maxTokens));

    const result = await apiFetch(`/api/memory?${params.toString()}`);
    await logToolCall("omniroute_memory_search", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_memory_search", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleMemoryAdd(args: z.infer<typeof memoryAddInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = await apiFetch("/api/memory", {
      method: "POST",
      body: JSON.stringify({
        apiKeyId: args.apiKeyId,
        sessionId: args.sessionId ?? "",
        type: args.type,
        key: args.key,
        content: args.content,
        metadata: args.metadata ?? {},
      }),
    });
    await logToolCall("omniroute_memory_add", { ...args, content: "[redacted]" }, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_memory_add", { apiKeyId: args.apiKeyId, type: args.type }, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleMemoryClear(args: z.infer<typeof memoryClearInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const params = new URLSearchParams({ apiKeyId: args.apiKeyId });
    if (args.type) params.set("type", args.type);
    if (args.olderThan) params.set("olderThan", args.olderThan);

    const result = await apiFetch(`/api/memory?${params.toString()}`, { method: "DELETE" });
    await logToolCall("omniroute_memory_clear", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_memory_clear", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

// ── Skill Tools (HTTP-based — replaces OmniRoute internal @/lib/skills/* imports) ──

async function handleSkillsList(args: z.infer<typeof skillsListInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const params = new URLSearchParams();
    if (args.apiKeyId) params.set("apiKeyId", args.apiKeyId);
    if (args.name) params.set("name", args.name);
    if (args.enabled !== undefined) params.set("enabled", String(args.enabled));

    const result = await apiFetch(`/api/skills${params.toString() ? `?${params.toString()}` : ""}`);
    await logToolCall("omniroute_skills_list", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_skills_list", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSkillsEnable(args: z.infer<typeof skillsEnableInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = await apiFetch(`/api/skills/${encodeURIComponent(args.skillId)}`, {
      method: "PATCH",
      body: JSON.stringify({ enabled: args.enabled, apiKeyId: args.apiKeyId }),
    });
    await logToolCall("omniroute_skills_enable", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_skills_enable", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSkillsExecute(args: z.infer<typeof skillsExecuteInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const result = await apiFetch("/api/skills/execute", {
      method: "POST",
      body: JSON.stringify({
        apiKeyId: args.apiKeyId,
        skillName: args.skillName,
        input: args.input,
        sessionId: args.sessionId,
      }),
    });
    await logToolCall("omniroute_skills_execute", { apiKeyId: args.apiKeyId, skillName: args.skillName }, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_skills_execute", { apiKeyId: args.apiKeyId, skillName: args.skillName }, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

async function handleSkillsExecutions(args: z.infer<typeof skillsExecutionsInput>): Promise<TextToolResult> {
  const start = Date.now();
  try {
    const params = new URLSearchParams();
    if (args.apiKeyId) params.set("apiKeyId", args.apiKeyId);
    if (args.limit) params.set("limit", String(args.limit));

    const result = await apiFetch(`/api/skills/executions${params.toString() ? `?${params.toString()}` : ""}`);
    await logToolCall("omniroute_skills_executions", args, result, Date.now() - start, true);
    return { content: [{ type: "text" as const, text: JSON.stringify(result, null, 2) }] };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    await logToolCall("omniroute_skills_executions", args, null, Date.now() - start, false, msg);
    return { content: [{ type: "text" as const, text: `Error: ${msg}` }], isError: true };
  }
}

// ============ MCP Server Setup ============

const TOOL_COUNT = 27; // 8 essential + 11 advanced + 3 memory + 4 skills + web_search

export function createMcpServer(): McpServer {
  const server = new McpServer({ name: "omniroute", version: VERSION });

  // ── Essential Tools ──────────────────────────────────────────────────────────
  server.registerTool("omniroute_get_health",
    { description: "Returns OmniRoute health: uptime, memory, circuit breakers, rate limits, cache stats", inputSchema: getHealthInput },
    withScopeEnforcement("omniroute_get_health", async (args) => { getHealthInput.parse(args ?? {}); return handleGetHealth(); })
  );
  server.registerTool("omniroute_list_combos",
    { description: "Lists all configured combos (model chains) with strategies and optional metrics", inputSchema: listCombosInput },
    withScopeEnforcement("omniroute_list_combos", (args) => handleListCombos(listCombosInput.parse(args)))
  );
  server.registerTool("omniroute_get_combo_metrics",
    { description: "Returns detailed performance metrics for a specific combo", inputSchema: getComboMetricsInput },
    withScopeEnforcement("omniroute_get_combo_metrics", (args) => handleGetComboMetrics(getComboMetricsInput.parse(args)))
  );
  server.registerTool("omniroute_switch_combo",
    { description: "Activates or deactivates a combo for routing", inputSchema: switchComboInput },
    withScopeEnforcement("omniroute_switch_combo", (args) => handleSwitchCombo(switchComboInput.parse(args)))
  );
  server.registerTool("omniroute_check_quota",
    { description: "Checks remaining API quota for one or all providers", inputSchema: checkQuotaInput },
    withScopeEnforcement("omniroute_check_quota", (args) => handleCheckQuota(checkQuotaInput.parse(args)))
  );
  server.registerTool("omniroute_route_request",
    { description: "Sends a chat completion request through OmniRoute intelligent routing", inputSchema: routeRequestInput },
    withScopeEnforcement("omniroute_route_request", (args) => handleRouteRequest(routeRequestInput.parse(args)))
  );
  server.registerTool("omniroute_cost_report",
    { description: "Generates a cost report for the specified period (session/day/week/month)", inputSchema: costReportInput },
    withScopeEnforcement("omniroute_cost_report", (args) => handleCostReport(costReportInput.parse(args)))
  );
  server.registerTool("omniroute_list_models_catalog",
    { description: "Lists all available AI models across providers with capabilities and pricing", inputSchema: listModelsCatalogInput },
    withScopeEnforcement("omniroute_list_models_catalog", (args) => handleListModelsCatalog(listModelsCatalogInput.parse(args)))
  );
  server.registerTool("omniroute_web_search",
    { description: "Performs a web search via OmniRoute's search gateway (Serper, Brave, Perplexity, Exa, Tavily). Returns results with title, URL, snippet.", inputSchema: webSearchInput },
    withScopeEnforcement("omniroute_web_search", (args) => handleWebSearch(webSearchInput.parse(args)))
  );

  // ── Advanced Tools ───────────────────────────────────────────────────────────
  server.registerTool("omniroute_simulate_route",
    { description: "Dry-run routing simulation: shows path, probabilities, costs, and circuit breaker states without executing", inputSchema: simulateRouteInput },
    withScopeEnforcement("omniroute_simulate_route", (args) => handleSimulateRoute(simulateRouteInput.parse(args)))
  );
  server.registerTool("omniroute_set_budget_guard",
    { description: "Sets a session budget limit with configurable action when exceeded (degrade/block/alert)", inputSchema: setBudgetGuardInput },
    withScopeEnforcement("omniroute_set_budget_guard", (args) => handleSetBudgetGuard(setBudgetGuardInput.parse(args)))
  );
  server.registerTool("omniroute_set_routing_strategy",
    { description: "Updates combo routing strategy at runtime (priority/weighted/round-robin/auto/etc.)", inputSchema: setRoutingStrategyInput },
    withScopeEnforcement("omniroute_set_routing_strategy", (args) => handleSetRoutingStrategy(setRoutingStrategyInput.parse(args)))
  );
  server.registerTool("omniroute_set_resilience_profile",
    { description: "Applies a resilience profile controlling circuit breakers, retries, timeouts, and fallback depth", inputSchema: setResilienceProfileInput },
    withScopeEnforcement("omniroute_set_resilience_profile", (args) => handleSetResilienceProfile(setResilienceProfileInput.parse(args)))
  );
  server.registerTool("omniroute_test_combo",
    { description: "Live-tests each provider in a combo, reporting latency, cost, and success per provider", inputSchema: testComboInput },
    withScopeEnforcement("omniroute_test_combo", (args) => handleTestCombo(testComboInput.parse(args)))
  );
  server.registerTool("omniroute_get_provider_metrics",
    { description: "Detailed per-provider metrics: latency percentiles, success rate, quota, circuit breaker state", inputSchema: getProviderMetricsInput },
    withScopeEnforcement("omniroute_get_provider_metrics", (args) => handleGetProviderMetrics(getProviderMetricsInput.parse(args)))
  );
  server.registerTool("omniroute_best_combo_for_task",
    { description: "Recommends the best combo for a task type based on provider fitness, cost, and latency constraints", inputSchema: bestComboForTaskInput },
    withScopeEnforcement("omniroute_best_combo_for_task", (args) => handleBestComboForTask(bestComboForTaskInput.parse(args)))
  );
  server.registerTool("omniroute_explain_route",
    { description: "Explains why a request was routed to a specific provider, showing scoring factors and fallbacks", inputSchema: explainRouteInput },
    withScopeEnforcement("omniroute_explain_route", (args) => handleExplainRoute(explainRouteInput.parse(args)))
  );
  server.registerTool("omniroute_get_session_snapshot",
    { description: "Full snapshot of the current session: cost, tokens, top models, errors, budget status", inputSchema: getSessionSnapshotInput },
    withScopeEnforcement("omniroute_get_session_snapshot", async (args) => { getSessionSnapshotInput.parse(args ?? {}); return handleGetSessionSnapshot(); })
  );
  server.registerTool("omniroute_db_health_check",
    { description: "Diagnoses (or repairs) OmniRoute database drift, broken combo references, and orphan rows", inputSchema: dbHealthCheckInput },
    withScopeEnforcement("omniroute_db_health_check", (args) => handleDbHealthCheck(dbHealthCheckInput.parse(args ?? {})))
  );
  server.registerTool("omniroute_sync_pricing",
    { description: "Syncs pricing data from external sources (LiteLLM) without overwriting user-set prices", inputSchema: syncPricingInput },
    withScopeEnforcement("omniroute_sync_pricing", (args) => handleSyncPricing(syncPricingInput.parse(args)))
  );

  // ── Memory Tools ─────────────────────────────────────────────────────────────
  server.registerTool("omniroute_memory_search",
    { description: "Search memories by query, type, or API key with token budget enforcement", inputSchema: memorySearchInput },
    withScopeEnforcement("omniroute_memory_search", (args) => handleMemorySearch(memorySearchInput.parse(args)))
  );
  server.registerTool("omniroute_memory_add",
    { description: "Add a new memory entry (factual/episodic/procedural/semantic)", inputSchema: memoryAddInput },
    withScopeEnforcement("omniroute_memory_add", (args) => handleMemoryAdd(memoryAddInput.parse(args)))
  );
  server.registerTool("omniroute_memory_clear",
    { description: "Clear memories for an API key, optionally filtered by type or age", inputSchema: memoryClearInput },
    withScopeEnforcement("omniroute_memory_clear", (args) => handleMemoryClear(memoryClearInput.parse(args)))
  );

  // ── Skill Tools ──────────────────────────────────────────────────────────────
  server.registerTool("omniroute_skills_list",
    { description: "List all registered OmniRoute skills with optional filtering by API key or name", inputSchema: skillsListInput },
    withScopeEnforcement("omniroute_skills_list", (args) => handleSkillsList(skillsListInput.parse(args)))
  );
  server.registerTool("omniroute_skills_enable",
    { description: "Enable or disable a specific OmniRoute skill by ID", inputSchema: skillsEnableInput },
    withScopeEnforcement("omniroute_skills_enable", (args) => handleSkillsEnable(skillsEnableInput.parse(args)))
  );
  server.registerTool("omniroute_skills_execute",
    { description: "Execute an OmniRoute skill with provided input and return the result", inputSchema: skillsExecuteInput },
    withScopeEnforcement("omniroute_skills_execute", (args) => handleSkillsExecute(skillsExecuteInput.parse(args)))
  );
  server.registerTool("omniroute_skills_executions",
    { description: "List recent OmniRoute skill execution history", inputSchema: skillsExecutionsInput },
    withScopeEnforcement("omniroute_skills_executions", (args) => handleSkillsExecutions(skillsExecutionsInput.parse(args)))
  );

  return server;
}

// ============ Main Entry Point ============

export async function startMcpStdio(): Promise<void> {
  const server = createMcpServer();
  const transport = new StdioServerTransport();
  const stopHeartbeat = startMcpHeartbeat({
    version: VERSION,
    scopesEnforced: MCP_ENFORCE_SCOPES,
    allowedScopes: Array.from(MCP_ALLOWED_SCOPES),
    toolCount: TOOL_COUNT,
  });

  const cleanup = () => { stopHeartbeat(); };
  process.once("exit",    cleanup);
  process.once("SIGINT",  cleanup);
  process.once("SIGTERM", cleanup);

  console.error(`[MCP] OmniRoute MCP Server v${VERSION} starting (stdio)…`);
  try {
    await server.connect(transport);
    console.error("[MCP] OmniRoute MCP Server connected and ready.");
  } finally {
    cleanup();
    process.off("exit",    cleanup);
    process.off("SIGINT",  cleanup);
    process.off("SIGTERM", cleanup);
  }
}

// Run directly if invoked as a script
if (process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/\\/g, "/"))) {
  startMcpStdio().catch((err) => {
    console.error("[MCP] Fatal error:", err);
    process.exit(1);
  });
}
