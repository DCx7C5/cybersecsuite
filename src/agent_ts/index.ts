/**
 * TypeScript companion — registers TS-only Claude Code hooks and hosts IPC.
 *
 * The @anthropic-ai/claude-code package surface evolves; we probe common exports
 * and fall back to IPC-only mode if registration is unavailable.
 */
import { createRequire } from "module";
import { startIpcServer, stopIpcServer } from "./ipc";
import { onCssFirstSetup } from "./hooks/css_first_setup";
import { onSetup } from "./hooks/setup";
import { onSessionEnd, onSessionStart } from "./hooks/session";
import { onTeammateIdle } from "./hooks/team";
import { onTaskCompleted } from "./hooks/tasks";
import { onConfigChange, onWorktreeCreate, onWorktreeRemove } from "./hooks/config";

const require = createRequire(__filename);

function tryRegisterClaudeCodeHooks(): void {
  let mod: Record<string, unknown>;
  try {
    mod = require("@anthropic-ai/claude-code") as Record<string, unknown>;
  } catch (e) {
    console.warn("[agent_ts] @anthropic-ai/claude-code not installed:", String(e));
    return;
  }

  const candidates = [
    "registerHooks",
    "registerClaudeCodeHooks",
    "createClaudeCode",
    "ClaudeCode",
    "default",
  ] as const;

  for (const key of candidates) {
    const fn = mod[key as string];
    if (typeof fn === "function") {
      console.log(`[agent_ts] Found export ${key} — attempting hook registration (best-effort)`);
      try {
        (fn as (hooks: Record<string, unknown>) => void)({
          Setup: onSetup,
          SessionStart: onSessionStart,
          SessionEnd: onSessionEnd,
          TeammateIdle: onTeammateIdle,
          TaskCompleted: onTaskCompleted,
          ConfigChange: onConfigChange,
          WorktreeCreate: onWorktreeCreate,
          WorktreeRemove: onWorktreeRemove,
          // Non-standard: guarded first-run installer
          CcsFirstSetup: onCssFirstSetup,
        });
      } catch (err) {
        console.warn("[agent_ts] Hook registration failed:", String(err));
      }
      return;
    }
  }

  console.warn("[agent_ts] No known hook registration entrypoint found in @anthropic-ai/claude-code");
}

async function shutdown(): Promise<void> {
  await stopIpcServer();
  process.exit(0);
}

async function main(): Promise<void> {
  startIpcServer();
  tryRegisterClaudeCodeHooks();
  process.stdin.resume();
  process.on("SIGTERM", () => void shutdown());
  process.on("SIGINT", () => void shutdown());
}

void main();
