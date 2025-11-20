#!/usr/bin/env python3
"""
🚨 xEntity Error Classes
Simple, focused exceptions for entity operations.
"""

from typing import Optional, Any, Dict


class xEntityError(Exception):
    """Base exception for all xEntity errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class xEntityValidationError(xEntityError):
    """Raised when entity validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, 
                 constraint: Optional[str] = None):
        details = {
            "field": field,
            "constraint": constraint
        }
        super().__init__(message, details)


class xEntityStateError(xEntityError):
    """Raised when entity state transition is invalid."""
    
    def __init__(self, current_state: str, target_state: str, 
                 reason: Optional[str] = None):
        message = f"Cannot transition from '{current_state}' to '{target_state}'"
        if reason:
            message += f": {reason}"
        details = {
            "current_state": current_state,
            "target_state": target_state,
            "reason": reason
        }
        super().__init__(message, details)


class xEntityActionError(xEntityError):
    """Raised when entity action execution fails."""
    
    def __init__(self, action_name: str, reason: str):
        message = f"Action '{action_name}' failed: {reason}"
        details = {
            "action": action_name,
            "reason": reason
        }
        super().__init__(message, details)


class xEntityNotFoundError(xEntityError):
    """Raised when entity is not found."""
    
    def __init__(self, entity_id: str, entity_type: Optional[str] = None):
        message = f"Entity '{entity_id}' not found"
        if entity_type:
            message = f"{entity_type} entity '{entity_id}' not found"
        details = {
            "entity_id": entity_id,
            "entity_type": entity_type
        }
        super().__init__(message, details) 