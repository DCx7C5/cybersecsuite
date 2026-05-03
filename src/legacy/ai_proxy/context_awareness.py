"""
Worker Context Awareness — Enhanced awareness of architecture, scope, patterns, and APIs.

Extends WorkerContext with:
- Architecture awareness (layer, component, module)
- Scope awareness (session, project, investigation)
- Pattern awareness (recently used patterns, tools, functions)
- API awareness (recently called endpoints, parameters, response types)

Enables:
- Context-aware task routing and deduplication
- Intelligent task sequencing based on accessed patterns
- Cache locality optimization
- Reduced context switching overhead
"""


import logging
from datetime import datetime
from typing import Any, Optional


from db.models.worker_context import WorkerContext

logger = logging.getLogger("worker_context_awareness")


class ArchitectureContext:
    """Worker's awareness of system architecture."""

    def __init__(self):
        self.current_layer: Optional[str] = None  # Layer 0-6 from architecture
        self.current_component: Optional[str] = None  # e.g., "ai_proxy", "google_a2a", "mcp"
        self.current_module: Optional[str] = None  # e.g., "routing", "providers", "health"
        self.accessed_layers: list[str] = []  # Layers visited this session
        self.accessed_components: list[str] = []  # Components visited this session

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "current_layer": self.current_layer,
            "current_component": self.current_component,
            "current_module": self.current_module,
            "accessed_layers": self.accessed_layers[-10:],  # Keep last 10
            "accessed_components": self.accessed_components[-10:],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArchitectureContext:
        """Restore from dict."""
        ctx = cls()
        ctx.current_layer = data.get("current_layer")
        ctx.current_component = data.get("current_component")
        ctx.current_module = data.get("current_module")
        ctx.accessed_layers = data.get("accessed_layers", [])
        ctx.accessed_components = data.get("accessed_components", [])
        return ctx


class ScopeContext:
    """Worker's awareness of execution scope."""

    def __init__(self):
        self.session_id: Optional[int] = None
        self.project_id: Optional[int] = None
        self.investigation_id: Optional[int] = None
        self.scope_level: str = "session"  # session, project, investigation
        self.scope_breadcrumbs: list[str] = []  # Trail of accessed scopes

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "session_id": self.session_id,
            "project_id": self.project_id,
            "investigation_id": self.investigation_id,
            "scope_level": self.scope_level,
            "scope_breadcrumbs": self.scope_breadcrumbs[-10:],  # Keep last 10
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ScopeContext:
        """Restore from dict."""
        ctx = cls()
        ctx.session_id = data.get("session_id")
        ctx.project_id = data.get("project_id")
        ctx.investigation_id = data.get("investigation_id")
        ctx.scope_level = data.get("scope_level", "session")
        ctx.scope_breadcrumbs = data.get("scope_breadcrumbs", [])
        return ctx


class PatternContext:
    """Worker's awareness of patterns and operations."""

    def __init__(self):
        self.recent_patterns: list[str] = []  # Recently accessed patterns
        self.pattern_count: dict[str, int] = {}  # Pattern frequency
        self.recent_functions: list[str] = []  # Recently called functions
        self.function_count: dict[str, int] = {}  # Function call frequency

    def add_pattern(self, pattern: str) -> None:
        """Record pattern access."""
        # Keep in recent list (last 20)
        if pattern in self.recent_patterns:
            self.recent_patterns.remove(pattern)
        self.recent_patterns.append(pattern)
        if len(self.recent_patterns) > 20:
            self.recent_patterns.pop(0)

        # Track frequency
        self.pattern_count[pattern] = self.pattern_count.get(pattern, 0) + 1

    def add_function_call(self, function_name: str) -> None:
        """Record function call."""
        # Keep in recent list (last 20)
        if function_name in self.recent_functions:
            self.recent_functions.remove(function_name)
        self.recent_functions.append(function_name)
        if len(self.recent_functions) > 20:
            self.recent_functions.pop(0)

        # Track frequency
        self.function_count[function_name] = self.function_count.get(function_name, 0) + 1

    def get_hot_patterns(self, limit: int = 5) -> list[str]:
        """Get most frequently accessed patterns."""
        sorted_patterns = sorted(
            self.pattern_count.items(), key=lambda x: x[1], reverse=True
        )
        return [p[0] for p in sorted_patterns[:limit]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "recent_patterns": self.recent_patterns,
            "pattern_count": self.pattern_count,
            "recent_functions": self.recent_functions,
            "function_count": self.function_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PatternContext:
        """Restore from dict."""
        ctx = cls()
        ctx.recent_patterns = data.get("recent_patterns", [])
        ctx.pattern_count = data.get("pattern_count", {})
        ctx.recent_functions = data.get("recent_functions", [])
        ctx.function_count = data.get("function_count", {})
        return ctx


class APIContext:
    """Worker's awareness of API endpoints and usage."""

    def __init__(self):
        self.recent_endpoints: list[str] = []  # Recently called endpoints
        self.endpoint_count: dict[str, int] = {}  # Endpoint call frequency
        self.endpoint_latencies: dict[str, list[float]] = {}  # Response times per endpoint
        self.recent_errors: list[dict[str, Any]] = []  # Recent API errors

    def record_endpoint_call(
        self,
        endpoint: str,
        latency_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Record API endpoint call."""
        # Track recent endpoints
        if endpoint in self.recent_endpoints:
            self.recent_endpoints.remove(endpoint)
        self.recent_endpoints.append(endpoint)
        if len(self.recent_endpoints) > 20:
            self.recent_endpoints.pop(0)

        # Track frequency
        self.endpoint_count[endpoint] = self.endpoint_count.get(endpoint, 0) + 1

        # Track latency
        if endpoint not in self.endpoint_latencies:
            self.endpoint_latencies[endpoint] = []
        self.endpoint_latencies[endpoint].append(latency_ms)
        # Keep last 100 measurements
        if len(self.endpoint_latencies[endpoint]) > 100:
            self.endpoint_latencies[endpoint].pop(0)

        # Track errors
        if error:
            self.recent_errors.append(
                {
                    "endpoint": endpoint,
                    "error": error,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )
            # Keep last 20 errors
            if len(self.recent_errors) > 20:
                self.recent_errors.pop(0)

    def get_avg_latency(self, endpoint: str) -> float:
        """Get average latency for endpoint."""
        latencies = self.endpoint_latencies.get(endpoint, [])
        return sum(latencies) / len(latencies) if latencies else 0.0

    def get_p95_latency(self, endpoint: str) -> float:
        """Get 95th percentile latency for endpoint."""
        latencies = self.endpoint_latencies.get(endpoint, [])
        if not latencies:
            return 0.0
        sorted_latencies = sorted(latencies)
        idx = int(len(sorted_latencies) * 0.95)
        return sorted_latencies[min(idx, len(sorted_latencies) - 1)]

    def get_hot_endpoints(self, limit: int = 5) -> list[str]:
        """Get most frequently called endpoints."""
        sorted_endpoints = sorted(
            self.endpoint_count.items(), key=lambda x: x[1], reverse=True
        )
        return [e[0] for e in sorted_endpoints[:limit]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "recent_endpoints": self.recent_endpoints,
            "endpoint_count": self.endpoint_count,
            "recent_errors": self.recent_errors,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> APIContext:
        """Restore from dict."""
        ctx = cls()
        ctx.recent_endpoints = data.get("recent_endpoints", [])
        ctx.endpoint_count = data.get("endpoint_count", {})
        ctx.recent_errors = data.get("recent_errors", [])
        return ctx


class WorkerContextAwareness:
    """
    Composite awareness context for workers.

    Tracks architecture, scope, patterns, and APIs to enable intelligent
    task routing, deduplication, and context-aware optimization.
    """

    def __init__(self, worker_id: str, session_id: int):
        self.worker_id = worker_id
        self.session_id = session_id
        self.architecture = ArchitectureContext()
        self.scope = ScopeContext()
        self.pattern = PatternContext()
        self.api = APIContext()
        self.created_at = datetime.utcnow()
        self.last_updated_at = datetime.utcnow()

    async def save_to_db(self) -> None:
        """Persist awareness context to WorkerContext in database."""
        try:
            from db.models.llm_session import Session

            session = await Session.get_or_none(id=self.session_id)
            if not session:
                logger.warning(f"Session {self.session_id} not found")
                return

            worker_context = await WorkerContext.get_or_none(
                session=session, worker_id=self.worker_id
            )
            if not worker_context:
                logger.warning(
                    f"WorkerContext not found for {self.worker_id} in session {self.session_id}"
                )
                return

            # Store in context_metadata
            worker_context.context_metadata = {
                "architecture": self.architecture.to_dict(),
                "scope": self.scope.to_dict(),
                "pattern": self.pattern.to_dict(),
                "api": self.api.to_dict(),
                "last_updated": datetime.utcnow().isoformat(),
            }

            await worker_context.save()

        except Exception as e:
            logger.error(f"Failed to save worker context awareness: {e}")

    @classmethod
    async def load_from_db(cls, worker_id: str, session_id: int) -> WorkerContextAwareness:
        """Load awareness context from database."""
        awareness = cls(worker_id, session_id)

        try:
            from db.models.llm_session import Session

            session = await Session.get_or_none(id=session_id)
            if not session:
                return awareness

            worker_context = await WorkerContext.get_or_none(
                session=session, worker_id=worker_id
            )
            if not worker_context or not worker_context.context_metadata:
                return awareness

            metadata = worker_context.context_metadata

            # Restore contexts
            if "architecture" in metadata:
                awareness.architecture = ArchitectureContext.from_dict(
                    metadata["architecture"]
                )
            if "scope" in metadata:
                awareness.scope = ScopeContext.from_dict(metadata["scope"])
            if "pattern" in metadata:
                awareness.pattern = PatternContext.from_dict(metadata["pattern"])
            if "api" in metadata:
                awareness.api = APIContext.from_dict(metadata["api"])

        except Exception as e:
            logger.error(f"Failed to load worker context awareness: {e}")

        return awareness

    def get_context_summary(self) -> dict[str, Any]:
        """Get summary of current awareness context."""
        return {
            "worker_id": self.worker_id,
            "session_id": self.session_id,
            "architecture": {
                "current_layer": self.architecture.current_layer,
                "current_component": self.architecture.current_component,
                "recent_components": self.architecture.accessed_components[-3:],
            },
            "scope": {
                "scope_level": self.scope.scope_level,
                "session_id": self.scope.session_id,
                "project_id": self.scope.project_id,
            },
            "hot_patterns": self.pattern.get_hot_patterns(3),
            "hot_endpoints": self.api.get_hot_endpoints(3),
            "recent_errors": len(self.api.recent_errors),
        }
