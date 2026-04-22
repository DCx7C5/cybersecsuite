import { spawn } from "child_process";
import * as fs from "fs";
import * as path from "path";
import { repoRootFromHere, sendEvent } from "../ipc";

/**
 * Setup hook — runs `make ccs-first-setup` once per machine/repo (sentinel).
 */
export async function onCcsFirstSetup(payload: unknown): Promise<void> {
  const root = repoRootFromHere();
  const sentinel = path.join(root, ".css-initialized");
  if (fs.existsSync(sentinel)) {
    sendEvent("SetupSkipped", { reason: "sentinel_exists", sentinel });
    return;
  }
  sendEvent("SetupStart", { root, payload });
  await new Promise<void>((resolve) => {
    const child = spawn("make", ["ccs-first-setup"], {
      cwd: root,
      stdio: "inherit",
      shell: false,
    });
    child.on("close", (code) => {
      sendEvent("SetupDone", { code });
      resolve();
    });
    child.on("error", (err) => {
      sendEvent("SetupError", { error: String(err) });
      resolve();
    });
  });
}
