# cybersecsuite — multi-stage build with uv
FROM python:3.14-slim AS base

# Install uv + curl (for healthcheck)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update -qq && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY mcp_server.py .
COPY templates/ templates/

# Install the project itself
RUN uv sync --frozen --no-dev

# Runtime
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV ASGI_HOST=127.0.0.1
ENV ASGI_PORT=8000
ENV ASGI_TLS_PORT=8433

EXPOSE 8000 8080 8433

# Default: run the ASGI server (AI proxy + A2A + health)
CMD ["uv", "run", "uvicorn", "proxy.asgi:app", "--host", "0.0.0.0", "--port", "8000"]

