"""
Security Tests for Phase 6B REST API

Tests security controls:
- Path traversal prevention
- Authentication enforcement
- Authorization checks
- Input validation
- Error handling
- Audit logging

Run with: pytest tests/test_phase6b_rest_api_security.py -v --tb=short
"""

import pytest
import sys
import os
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent / "packages" / "com.twg.the-seed" / "seed" / "engine"))

# Import security modules
try:
    from security_validators import InputValidator
    from auth_middleware import AuthToken, ROLE_ADMIN, ROLE_VIEWER, BearerAuth, AuditLogger
    SECURITY_MODULES_AVAILABLE = True
except ImportError:
    SECURITY_MODULES_AVAILABLE = False
    pytest.skip("Security modules not available", allow_module_level=True)


# ============================================================================
# PATH TRAVERSAL PREVENTION TESTS
# ============================================================================

class TestPathTraversalPrevention:
    """Verify path traversal attacks are blocked."""
    
    def test_parent_directory_traversal_blocked(self):
        """Test that ../ patterns are rejected."""
        with pytest.raises(Exception):  # Should raise HTTPException
            InputValidator.validate_filepath("../../../etc/passwd")
    
    def test_url_encoded_traversal_blocked(self):
        """Test that URL-encoded traversal %2e%2e is rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("%2e%2e%2fpasswd")
    
    def test_double_encoded_traversal_blocked(self):
        """Test that double-encoded traversal is rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("%252e%252e%252fetc%252fpasswd")
    
    def test_backslash_traversal_blocked(self):
        """Test that Windows-style traversal is rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("..\\..\\windows\\system32")
    
    def test_environment_variable_injection_blocked(self):
        """Test that environment variable references are rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("$HOME/.ssh/id_rsa")
    
    def test_command_injection_blocked(self):
        """Test that command injection patterns are rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("snapshot; rm -rf /")
    
    def test_pipe_injection_blocked(self):
        """Test that pipe characters are rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("snapshot | cat /etc/passwd")
    
    def test_valid_filename_accepted(self):
        """Test that valid filenames are accepted."""
        result = InputValidator.validate_filepath("snapshot-2025-01-15.json")
        assert isinstance(result, Path)
        assert result.name == "snapshot-2025-01-15.json"
    
    def test_valid_nested_path_accepted(self):
        """Test that valid nested paths within base dir are accepted."""
        result = InputValidator.validate_filepath("archive/daily/snapshot.json")
        assert isinstance(result, Path)
        assert "archive" in str(result)
    
    def test_resolved_path_stays_within_base_dir(self):
        """Test that resolved path doesn't escape base directory."""
        base_dir = "/tmp/snapshots"
        result = InputValidator.validate_filepath(
            "subdir/snapshot.json",
            base_dir=base_dir
        )
        # Verify path is within base
        assert str(result).startswith(base_dir)
    
    def test_empty_filepath_rejected(self):
        """Test that empty filepath is rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath("")
    
    def test_null_filepath_rejected(self):
        """Test that None is rejected."""
        with pytest.raises(Exception):
            InputValidator.validate_filepath(None)
    
    def test_excessive_length_rejected(self):
        """Test that excessively long paths are rejected."""
        long_path = "a" * 500  # Exceeds default 260 limit
        with pytest.raises(Exception):
            InputValidator.validate_filepath(long_path)


# ============================================================================
# INPUT VALIDATION TESTS
# ============================================================================

class TestInputValidation:
    """Verify all user inputs are properly validated."""
    
    def test_realm_id_validation_alphanumeric(self):
        """Test realm ID accepts valid format."""
        result = InputValidator.validate_realm_id("realm_123")
        assert result == "realm_123"
    
    def test_realm_id_rejects_special_chars(self):
        """Test realm ID rejects special characters."""
        with pytest.raises(Exception):
            InputValidator.validate_realm_id("realm@123")
    
    def test_realm_id_rejects_excessive_length(self):
        """Test realm ID length validation."""
        long_id = "a" * 200
        with pytest.raises(Exception):
            InputValidator.validate_realm_id(long_id)
    
    def test_npc_id_validation(self):
        """Test NPC ID validation."""
        result = InputValidator.validate_npc_id("npc-warbler_001")
        assert result == "npc-warbler_001"
    
    def test_npc_id_rejects_invalid_chars(self):
        """Test NPC ID rejects invalid characters."""
        with pytest.raises(Exception):
            InputValidator.validate_npc_id("npc!@#$")
    
    def test_seed_validation_valid_range(self):
        """Test seed validation accepts valid range."""
        result = InputValidator.validate_seed(12345)
        assert result == 12345
    
    def test_seed_validation_rejects_negative(self):
        """Test seed validation rejects negative values."""
        with pytest.raises(Exception):
            InputValidator.validate_seed(-1)
    
    def test_seed_validation_rejects_too_large(self):
        """Test seed validation rejects values > 2^31-1."""
        with pytest.raises(Exception):
            InputValidator.validate_seed(2**31)
    
    def test_hash_validation_hex_format(self):
        """Test hash validation accepts valid hex."""
        valid_hash = "abc123def456"
        result = InputValidator.validate_hash(valid_hash)
        assert result == valid_hash
    
    def test_hash_validation_rejects_non_hex(self):
        """Test hash validation rejects non-hex."""
        with pytest.raises(Exception):
            InputValidator.validate_hash("abc123xyz")


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

class TestAuthentication:
    """Verify authentication controls."""
    
    def test_token_creation_valid_format(self):
        """Test valid token is created."""
        token = AuthToken.create_token("user123", role="admin")
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 20
    
    def test_token_includes_user_id(self):
        """Test token contains user ID."""
        token = AuthToken.create_token("user123", role="admin")
        payload = AuthToken.verify_token(token)
        assert payload["user_id"] == "user123"
    
    def test_token_includes_role(self):
        """Test token contains role."""
        token = AuthToken.create_token("user123", role="admin")
        payload = AuthToken.verify_token(token)
        assert payload["role"] == "admin"
    
    def test_invalid_token_rejected(self):
        """Test invalid token is rejected."""
        with pytest.raises(Exception):
            AuthToken.verify_token("invalid.token.here")
    
    def test_expired_token_rejected(self):
        """Test expired token is rejected."""
        # Create token with 0 hour expiry (immediately expired)
        token = AuthToken.create_token("user123", expires_in_hours=0)
        import time
        time.sleep(1)  # Ensure expiry
        with pytest.raises(Exception):
            AuthToken.verify_token(token)
    
    def test_tampered_token_rejected(self):
        """Test tampered token is rejected."""
        token = AuthToken.create_token("user123")
        tampered = token[:-5] + "XXXXX"  # Modify last characters
        with pytest.raises(Exception):
            AuthToken.verify_token(tampered)


# ============================================================================
# AUTHORIZATION TESTS
# ============================================================================

class TestAuthorization:
    """Verify role-based access control."""
    
    def test_admin_token_has_admin_role(self):
        """Test admin token contains admin role."""
        token = AuthToken.create_token("admin_user", role=ROLE_ADMIN)
        payload = AuthToken.verify_token(token)
        assert payload["role"] == ROLE_ADMIN
    
    def test_viewer_token_has_viewer_role(self):
        """Test viewer token contains viewer role."""
        token = AuthToken.create_token("viewer_user", role=ROLE_VIEWER)
        payload = AuthToken.verify_token(token)
        assert payload["role"] == ROLE_VIEWER
    
    def test_token_different_for_different_roles(self):
        """Test different tokens for different roles."""
        admin_token = AuthToken.create_token("user", role=ROLE_ADMIN)
        viewer_token = AuthToken.create_token("user", role=ROLE_VIEWER)
        
        admin_payload = AuthToken.verify_token(admin_token)
        viewer_payload = AuthToken.verify_token(viewer_token)
        
        assert admin_payload["role"] != viewer_payload["role"]


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Verify error messages don't leak sensitive info."""
    
    def test_generic_error_message_returned(self):
        """Test generic error message to client."""
        from security_validators import SecureErrorHandler
        
        error = Exception("SELECT * FROM users WHERE id = 1; DROP TABLE users;")
        safe_msg = SecureErrorHandler.safe_error_detail(error, context="test")
        
        # Should NOT contain original error
        assert "SELECT" not in safe_msg
        assert "DROP TABLE" not in safe_msg
        assert "An error occurred" in safe_msg
    
    def test_file_path_not_in_error_message(self):
        """Test file paths not exposed in errors."""
        from security_validators import SecureErrorHandler
        
        error = FileNotFoundError("/home/admin/.ssh/config")
        safe_msg = SecureErrorHandler.safe_error_detail(error, context="test")
        
        assert "/home/admin" not in safe_msg
        assert ".ssh" not in safe_msg


# ============================================================================
# AUDIT LOGGING TESTS
# ============================================================================

class TestAuditLogging:
    """Verify actions are logged."""
    
    def test_action_logged(self):
        """Test that action is logged."""
        entry = AuditLogger.log_action(
            user_id="user123",
            action="snapshot_save",
            resource="snapshot.json",
            result="success"
        )
        
        assert entry["user_id"] == "user123"
        assert entry["action"] == "snapshot_save"
        assert entry["resource"] == "snapshot.json"
        assert entry["result"] == "success"
    
    def test_audit_entry_has_timestamp(self):
        """Test audit entry includes timestamp."""
        entry = AuditLogger.log_action(
            user_id="user123",
            action="test",
            resource="test",
            result="success"
        )
        
        assert "timestamp" in entry
        assert entry["timestamp"] is not None
    
    def test_metadata_included_in_audit(self):
        """Test metadata is included in audit log."""
        metadata = {"realm_id": "realm_123", "changes": ["name", "description"]}
        entry = AuditLogger.log_action(
            user_id="user123",
            action="realm_update",
            resource="realm_123",
            result="success",
            metadata=metadata
        )
        
        assert entry["metadata"] == metadata


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestSecurityIntegration:
    """Integration tests for security controls."""
    
    def test_path_validation_in_workflow(self):
        """Test complete path validation workflow."""
        # Valid path should pass
        valid_path = InputValidator.validate_filepath("snapshot.json")
        assert valid_path is not None
        
        # Traversal should fail
        with pytest.raises(Exception):
            InputValidator.validate_filepath("../malicious.json")
    
    def test_full_auth_flow(self):
        """Test complete authentication flow."""
        # 1. Create token
        token = AuthToken.create_token("user123", role=ROLE_ADMIN)
        assert token is not None
        
        # 2. Verify token
        payload = AuthToken.verify_token(token)
        assert payload["user_id"] == "user123"
        
        # 3. Check role
        assert payload["role"] == ROLE_ADMIN
    
    def test_security_headers_present(self):
        """Test security headers configuration."""
        # This would test the actual FastAPI app security headers
        # Configured in CORS and middleware setup
        pass


# ============================================================================
# COMPLIANCE TESTS
# ============================================================================

class TestComplianceRequirements:
    """Verify compliance with security standards."""
    
    def test_all_inputs_validated(self):
        """Verify all input validators exist."""
        assert hasattr(InputValidator, 'validate_filepath')
        assert hasattr(InputValidator, 'validate_realm_id')
        assert hasattr(InputValidator, 'validate_npc_id')
        assert hasattr(InputValidator, 'validate_seed')
        assert hasattr(InputValidator, 'validate_hash')
    
    def test_all_error_handlers_exist(self):
        """Verify error handling is in place."""
        from security_validators import SecureErrorHandler
        assert hasattr(SecureErrorHandler, 'safe_error_detail')
        assert hasattr(SecureErrorHandler, 'raise_safe_error')
    
    def test_audit_logging_implemented(self):
        """Verify audit logging is implemented."""
        assert hasattr(AuditLogger, 'log_action')
    
    def test_auth_enforcement_available(self):
        """Verify auth enforcement mechanisms exist."""
        assert hasattr(BearerAuth, 'get_current_user')


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])