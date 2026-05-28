"""Core database layer — models, enums, and scopes utilities."""

# Scope and core exceptions
from .exceptions import (
    ScopeError,
    ScopePermissionError,
    ScopeValidationError,
)

# Enums (import before scope_utils to avoid circular import)
from .models.enums import ScopeLevel

# Models and enums
from .models import (
    RedBlueMode,
    AuditAction,
    Severity,
    Confidence,
    FindingStatus,
    IOCStatus,
    ProjectScope,
    SessionScope,
)

# Serializers
from .serializers import (
    BaseListSerializer,
    BaseModelSerializer,
    BaseSerializer,
    SerializerValidationError,
)
