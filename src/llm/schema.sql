-- LLM Sessions — one row per worktree lifecycle
-- Applied once: psql $CYBERSEC_DB_DSN -f src/llm/schema.sql

CREATE TABLE IF NOT EXISTS llm_sessions (
    sid                  CHAR(12)         PRIMARY KEY,
    repo_root            TEXT             NOT NULL DEFAULT '',
    branch               TEXT             NOT NULL DEFAULT '',
    opened_at            TIMESTAMPTZ      NOT NULL,
    closed_at            TIMESTAMPTZ,
    total_input_tokens   BIGINT           NOT NULL DEFAULT 0,
    total_output_tokens  BIGINT           NOT NULL DEFAULT 0,
    total_cost_usd       NUMERIC(14, 8)   NOT NULL DEFAULT 0,
    total_calls          INTEGER          NOT NULL DEFAULT 0
);

-- LLM Calls — one row per Anthropic API request, bound to a session
CREATE TABLE IF NOT EXISTS llm_calls (
    id                   BIGSERIAL        PRIMARY KEY,
    sid                  CHAR(12)         NOT NULL REFERENCES llm_sessions(sid) ON DELETE CASCADE,
    model                VARCHAR(128)     NOT NULL,
    input_tokens         INTEGER          NOT NULL DEFAULT 0,
    output_tokens        INTEGER          NOT NULL DEFAULT 0,
    cache_read_tokens    INTEGER          NOT NULL DEFAULT 0,
    cache_write_tokens   INTEGER          NOT NULL DEFAULT 0,
    cost_usd             NUMERIC(14, 8)   NOT NULL DEFAULT 0,
    latency_ms           DOUBLE PRECISION NOT NULL DEFAULT 0,
    stream               BOOLEAN          NOT NULL DEFAULT TRUE,
    success              BOOLEAN          NOT NULL DEFAULT TRUE,
    error                TEXT,
    request_id           VARCHAR(64),
    called_at            TIMESTAMPTZ      NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS llm_calls_sid_called_at   ON llm_calls (sid, called_at DESC);
CREATE INDEX IF NOT EXISTS llm_calls_model_called_at ON llm_calls (model, called_at DESC);
CREATE INDEX IF NOT EXISTS llm_sessions_opened_at    ON llm_sessions (opened_at DESC);

-- Materialized view for fast per-model cost aggregation (refresh on teardown)
CREATE MATERIALIZED VIEW IF NOT EXISTS llm_cost_by_model AS
SELECT
    sid,
    model,
    COUNT(*)           AS calls,
    SUM(input_tokens)  AS total_input,
    SUM(output_tokens) AS total_output,
    SUM(cost_usd)      AS total_cost
FROM llm_calls
GROUP BY sid, model;

CREATE UNIQUE INDEX IF NOT EXISTS llm_cost_by_model_idx ON llm_cost_by_model (sid, model);
