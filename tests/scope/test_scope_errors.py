"""
Comprehensive tests for scopes error handling (t365).

Tests:
- ScopeError/ScopePermissionError exception classes
- Consistent error response format
- 90%+ code coverage
"""
import pytest

from db.exceptions import (
    ScopeError,
    ScopePermissionError,
    ScopeResourceNotFoundError,
    ScopeValidationError,
    CacheInvalidationError,
    ScopeHierarchyError,
)


class TestScopeErrorBase:
    """Test base ScopeError exception."""
    
    def test_create_scope_error(self) -> None:
        """Test creating base ScopeError."""
        error = ScopeError(
            message="Access denied",
            error_code="ACCESS_DENIED",
        )
        
        assert str(error) == "Access denied"
        assert error.message == "Access denied"
        assert error.error_code == "ACCESS_DENIED"
    
    def test_scope_error_with_context(self) -> None:
        """Test ScopeError with context."""
        context = {
            "scope_level": "project",
            "resource_id": "inv-123",
        }
        
        error = ScopeError(
            message="Error occurred",
            context=context,
        )
        
        assert error.context == context
        assert error.context["scope_level"] == "project"
    
    def test_scope_error_default_context(self) -> None:
        """Test that ScopeError has default empty context."""
        error = ScopeError(message="Test error")
        assert error.context == {}


class TestScopePermissionError:
    """Test ScopePermissionError exception."""
    
    def test_create_permission_error(self) -> None:
        """Test creating permission error."""
        error = ScopePermissionError(
            message="User lacks read permission",
            user_id="analyst-001",
            resource="investigation",
            action="read",
            scope_level="project",
        )
        
        assert isinstance(error, ScopeError)
        assert error.message == "User lacks read permission"
        assert error.error_code == "PERMISSION_DENIED"
        assert error.context.get("user_id") == "analyst-001"
        assert error.context.get("action") == "read"
        assert error.context.get("scope_level") == "project"
    
    def test_permission_error_minimal(self) -> None:
        """Test permission error with minimal parameters."""
        error = ScopePermissionError(message="Access denied")
        
        assert error.message == "Access denied"
        assert error.error_code == "PERMISSION_DENIED"
        assert error.context == {}
    
    def test_permission_error_with_partial_context(self) -> None:
        """Test permission error with partial context."""
        error = ScopePermissionError(
            message="Write denied",
            resource="artifact",
        )
        
        assert error.context.get("resource") == "artifact"
        assert error.context.get("user_id") is None


class TestScopeResourceNotFoundError:
    """Test ScopeResourceNotFoundError exception."""
    
    def test_create_not_found_error(self) -> None:
        """Test creating not found error."""
        error = ScopeResourceNotFoundError(
            message="Investigation not found",
            resource_id="inv-missing",
            resource_type="Investigation",
            scope_level="project",
        )
        
        assert isinstance(error, ScopeError)
        assert error.message == "Investigation not found"
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert error.context.get("resource_id") == "inv-missing"
        assert error.context.get("resource_type") == "Investigation"
        assert error.context.get("scope_level") == "project"
    
    def test_not_found_error_basic(self) -> None:
        """Test basic not found error."""
        error = ScopeResourceNotFoundError(
            message="Resource not found"
        )
        
        assert error.error_code == "RESOURCE_NOT_FOUND"
        assert error.context == {}


class TestScopeValidationError:
    """Test ScopeValidationError exception."""
    
    def test_create_validation_error(self) -> None:
        """Test creating validation error."""
        error = ScopeValidationError(
            message="Missing required session_id",
        )
        
        assert error.message == "Missing required session_id"
        assert error.error_code == "SCOPE_VALIDATION_FAILED"
    
    def test_validation_error_with_context(self) -> None:
        """Test validation error with context."""
        context = {
            "required_fields": ["session_id", "project_id"],
            "provided_fields": ["session_id"],
        }
        
        error = ScopeValidationError(
            message="Validation failed",
            context=context,
        )
        
        assert error.context["required_fields"] == ["session_id", "project_id"]
        assert error.context["provided_fields"] == ["session_id"]


class TestCacheInvalidationError:
    """Test CacheInvalidationError exception."""
    
    def test_create_cache_error(self) -> None:
        """Test creating cache error."""
        error = CacheInvalidationError(
            message="Cache invalidation failed",
            cache_key="project:123:findings",
            scope_level="project",
        )
        
        assert error.message == "Cache invalidation failed"
        assert error.error_code == "CACHE_INVALIDATION_FAILED"
        assert error.context.get("cache_key") == "project:123:findings"
        assert error.context.get("scope_level") == "project"
    
    def test_cache_error_minimal(self) -> None:
        """Test cache error with minimal parameters."""
        error = CacheInvalidationError(
            message="Cache failed"
        )
        
        assert error.error_code == "CACHE_INVALIDATION_FAILED"


class TestScopeHierarchyError:
    """Test ScopeHierarchyError exception."""
    
    def test_create_hierarchy_error(self) -> None:
        """Test creating hierarchy error."""
        error = ScopeHierarchyError(
            message="Cannot access child scopes",
            source_scope="session",
            target_scope="runtime",
        )
        
        assert error.message == "Cannot access child scopes"
        assert error.error_code == "SCOPE_HIERARCHY_ERROR"
        assert error.context.get("source_scope") == "session"
        assert error.context.get("target_scope") == "runtime"
    
    def test_hierarchy_error_basic(self) -> None:
        """Test basic hierarchy error."""
        error = ScopeHierarchyError(
            message="Hierarchy violation"
        )
        
        assert error.error_code == "SCOPE_HIERARCHY_ERROR"


class TestErrorInheritanceHierarchy:
    """Test error inheritance and type checking."""
    
    def test_permission_error_is_scope_error(self) -> None:
        """Test that ScopePermissionError is a ScopeError."""
        error = ScopePermissionError(message="Permission denied")
        assert isinstance(error, ScopeError)
        assert isinstance(error, Exception)
    
    def test_not_found_error_is_scope_error(self) -> None:
        """Test that ScopeResourceNotFoundError is a ScopeError."""
        error = ScopeResourceNotFoundError(message="Not found")
        assert isinstance(error, ScopeError)
        assert isinstance(error, Exception)
    
    def test_validation_error_is_scope_error(self) -> None:
        """Test that ScopeValidationError is a ScopeError."""
        error = ScopeValidationError(message="Invalid")
        assert isinstance(error, ScopeError)
        assert isinstance(error, Exception)
    
    def test_cache_error_is_scope_error(self) -> None:
        """Test that CacheInvalidationError is a ScopeError."""
        error = CacheInvalidationError(message="Cache failed")
        assert isinstance(error, ScopeError)
        assert isinstance(error, Exception)
    
    def test_hierarchy_error_is_scope_error(self) -> None:
        """Test that ScopeHierarchyError is a ScopeError."""
        error = ScopeHierarchyError(message="Hierarchy failed")
        assert isinstance(error, ScopeError)
        assert isinstance(error, Exception)


class TestErrorExceptionRaising:
    """Test that errors can be properly raised and caught."""
    
    def test_raise_permission_error(self) -> None:
        """Test raising and catching permission error."""
        with pytest.raises(ScopePermissionError) as exc_info:
            raise ScopePermissionError(
                message="Permission denied",
                user_id="user-123",
                action="delete",
            )
        
        error = exc_info.value
        assert error.context.get("user_id") == "user-123"
        assert error.context.get("action") == "delete"
    
    def test_raise_and_catch_as_scope_error(self) -> None:
        """Test catching specific error as base ScopeError."""
        with pytest.raises(ScopeError) as exc_info:
            raise ScopePermissionError(
                message="Permission denied",
                action="delete",
            )
        
        error = exc_info.value
        assert isinstance(error, ScopePermissionError)
    
    def test_error_message_preservation(self) -> None:
        """Test that error messages are preserved through raise/catch."""
        original_message = "Custom permission denied message"
        
        with pytest.raises(ScopePermissionError) as exc_info:
            raise ScopePermissionError(message=original_message)
        
        caught_error = exc_info.value
        assert str(caught_error) == original_message
        assert caught_error.message == original_message
    
    def test_raise_not_found_error(self) -> None:
        """Test raising not found error."""
        with pytest.raises(ScopeResourceNotFoundError):
            raise ScopeResourceNotFoundError(
                message="Resource not found",
                resource_id="inv-999",
            )
    
    def test_raise_validation_error(self) -> None:
        """Test raising validation error."""
        with pytest.raises(ScopeValidationError):
            raise ScopeValidationError(
                message="Invalid request",
            )


class TestErrorContextPreservation:
    """Test that error context is preserved."""
    
    def test_permission_error_context_preserved(self) -> None:
        """Test that permission error context is preserved."""
        context_data = {
            "user_id": "analyst-001",
            "resource": "investigation",
            "action": "delete",
            "scope_level": "session",
        }
        
        error = ScopePermissionError(
            message="Permission denied",
            **context_data,
        )
        
        assert error.context.get("user_id") == context_data["user_id"]
        assert error.context.get("action") == context_data["action"]
        assert error.context.get("scope_level") == context_data["scope_level"]
    
    def test_not_found_error_context_preserved(self) -> None:
        """Test that not found error context is preserved."""
        error = ScopeResourceNotFoundError(
            message="Not found",
            resource_id="inv-123",
            resource_type="Investigation",
        )
        
        assert error.context.get("resource_id") == "inv-123"
        assert error.context.get("resource_type") == "Investigation"
    
    def test_validation_error_context_preserved(self) -> None:
        """Test that validation error context is preserved."""
        context = {
            "invalid_fields": ["project_id", "session_id"],
        }
        
        error = ScopeValidationError(
            message="Invalid",
            context=context,
        )
        
        assert error.context["invalid_fields"] == ["project_id", "session_id"]


class TestErrorCodes:
    """Test error code constants."""
    
    def test_all_errors_have_error_codes(self) -> None:
        """Test that all error types have consistent error codes."""
        errors = [
            (ScopeError("test"), "SCOPE_ERROR"),
            (ScopePermissionError("test"), "PERMISSION_DENIED"),
            (ScopeResourceNotFoundError("test"), "RESOURCE_NOT_FOUND"),
            (ScopeValidationError("test"), "SCOPE_VALIDATION_FAILED"),
            (CacheInvalidationError("test"), "CACHE_INVALIDATION_FAILED"),
            (ScopeHierarchyError("test"), "SCOPE_HIERARCHY_ERROR"),
        ]
        
        for error, expected_code in errors:
            assert error.error_code == expected_code, \
                f"Expected {expected_code}, got {error.error_code}"


class TestErrorMessageFormatting:
    """Test error message formatting and representation."""
    
    def test_scope_error_str_representation(self) -> None:
        """Test string representation of errors."""
        error = ScopeError(message="Test error message")
        assert str(error) == "Test error message"
    
    def test_permission_error_str_representation(self) -> None:
        """Test string representation of permission error."""
        error = ScopePermissionError(message="Permission test message")
        assert str(error) == "Permission test message"
    
    def test_error_context_not_in_string_representation(self) -> None:
        """Test that context is not included in string representation."""
        error = ScopePermissionError(
            message="Test",
            user_id="secret-user-id",
            context={"password": "secret-password"},
        )
        
        error_str = str(error)
        # String representation should only have the message
        assert error_str == "Test"


class TestErrorEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_empty_message(self) -> None:
        """Test error with empty message."""
        error = ScopeError(message="")
        assert error.message == ""
    
    def test_none_context_handled(self) -> None:
        """Test that None context is handled gracefully."""
        error = ScopeError(message="test", context=None)
        assert error.context == {}
    
    def test_large_context(self) -> None:
        """Test error with large context dictionary."""
        large_context = {f"key_{i}": f"value_{i}" for i in range(100)}
        
        error = ScopeError(
            message="test",
            context=large_context,
        )
        
        assert len(error.context) == 100
        assert error.context["key_0"] == "value_0"
        assert error.context["key_99"] == "value_99"
