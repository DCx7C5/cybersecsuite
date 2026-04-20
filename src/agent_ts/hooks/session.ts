import { sendEvent } from "../ipc";

export async function onSessionStart(payload: unknown): Promise<void> {
  sendEvent("SessionStart", { payload, ts: Date.now() });
}

export async function onSessionEnd(payload: unknown): Promise<void> {
  sendEvent("SessionEnd", { payload, ts: Date.now() });
}
