FROM oven/bun:1

WORKDIR /app

# Source is mounted at runtime (./src/frontend:/app) — install deps on start
EXPOSE 5173

CMD ["sh", "-c", "bun install && bun run dev --host"]
