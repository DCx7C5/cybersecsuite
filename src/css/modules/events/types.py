"""Event type constants for Phase 3 and beyond."""

# Phase 3 events
EVENT_TYPES_PHASE3 = {
    "module.loaded": "Module initialization",
    "module.error": "Module error",
    "provider.initialized": "Provider initialized",
    "provider.error": "Provider error",
}

# Phase 5 — Cross-module integration events (active)
EVENT_TYPES_PHASE5 = {
    "tool.call.start": "Tool call started",
    "tool.call.complete": "Tool call completed",
    "tool.call.error": "Tool call error",
    "permission.denied": "Permission denied on tool access",
    "marketplace.install": "Marketplace item installed",
    "marketplace.uninstall": "Marketplace item uninstalled",
    "marketplace.updated": "Marketplace item updated",
    "marketplace.cache.invalidated": "Marketplace cache invalidated",
}

# Phase 6+ events (planned)
EVENT_TYPES_PHASE6 = {
    "team.spawned": "Team spawned",
    "team.shutdown": "Team shutdown",
    "team.crashed": "Team crashed",
    "task.delegated": "Task delegated",
    "task.completed": "Task completed",
    "task.failed": "Task failed",
    "task.reassigned": "Task reassigned",
    "agent.action": "Agent action",
    "agent.error": "Agent error",
    "permission.granted": "Permission granted",
    "permission.revoked": "Permission revoked",
    "llm.call.start": "LLM call started",
    "llm.call.complete": "LLM call completed",
    "llm.call.error": "LLM call error",
    "llm.cache.hit": "LLM cache hit",
}

# Phase 14 events (planned)
EVENT_TYPES_PHASE14 = {
    "http.request.started": "HTTP request started",
    "http.request.completed": "HTTP request completed",
    "http.request.failed": "HTTP request failed",
    "command.dispatched": "Command dispatched",
    "command.handled": "Command handled",
    "command.failed": "Command failed",
    "agent.run.started": "Agent run started",
    "agent.run.completed": "Agent run completed",
    "agent.run.failed": "Agent run failed",
}

# Combined for reference
ALL_EVENT_TYPES = {
    **EVENT_TYPES_PHASE3,
    **EVENT_TYPES_PHASE5,
    **EVENT_TYPES_PHASE6,
    **EVENT_TYPES_PHASE14,
}
