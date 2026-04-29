"""
FastAPI scope middleware for request-level scope context injection.

Provides:
- Automatic scope context extraction from request headers/path
- Scope permission enforcement with < 5ms overhead
- Request/response context management
- Audit logging integration
- Error handling with proper HTTP status codes
"""


import logging
import time
from typing import Any, Awaitable, Callable, Optional
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from asgi.middleware import should_skip_path
from db.scope_utils import ScopeLevel, check_scope_permission
from db.exceptions import (
    ScopeError,
    ScopePermissionError,
    ScopeValidationError,
)
from db.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)


class RequestScopeContext:
    """Request-scoped context holder for scope information and request tracking.
    
    Tracks request-specific metadata including request ID, timing, and scope information.
    Separate from db.scope_utils.ScopeContext which handles scope hierarchy management.
    """
    
    def __init__(
        self,
        request_id: str,
        scope_level: str,
        user_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        project_id: Optional[int] = None,
        session_id: Optional[str] = None,
        runtime_id: Optional[str] = None,
    ) -> None:
        """Initialize request scope context.
        
        Args:
            request_id: Unique request identifier
            scope_level: Scope level from request
            user_id: User making the request
            resource_id: Resource being accessed
            project_id: Project identifier
            session_id: Session identifier
            runtime_id: Runtime identifier
        """
        self.request_id = request_id
        self.scope_level = scope_level
        self.user_id = user_id
        self.resource_id = resource_id
        self.project_id = project_id
        self.session_id = session_id
        self.runtime_id = runtime_id
        self.start_time = time.time()
    
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds.
        
        Returns:
            Elapsed time in milliseconds
        """
        return (time.time() - self.start_time) * 1000
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging.
        
        Returns:
            Dictionary representation
        """
        return {
            "request_id": self.request_id,
            "scope_level": self.scope_level,
            "user_id": self.user_id,
            "resource_id": self.resource_id,
            "project_id": self.project_id,
            "session_id": self.session_id,
            "runtime_id": self.runtime_id,
            "elapsed_ms": self.elapsed_ms(),
        }


# Backward compatibility alias - local RequestScopeContext has same interface as db.scope_utils.ScopeContext
ScopeContext = RequestScopeContext


class ScopeMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for scope context injection and enforcement.
    
    Features:
    - Extracts scope context from request headers and path
    - Validates scope context consistency
    - Enforces scope permissions with < 5ms overhead
    - Integrates with audit logging
    - Proper error handling with scoped status codes
    """
    
    def __init__(
        self,
        app: ASGIApp,
        skip_paths: Optional[list[str]] = None,
        permission_check_enabled: bool = True,
        audit_enabled: bool = True,
    ) -> None:
        """Initialize scope middleware.
        
        Args:
            app: ASGI application
            skip_paths: Paths to skip scope enforcement (e.g., ['/health', '/legacy_docs'])
            permission_check_enabled: Enable permission checks
            audit_enabled: Enable audit logging
        """
        super().__init__(app)
        self.skip_paths = skip_paths or [
            "/health",
            "/legacy_docs",
            "/openapi.json",
            "/redoc",
            "/.well-known",
        ]
        self.permission_check_enabled = permission_check_enabled
        self.audit_enabled = audit_enabled
    
    async def dispatch(self, request: Request, call_next: Callable[..., Awaitable[Response]]) -> Response:
        """Process request with scope middleware.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware/handler
            
        Returns:
            Response (with scope context or error)
        """
        # Skip scope enforcement for certain paths
        if should_skip_path(request.url.path, self.skip_paths):
            return await call_next(request)
        
        # Create request scope context
        request_id = str(uuid4())
        start_time = time.time()
        
        try:
            # Extract scope context from request
            scope_ctx = await self._extract_scope_context(request, request_id)
            
            # Note: scope context validation is done during extraction.
            # _validate_scope_context is available for direct testing but not called here
            # because path_params may not be available in middleware before route matching.
            
            # Perform permission check if enabled
            if self.permission_check_enabled:
                await self._check_permissions(scope_ctx, request)
            
            # Attach scope context to request
            request.state.scope_context = scope_ctx
            request.state.scope_middleware_elapsed = time.time() - start_time
            
            # Log scope access
            if self.audit_enabled:
                await self._audit_access(scope_ctx, request, "granted")
            
        except ScopePermissionError as e:
            if self.audit_enabled:
                await self._audit_permission_error(e, request_id)
            
            return self._error_response(e, 403)
        
        except ScopeValidationError as e:
            return self._error_response(e, 422)
        
        except ScopeError as e:
            return self._error_response(e, 500)
        
        except Exception as e:
            logger.error(f"Unexpected error in scope middleware: {e}", exc_info=True)
            return self._error_response(
                ScopeError(f"Internal server error: {str(e)}"),
                500
            )
        
        # Call next middleware/handler
        response = await call_next(request)
        
        # Add scope headers to response
        elapsed_ms = (time.time() - start_time) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Scope-Level"] = scope_ctx.scope_level
        response.headers["X-Scope-Elapsed-Ms"] = f"{elapsed_ms:.2f}"
        
        return response
    
    async def _extract_scope_context(
        self,
        request: Request,
        request_id: str,
    ) -> RequestScopeContext:
        """Extract scope context from request.
        
        Reads from:
        - Headers: X-Scope-Level, X-User-ID, X-Resource-ID, etc.
        - Path parameters: /api/projects/{project_id}/resources/{resource_id}
        - Query parameters: ?scope_level=project&project_id=123
        
        Args:
            request: HTTP request
            request_id: Request ID for tracking
            
        Returns:
            Extracted scope context
            
        Raises:
            ScopeValidationError: If required scope fields are missing
        """
        # Get scope level (required)
        scope_level = (
            request.headers.get("X-Scope-Level")
            or request.query_params.get("scope_level")
            or None  # Will be determined below
        )
        
        # Get user ID (required for permission checks)
        user_id = (
            request.headers.get("X-User-ID")
            or request.query_params.get("user_id")
            or "anonymous"
        )
        
        # Get resource ID (optional)
        resource_id = (
            request.headers.get("X-Resource-ID")
            or request.path_params.get("resource_id")
            or request.query_params.get("resource_id")
        )
        
        # Get project ID (for project+ scopes)
        project_id = None
        project_id_str = (
            request.headers.get("X-Project-ID")
            or request.path_params.get("project_id")
            or request.query_params.get("project_id")
        )
        if project_id_str:
            try:
                project_id = int(project_id_str)
            except (ValueError, TypeError):
                raise ScopeValidationError(
                    f"Invalid project_id: {project_id_str}",
                    scope_level=scope_level or "unknown",
                    invalid_fields=["project_id"],
                )
        
        # Get session ID (optional for now, will validate based on scope level)
        session_id = (
            request.headers.get("X-Session-ID")
            or request.path_params.get("session_id")
            or request.query_params.get("session_id")
        )
        
        # Infer scope level if not explicitly provided
        if not scope_level:
            if session_id:
                scope_level = "session"
            elif project_id:
                scope_level = "project"
            else:
                scope_level = "app"  # Default to app scope if nothing else available
        
        # Validate scope level
        try:
            ScopeLevel(scope_level)
        except ValueError:
            raise ScopeValidationError(
                f"Invalid scope_level: {scope_level}",
                scope_level=scope_level,
                invalid_fields=["scope_level"],
            )
        
        # Validate that session scope has both project and session IDs
        if scope_level == "session":
            if not session_id:
                raise ScopeValidationError(
                    "SESSION scope requires session_id",
                    scope_level=scope_level,
                    invalid_fields=["session_id"],
                )
            if not project_id:
                raise ScopeValidationError(
                    "SESSION scope requires project_id",
                    scope_level=scope_level,
                    invalid_fields=["project_id"],
                )
        
        # Note: Project scope project_id validation is skipped here because
        # path_params are not available in BaseHTTPMiddleware (runs before route matching).
        # Validation can be enforced in _validate_scope_context or application layer.
        
        # Get runtime ID (for runtime+ scopes)
        runtime_id = None
        if scope_level in ["runtime", "session"]:
            runtime_id = (
                request.headers.get("X-Runtime-ID")
                or request.query_params.get("runtime_id")
            )
        
        return RequestScopeContext(
            request_id=request_id,
            scope_level=scope_level,
            user_id=user_id,
            resource_id=resource_id,
            project_id=project_id,
            session_id=session_id,
            runtime_id=runtime_id,
        )
    
    def _validate_scope_context(self, ctx: RequestScopeContext) -> None:
        """Validate scope context consistency.
        
        Args:
            ctx: Scope context to validate
            
        Raises:
            ScopeValidationError: If validation fails
        """
        # Validate scope level
        try:
            scope_level = ScopeLevel(ctx.scope_level)
        except ValueError:
            raise ScopeValidationError(
                f"Invalid scope_level: {ctx.scope_level}",
                scope_level=ctx.scope_level,
                invalid_fields=["scope_level"],
            )
        
        # Validate scope hierarchy requirements
        if scope_level == ScopeLevel.PROJECT and not ctx.project_id:
            raise ScopeValidationError(
                "PROJECT scope requires project_id",
                scope_level=ctx.scope_level,
                invalid_fields=["project_id"],
            )
        
        if scope_level == ScopeLevel.SESSION:
            if not ctx.project_id:
                raise ScopeValidationError(
                    "SESSION scope requires project_id",
                    scope_level=ctx.scope_level,
                    invalid_fields=["project_id"],
                )
            if not ctx.session_id:
                raise ScopeValidationError(
                    "SESSION scope requires session_id",
                    scope_level=ctx.scope_level,
                    invalid_fields=["session_id"],
                )
    
    async def _check_permissions(
        self,
        ctx: RequestScopeContext,
        request: Request,
    ) -> None:
        """Check if user has permission for this scope/action.
        
        Args:
            ctx: Scope context
            request: HTTP request
            
        Raises:
            ScopePermissionError: If permission check fails
        """
        # Extract action from HTTP method
        action = self._http_method_to_action(request.method)
        
        # Perform permission check (would integrate with permission system)
        # This is a simplified example
        has_permission = await check_scope_permission(
            user_id=ctx.user_id,
            scope_level=ctx.scope_level,
            action=action,
            resource_id=ctx.resource_id,
            project_id=ctx.project_id,
            session_id=ctx.session_id,
        )
        
        if not has_permission:
            raise ScopePermissionError(
                f"User {ctx.user_id} lacks permission for {action} in {ctx.scope_level} scope",
                scope_level=ctx.scope_level,
                resource_id=ctx.resource_id,
                user_id=ctx.user_id,
                action=action,
            )
    
    @staticmethod
    def _http_method_to_action(method: str) -> str:
        """Map HTTP method to scope action.
        
        Args:
            method: HTTP method
            
        Returns:
            Scope action name
        """
        method_to_action = {
            "GET": "read",
            "HEAD": "read",
            "OPTIONS": "read",
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        return method_to_action.get(method, "read")
    
    async def _audit_access(
        self,
        ctx: RequestScopeContext,
        request: Request,
        result: str,
    ) -> None:
        """Log successful scope access to audit trail.
        
        Args:
            ctx: Scope context
            request: HTTP request
            result: Result status
        """
        try:
            audit_logger = get_audit_logger()
            action = self._http_method_to_action(request.method)
            
            await audit_logger.log_permission_check(
                user_id=ctx.user_id,
                resource=f"api:{request.url.path}",
                action=action,
                scope_level=ctx.scope_level,
                result=result,
                details={
                    "request_id": ctx.request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "elapsed_ms": ctx.elapsed_ms(),
                },
            )
        except Exception as e:
            logger.error(f"Failed to log audit access: {e}")
    
    async def _audit_permission_error(
        self,
        error: ScopePermissionError,
        request_id: str,
    ) -> None:
        """Log permission denial to audit trail.
        
        Args:
            error: Permission error
            request_id: Request ID for tracking
        """
        try:
            audit_logger = await get_audit_logger()
            
            await audit_logger.log_permission_check(
                user_id=error.context.get("user_id", "unknown"),
                resource="api:error",
                action=error.context.get("action", "unknown"),
                scope_level=error.context.get("scope_level", "unknown"),
                result="denied",
                details={
                    "request_id": request_id,
                    "error_message": error.message,
                },
            )
        except Exception as e:
            logger.error(f"Failed to log permission error: {e}")
    
    @staticmethod
    def _error_response(error: ScopeError, status_code: int) -> JSONResponse:
        """Generate error response for scope error.
        
        Args:
            error: Scope error
            status_code: HTTP status code
            
        Returns:
            JSON error response
        """
        return JSONResponse(
            status_code=status_code,
            content={
                "error": {
                    "type": error.__class__.__name__,
                    "message": str(error),
                    "error_code": error.error_code,
                    "context": error.context,
                }
            },
        )
