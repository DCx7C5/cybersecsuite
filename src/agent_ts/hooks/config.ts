import { sendEvent } from "../ipc";

export async function onConfigChange(payload: unknown): Promise<void> {
  sendEvent("ConfigChange", { payload });
}

export async function onWorktreeCreate(payload: unknown): Promise<void> {
  sendEvent("WorktreeCreate", { payload });
}

export async function onWorktreeRemove(payload: unknown): Promise<void> {
  sendEvent("WorktreeRemove", { payload });
}
