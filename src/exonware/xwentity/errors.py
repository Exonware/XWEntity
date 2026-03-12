#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/errors.py
XWEntity Unified Error Classes
This module defines all error classes for the unified xwentity library.
Merged from both xwobject and xwentity to support unified XWEntity class.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
from typing import Any
# ==============================================================================
# BASE EXCEPTION (XWEntityError is primary)
# ==============================================================================


class XWEntityError(Exception):
    """
    Base exception for all XWEntity errors.
    All entity-related exceptions should extend this class to provide
    consistent error handling and identification.
    """

    def __init__(
        self,
        message: str,
        cause: Exception | None = None,
        **kwargs: Any
    ):
        """
        Initialize entity error.
        Args:
            message: Human-readable error message
            cause: Optional underlying exception that caused this error
            **kwargs: Additional context
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.context = kwargs

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
        value: Any = None,
        validation_errors: list[str] | None = None,
        cause: Exception | None = None,
        **kwargs: Any
    ):
        """
        Initialize validation error.
        Args:
            message: Error message
            field: Optional field name that failed validation
            value: Optional value that failed validation
            validation_errors: List of validation error messages
            cause: Optional underlying exception
            **kwargs: Additional context
        """
        super().__init__(message, cause, **kwargs)
        self.field = field
        self.value = value
        self.validation_errors = validation_errors or []

    def __str__(self) -> str:
        """Get string representation."""
        parts = [self.message]
        if self.field:
            parts.append(f"Field: {self.field}")
        if self.value is not None:
            parts.append(f"Value: {self.value}")
        if self.validation_errors:
            parts.append(f"Errors: {', '.join(self.validation_errors)}")
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
# DATA EXCEPTIONS
# ==============================================================================


class XWEntityDataError(XWEntityError):
    """
    Exception raised when entity data operations fail.
    This exception is raised when:
    - Data path operations fail
    - Data format is invalid
    - Data access is denied
    """

    def __init__(
        self,
        message: str,
        data_path: str | None = None,
        cause: Exception | None = None,
        **kwargs: Any
    ):
        """
        Initialize data error.
        Args:
            message: Error message
            data_path: Optional path where the error occurred
            cause: Optional underlying exception
            **kwargs: Additional context
        """
        super().__init__(message, cause, **kwargs)
        self.data_path = data_path
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
    # Base exceptions
    "XWEntityError",
    # Validation exceptions
    "XWEntityValidationError",
    # State exceptions
    "XWEntityStateError",
    # Action exceptions
    "XWEntityActionError",
    # Data exceptions
    "XWEntityDataError",
    # Not found exceptions
    "XWEntityNotFoundError",
]
