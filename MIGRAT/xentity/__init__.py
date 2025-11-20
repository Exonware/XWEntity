#!/usr/bin/env python3
"""
🏢 xEntity Module
Smart data containers combining schema, data, and actions.

This module provides:
- xEntity: Main entity class
- EntityState: Lifecycle states
- Errors: Entity-specific exceptions

Example:
    from xlib.xentity import xEntity
    from xlib.xaction import xAction
    
    class UserEntity(xEntity):
        def __init__(self):
            super().__init__(
                schema="schemas/user.json",
                entity_type="user"
            )
        
        @xAction(
            api_name="suspend",
            roles=["admin"],
            input_schemas={
                "reason": {"minLength": 10}
            }
        )
        def suspend_user(self, reason: str) -> bool:
            self.set("status", "suspended")
            self.set("suspended_reason", reason)
            return True
"""

# Main exports
from .facade import xEntity
from .model import xEntityState, xEntityMetadata
from .errors import (
    xEntityError,
    xEntityValidationError,
    xEntityStateError,
    xEntityActionError,
    xEntityNotFoundError
)

# For advanced usage
from .model import aEntity

__all__ = [
    # Main API
    'xEntity',
    'xEntityState',
    
    # Errors
    'xEntityError',
    'xEntityValidationError',
    'xEntityStateError',
    'xEntityActionError',
    'xEntityNotFoundError',
    
    # Advanced
    'xEntityMetadata',
    'aEntity',
]

# Version info
__version__ = "2.0.0"
__author__ = "xComBot Team" 