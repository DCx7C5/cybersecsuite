"""Scope enumerations."""

from enum import Enum


class ScopeLevel(str, Enum):
    """Scope hierarchy levels (GLOBAL → APP → PROJECT → RUNTIME → SESSION)."""
    
    GLOBAL = "global"
    APP = "app"
    PROJECT = "project"
    RUNTIME = "runtime"
    SESSION = "session"


class ScopeRestriction(str, Enum):
    """Access restriction modes for scopes."""
    
    NONE = "none"  # No restriction
    READ_ONLY = "read_only"  # Cannot modify
    DENY = "deny"  # Complete denial
    REQUIRE_AUTH = "require_auth"  # Must authenticate
    REQUIRE_ROLE = "require_role"  # Role-based access
