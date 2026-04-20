/**
 * Unix socket IPC — receives JSON lines from hooks and keeps a server alive.
 * Socket path: /tmp/cybersecsuite-hooks.sock
 */
import * as fs from "fs";
import * as net from "net";
import * as path from "path";

const SOCKET_PATH = "/tmp/cybersecsuite-hooks.sock";

let server: net.Server | null = null;

function logLine(msg: string, data?: unknown): void {
  const suffix = data === undefined ? "" : ` ${JSON.stringify(data)}`;
  console.log(`[ipc] ${msg}${suffix}`);
}

export function startIpcServer(): void {
  if (server) {
    return;
  }
  try {
    if (fs.existsSync(SOCKET_PATH)) {
      fs.unlinkSync(SOCKET_PATH);
    }
  } catch {
    // ignore unlink errors
  }

  server = net.createServer((socket) => {
    socket.setEncoding("utf8");
    let buffer = "";
    socket.on("data", (chunk: string) => {
      buffer += chunk;
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";
      for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) {
          continue;
        }
        try {
          const parsed = JSON.parse(trimmed) as unknown;
          logLine("message", parsed);
        } catch {
          logLine("non-json", trimmed);
        }
      }
    });
    socket.on("error", (err) => logLine("socket error", String(err)));
  });

  server.listen(SOCKET_PATH, () => {
    logLine("listening", SOCKET_PATH);
  });

  server.on("error", (err) => {
    logLine("server error", String(err));
  });
}

export function stopIpcServer(): Promise<void> {
  return new Promise((resolve) => {
    if (!server) {
      resolve();
      return;
    }
    server.close(() => {
      server = null;
      try {
        if (fs.existsSync(SOCKET_PATH)) {
          fs.unlinkSync(SOCKET_PATH);
        }
      } catch {
        // ignore
      }
      resolve();
    });
  });
}

/**
 * Fire-and-forget client: connects, writes one JSON event + newline, ends.
 */
export function sendEvent(event: string, payload: object): void {
  const client = net.createConnection(SOCKET_PATH, () => {
    const body = JSON.stringify({ event, payload, ts: new Date().toISOString() });
    client.write(`${body}\n`, () => client.end());
  });
  client.on("error", (err) => {
    logLine("sendEvent failed", { event, error: String(err) });
  });
}

export function repoRootFromHere(): string {
  // __dirname is .../src/agent_ts when compiled via CommonJS
  return path.resolve(__dirname, "..", "..", "..");
}
