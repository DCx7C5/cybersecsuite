# cybersecsuite — dashboard service (uv-based)
FROM python:3.14-slim AS base

# Install uv + curl (healthcheck) + libpq5 (asyncpg runtime)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
RUN apt-get update -qq \
    && apt-get install -y --no-install-recommends curl libpq5 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first for caching
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev --no-install-project

# Copy source
COPY src/ src/
COPY mcp_server.py .
COPY templates/ templates/
COPY data/fixtures/ data/fixtures/

# Install the project itself
RUN uv sync --frozen --no-dev

# Runtime
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV TERM=xterm-256color
ENV ASGI_HOST=0.0.0.0
ENV ASGI_PORT=8000
ENV ASGI_TLS_PORT=8433

EXPOSE 8000 8080 8433

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -fs http://localhost:8000/health || exit 1

STOPSIGNAL SIGTERM

CMD ["uv", "run", "uvicorn", "proxy.asgi:app", "--host", "0.0.0.0", "--port", "8000"]


ARG BUILD_DATE
ARG VCS_REF
ARG VERSION
ARG USER

# ── Metadata ──────────────────────────────────────────────────────────────────
LABEL maintainer="cybersec" \
      description="CyberSec Dashboard – live forensic web dashboard" \
      version="4.0.0"

# ── Environment ───────────────────────────────────────────────────────────────
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TERM=xterm-256color \
    COLORTERM=truecolor \
    CYBERSEC_DB_HOST=/var/run/postgresql \
    CYBERSEC_DB_USER=cybersec \
    CYBERSEC_DB_PASSWORD=cybersec_default \
    CYBERSEC_DB_NAME=cybersec_forensics

WORKDIR /app

# ── System deps ───────────────────────────────────────────────────────────────
# libpq5  – runtime shared-library required by psycopg & asyncpg
# curl    – used by the healthcheck
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libpq5 \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps (layer-cached as long as requirements.txt is unchanged) ───────
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
RUN uv pip install --no-cache-dir -r requirements.txt


# ── Application code ──────────────────────────────────────────────────────────
COPY --chmod=700 --chown="${USER}:${USER}" entrypoint.sh /entrypoint.sh

# ── Entrypoint script (must be installed as root, before USER switch) ─────────
COPY --chmod=755 .docker/dashboard/entrypoint.sh /usr/local/bin/entrypoint.sh

# ── Non-root user (security hardening) ───────────────────────────────────────
RUN useradd --no-create-home --shell /bin/false cybersec \
    && chown -R cybersec:cybersec /app
USER cybersec

# ── Networking ────────────────────────────────────────────────────────────────
EXPOSE 8322

# ── Healthcheck ───────────────────────────────────────────────────────────────
HEALTHCHECK --interval=15s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -fs http://localhost:8322/ > /dev/null || exit 1

# ── Signal handling ───────────────────────────────────────────────────────────
STOPSIGNAL SIGTERM

# ── Entrypoint ────────────────────────────────────────────────────────────────
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
