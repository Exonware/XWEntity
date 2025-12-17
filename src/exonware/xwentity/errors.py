#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/errors.py

XWEntity Custom Exceptions

This module defines all custom exceptions for the xwentity library following
GUIDE_DEV.md standards. All exceptions extend from a base exception class.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""


# ==============================================================================
# BASE EXCEPTION
# ==============================================================================

class XWEntityError(Exception):
    """
    Base exception for all XWEntity errors.
    
    All entity-related exceptions should extend this class to provide
    consistent error handling and identification.
    """
    
    def __init__(self, message: str, cause: Exception | None = None):
        """
        Initialize entity error.
        
        Args:
            message: Human-readable error message
            cause: Optional underlying exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
    
    def __str__(self) -> str:
        """Get string representation of error."""
        if self.cause:
            return f"{self.message} (caused by: {self.cause})"
        return self.message


# ==============================================================================
# VALIDATION EXCEPTIONS
# ==============================================================================

class XWEntityValidationError(XWEntityError):
    """
    Exception raised when entity validation fails.
    
    This exception is raised when:
    - Data does not conform to schema
    - Required fields are missing
    - Field values violate constraints
    - Type mismatches occur
    """
    
    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: any = None,
        cause: Exception | None = None
    ):
        """
        Initialize validation error.
        
        Args:
            message: Error message
            field: Optional field name that failed validation
            value: Optional value that failed validation
            cause: Optional underlying exception
        """
        super().__init__(message, cause)
        self.field = field
        self.value = value
    
    def __str__(self) -> str:
        """Get string representation."""
        parts = [self.message]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.value is not None:
            parts.append(f"Value: {self.value}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)


# ==============================================================================
# STATE EXCEPTIONS
# ==============================================================================

class XWEntityStateError(XWEntityError):
    """
    Exception raised when entity state operations fail.
    
    This exception is raised when:
    - Invalid state transitions are attempted
    - Operations are performed in invalid states
    - State validation fails
    """
    
    def __init__(
        self,
        message: str,
        current_state: str | None = None,
        target_state: str | None = None,
        cause: Exception | None = None
    ):
        """
        Initialize state error.
        
        Args:
            message: Error message
            current_state: Optional current entity state
            target_state: Optional target state for transition
            cause: Optional underlying exception
        """
        super().__init__(message, cause)
        self.current_state = current_state
        self.target_state = target_state
    
    def __str__(self) -> str:
        """Get string representation."""
        parts = [self.message]
        if self.current_state:
            parts.append(f"Current state: {self.current_state}")
        if self.target_state:
            parts.append(f"Target state: {self.target_state}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)


# ==============================================================================
# ACTION EXCEPTIONS
# ==============================================================================

class XWEntityActionError(XWEntityError):
    """
    Exception raised when entity action operations fail.
    
    This exception is raised when:
    - Action execution fails
    - Action is not found
    - Action validation fails
    - Action permissions are insufficient
    """
    
    def __init__(
        self,
        message: str,
        action_name: str | None = None,
        cause: Exception | None = None
    ):
        """
        Initialize action error.
        
        Args:
            message: Error message
            action_name: Optional name of the action that failed
            cause: Optional underlying exception
        """
        super().__init__(message, cause)
        self.action_name = action_name
    
    def __str__(self) -> str:
        """Get string representation."""
        parts = [self.message]
        if self.action_name:
            parts.append(f"Action: {self.action_name}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)


# ==============================================================================
# NOT FOUND EXCEPTIONS
# ==============================================================================

class XWEntityNotFoundError(XWEntityError):
    """
    Exception raised when an entity is not found.
    
    This exception is raised when:
    - Entity with given ID does not exist
    - Entity lookup fails
    - Entity has been deleted or archived
    """
    
    def __init__(
        self,
        message: str,
        entity_id: str | None = None,
        entity_type: str | None = None,
        cause: Exception | None = None
    ):
        """
        Initialize not found error.
        
        Args:
            message: Error message
            entity_id: Optional ID of the entity that was not found
            entity_type: Optional type of the entity that was not found
            cause: Optional underlying exception
        """
        super().__init__(message, cause)
        self.entity_id = entity_id
        self.entity_type = entity_type
    
    def __str__(self) -> str:
        """Get string representation."""
        parts = [self.message]
        if self.entity_id:
            parts.append(f"Entity ID: {self.entity_id}")
        if self.entity_type:
            parts.append(f"Entity Type: {self.entity_type}")
        if self.cause:
            parts.append(f"Caused by: {self.cause}")
        return " | ".join(parts)


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "XWEntityError",
    "XWEntityValidationError",
    "XWEntityStateError",
    "XWEntityActionError",
    "XWEntityNotFoundError",
]
