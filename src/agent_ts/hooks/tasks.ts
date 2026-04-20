import { sendEvent } from "../ipc";

export async function onTaskCompleted(payload: unknown): Promise<void> {
  sendEvent("TaskCompleted", { payload });
}
