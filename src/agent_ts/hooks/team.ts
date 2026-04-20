import { sendEvent } from "../ipc";

export async function onTeammateIdle(payload: unknown): Promise<void> {
  sendEvent("TeammateIdle", { payload });
}
