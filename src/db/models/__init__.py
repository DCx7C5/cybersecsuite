"""csdb-mcp initial model registry — scope + core only."""

MODEL_MODULES: list[str] = [
    "skills.csdb.db.models.scope",
    "skills.csdb.db.models.core",
]

# Tables created: workspaces, projects, sessions, shared_entries, audit_logs

