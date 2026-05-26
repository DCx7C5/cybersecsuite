# CyberSecSuite Frontend

React + TypeScript + Vite frontend for CyberSecSuite.

## Run locally

1. Start backend on port `8000`:
   ```bash
   cd /home/daen/Projects/cybersecsuite
   .venv/bin/python manage.py serve --port 8000
   ```
2. Start the Vite frontend:
   ```bash
   cd /home/daen/Projects/cybersecsuite/src/frontend
   bun run dev
   ```

Frontend URL: `http://127.0.0.1:5173`

## API wiring

- Vite proxy routes `/api`, `/marketplace`, and `/ws` to backend `http://127.0.0.1:8000`.
- API client also supports `VITE_API_BASE_URL` if direct backend URL mode is preferred.

## Useful commands

```bash
bun run check
bun run build
```
