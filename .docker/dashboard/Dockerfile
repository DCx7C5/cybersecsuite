# ── Base image ────────────────────────────────────────────────────────────────
FROM python:3.14-slim

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
COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# ── Application code ──────────────────────────────────────────────────────────
COPY . .

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
