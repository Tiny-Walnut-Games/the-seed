"""
Security Validators for Phase 6B REST API

Provides input validation, path traversal prevention, and secure error handling.
"""

import os
import re
from pathlib import Path
from typing import Optional, Tuple
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class InputValidator:
    """Validates user inputs against security threats."""
    
    # Unsafe path patterns (encoded and raw)
    UNSAFE_PATTERNS = [
        r'\.\.',           # Parent directory
        r'%2e%2e',        # URL-encoded parent
        r'%252e%252e',    # Double-encoded parent
        r'\.\./',         # Parent with slash
        r'\.\.\\',        # Parent with backslash
        r'~',             # Home directory
        r'\$',            # Environment variables
        r'`',             # Command substitution
        r'\|',            # Pipe
        r';',             # Command separator
        r'&',             # Command chaining
    ]
    
    @staticmethod
    def validate_filepath(
        filepath: str,
        base_dir: Optional[str] = None,
        max_length: int = 260
    ) -> Path:
        """
        Validate and sanitize filepath to prevent path traversal.
        
        Args:
            filepath: User-provided file path
            base_dir: Base directory to restrict access (default: ./snapshots)
            max_length: Maximum allowed path length
            
        Returns:
            Validated Path object
            
        Raises:
            HTTPException: If path is invalid or traversal attempt detected
        """
        # Set default base directory
        if base_dir is None:
            base_dir = os.path.join(os.getcwd(), "snapshots")
        
        # Ensure base directory exists
        os.makedirs(base_dir, exist_ok=True)
        base_path = Path(base_dir).resolve()
        
        # Validate input
        if not filepath or not isinstance(filepath, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filepath: must be a non-empty string"
            )
        
        if len(filepath) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Filepath too long (max {max_length} characters)"
            )
        
        # Check for unsafe patterns
        for pattern in InputValidator.UNSAFE_PATTERNS:
            if re.search(pattern, filepath, re.IGNORECASE):
                logger.warning(f"🚨 Path traversal attempt detected: {filepath[:50]}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid filepath: suspicious characters or patterns detected"
                )
        
        # Ensure only alphanumeric, underscores, hyphens, and dots
        if not re.match(r'^[a-zA-Z0-9._\-/\\]+$', filepath):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Filepath contains invalid characters"
            )
        
        # Resolve path to prevent traversal
        try:
            user_path = (base_path / filepath).resolve()
        except (ValueError, RuntimeError) as e:
            logger.warning(f"🚨 Invalid path resolution: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filepath: could not resolve path"
            )
        
        # Ensure resolved path is within base directory
        try:
            user_path.relative_to(base_path)
        except ValueError:
            logger.warning(
                f"🚨 Path traversal blocked: {filepath} resolves outside {base_path}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access denied: path outside allowed directory"
            )
        
        return user_path
    
    @staticmethod
    def validate_realm_id(realm_id: str, max_length: int = 128) -> str:
        """Validate realm ID format."""
        if not realm_id or len(realm_id) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid realm_id"
            )
        
        if not re.match(r'^[a-zA-Z0-9_\-]+$', realm_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Realm ID contains invalid characters"
            )
        
        return realm_id
    
    @staticmethod
    def validate_npc_id(npc_id: str, max_length: int = 128) -> str:
        """Validate NPC ID format."""
        if not npc_id or len(npc_id) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid npc_id"
            )
        
        if not re.match(r'^[a-zA-Z0-9_\-]+$', npc_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="NPC ID contains invalid characters"
            )
        
        return npc_id
    
    @staticmethod
    def validate_seed(seed: int) -> int:
        """Validate universe seed."""
        if not isinstance(seed, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seed must be an integer"
            )
        
        if seed < 0 or seed > 2**31 - 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Seed must be between 0 and 2^31-1"
            )
        
        return seed
    
    @staticmethod
    def validate_hash(hash_value: str, max_length: int = 256) -> str:
        """Validate hash string format."""
        if not hash_value or len(hash_value) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid hash"
            )
        
        if not re.match(r'^[a-fA-F0-9]+$', hash_value):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hash must be hexadecimal"
            )
        
        return hash_value


class SecureErrorHandler:
    """Provides secure error messages that don't leak implementation details."""
    
    @staticmethod
    def safe_error_detail(error: Exception, context: str = "operation") -> str:
        """
        Convert exception to safe error message.
        
        Logs full details internally but returns generic message to client.
        """
        error_str = str(error)
        
        # Log full error for debugging
        logger.error(f"❌ Error during {context}: {error_str}", exc_info=True)
        
        # Return generic message to client
        return f"An error occurred during {context}. Please try again or contact support."
    
    @staticmethod
    def raise_safe_error(error: Exception, context: str = "operation", 
                        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        """Raise HTTPException with safe message."""
        raise HTTPException(
            status_code=status_code,
            detail=SecureErrorHandler.safe_error_detail(error, context)
        )