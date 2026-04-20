import { sendEvent } from "../ipc";

export async function onSetup(payload: unknown): Promise<void> {
  sendEvent("GenericSetup", { payload });
}
