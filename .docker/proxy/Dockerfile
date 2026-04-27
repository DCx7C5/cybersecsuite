# cybersecsuite — proxy service (uv-based)
FROM python:3.14-slim AS base

ARG BUILD_DATE
ARG VCS_REF
ARG VERSION

LABEL maintainer="cybersec" \
      description="CyberSec Proxy — ASGI server + live forensic dashboard" \
      version="4.0.0"

# Install uv + curl (healthcheck) + libpq5 (asyncpg runtime)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends curl libpq5 git \
    && rm -rf /var/libs/apt/lists/*

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY mcp.json ./

# Install the project itself
RUN uv sync --frozen --no-dev

# Entrypoint (init DB + start uvicorn)
COPY --chmod=755 .docker/dashboard/entrypoint.sh /usr/local/bin/entrypoint.sh

# Non-root user
RUN useradd --no-create-home --shell /bin/false cybersec \
    && mkdir -p /home/cybersec/.cache/uv \
    && chown -R cybersec:cybersec /app /home/cybersec
USER cybersec

# Runtime environment
ENV PYTHONPATH=/app/src \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TERM=xterm-256color \
    ASGI_HOST=0.0.0.0 \
    ASGI_PORT=8000 \
    ASGI_TLS_PORT=8433

EXPOSE 8000 8080 8433

HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

STOPSIGNAL SIGTERM

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
