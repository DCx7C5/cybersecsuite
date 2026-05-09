# CyberSecSuite Frontend

React + TypeScript + Vite frontend for CyberSecSuite.

## Run locally

1. Start backend on port `8001`:
   ```bash
   cd /home/daen/Projects/cybersecsuite
   .venv/bin/uvicorn css.core.asgi.app:app --host 0.0.0.0 --port 8001
   ```
2. Start frontend on port `8000`:
   ```bash
   cd /home/daen/Projects/cybersecsuite/src/frontend
   bun run dev --host 0.0.0.0 --port 8000
   ```

Frontend URL: `http://127.0.0.1:8000`

## API wiring

- Vite proxy routes `/api`, `/marketplace`, and `/ws` to backend `http://127.0.0.1:8001`.
- API client also supports `VITE_API_BASE_URL` if direct backend URL mode is preferred.

## Useful commands

```bash
bun run check
bun run build
```
