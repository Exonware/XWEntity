#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/defs.py

XWEntity Type Definitions and Constants

This module defines all type definitions, enums, and constants for the xwentity
library following GUIDE_DEV.md standards.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""

from enum import Enum, auto
from typing import Any, Optional, Protocol, runtime_checkable


# ==============================================================================
# ENTITY STATE ENUM
# ==============================================================================

class EntityState(str, Enum):
    """
    Entity lifecycle states.
    
    States represent the current stage of an entity in its lifecycle,
    enabling state-based validation and operations.
    """
    
    DRAFT = "draft"
    """Entity is in draft state, can be modified freely."""
    
    VALIDATED = "validated"
    """Entity has been validated against schema."""
    
    COMMITTED = "committed"
    """Entity has been committed and is immutable."""
    
    ARCHIVED = "archived"
    """Entity has been archived and is read-only."""
    
    def __str__(self) -> str:
        """Get string representation."""
        return self.value


# ==============================================================================
# TYPE ALIASES
# ==============================================================================

EntityType = str
"""Type alias for entity type identifier."""

EntityID = str
"""Type alias for entity unique identifier."""

EntityData = dict[str, Any]
"""Type alias for entity data dictionary."""

EntityMetadata = dict[str, Any]
"""Type alias for entity metadata dictionary."""


# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# Default entity configuration
DEFAULT_ENTITY_TYPE = "entity"
"""Default entity type name."""

DEFAULT_STATE = EntityState.DRAFT
"""Default entity state."""

DEFAULT_VERSION = 1
"""Default entity version number."""

# State transition rules
STATE_TRANSITIONS: dict[EntityState, list[EntityState]] = {
    EntityState.DRAFT: [EntityState.VALIDATED, EntityState.ARCHIVED],
    EntityState.VALIDATED: [
        EntityState.COMMITTED,
        EntityState.DRAFT,
        EntityState.ARCHIVED
    ],
    EntityState.COMMITTED: [EntityState.ARCHIVED],
    EntityState.ARCHIVED: [EntityState.DRAFT],  # Can restore to draft
}
"""Valid state transitions for entity lifecycle."""

# Performance configuration
DEFAULT_CACHE_SIZE = 512
"""Default cache size for entity operations."""

DEFAULT_THREAD_SAFETY = False
"""Default thread safety setting."""


# ==============================================================================
# PROTOCOL INTERFACES (for runtime checking)
# ==============================================================================

@runtime_checkable
class IEntityProtocol(Protocol):
    """
    Protocol for entity interface that can be checked at runtime.
    
    This allows for duck typing and runtime type checking of entity
    implementations without requiring explicit inheritance.
    """
    
    id: EntityID
    type: EntityType
    state: EntityState
    version: int
    
    def _get(self, path: str, default: Any = None) -> Any: ...
    def _set(self, path: str, value: Any) -> None: ...
    def _delete(self, path: str) -> None: ...
    def _update(self, updates: EntityData) -> None: ...
    def _validate(self) -> bool: ...
    def _to_dict(self) -> EntityData: ...
    def _from_dict(self, data: EntityData) -> None: ...


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    # Enums
    "EntityState",
    # Type aliases
    "EntityType",
    "EntityID",
    "EntityData",
    "EntityMetadata",
    # Constants
    "DEFAULT_ENTITY_TYPE",
    "DEFAULT_STATE",
    "DEFAULT_VERSION",
    "STATE_TRANSITIONS",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_THREAD_SAFETY",
    # Protocols
    "IEntityProtocol",
]
