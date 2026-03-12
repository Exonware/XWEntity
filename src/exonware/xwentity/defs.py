#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/defs.py
XWEntity Unified Type Definitions and Constants
This module defines types, enums, and constants used throughout the unified xwentity library.
Merged from both xwobject and xwentity to support unified XWEntity class.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
from typing import Any, Protocol, runtime_checkable
from datetime import datetime
from enum import Enum
# ==============================================================================
# TYPE ALIASES (Unified - Entity types are primary, Object types are aliases)
# ==============================================================================
# Entity types (primary)
EntityType = str
"""Type alias for entity type identifier."""
EntityID = str
"""Type alias for entity unique identifier."""
EntityData = dict[str, Any]
"""Type alias for entity data dictionary."""
EntityMetadata = dict[str, Any]
"""Type alias for entity metadata dictionary."""
# Object types (aliases)
ObjectID = EntityID
"""Type alias for object identifier (same as EntityID)."""
ObjectType = EntityType
"""Type alias for object type (same as EntityType)."""
ObjectData = EntityData
"""Type alias for object data (same as EntityData)."""
ObjectMetadata = EntityMetadata
"""Type alias for object metadata (same as EntityMetadata)."""
# ==============================================================================
# ENTITY STATE ENUM (Primary - more comprehensive)
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
    ACTIVE = "active"
    """Object is active."""
    INACTIVE = "inactive"
    """Object is inactive."""
    DELETED = "deleted"
    """Object is deleted."""

    def __str__(self) -> str:
        """Get string representation."""
        return self.value
# ==============================================================================
# OBJECT STATE ENUM (Alias)
# ==============================================================================
ObjectState = EntityState
# ==============================================================================
# PERFORMANCE MODE ENUM
# ==============================================================================


class PerformanceMode(str, Enum):
    """
    Performance optimization modes for entity property access.
    Different modes optimize for different use cases:
    - PERFORMANCE: Direct property access (fastest, more memory)
    - MEMORY: Delegated to XWData (memory efficient, slightly slower)
    - BALANCED: Hybrid approach (good balance)
    - AUTO: Automatically choose based on entity size
    """
    PERFORMANCE = "performance"
    """Optimize for fast property access using direct attributes."""
    MEMORY = "memory"
    """Optimize for memory efficiency using XWData delegation."""
    BALANCED = "balanced"
    """Hybrid approach balancing performance and memory."""
    AUTO = "auto"
    """Automatically choose mode based on entity characteristics."""

    def __str__(self) -> str:
        """Get string representation."""
        return self.value
# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================
# Default entity configuration (primary)
DEFAULT_ENTITY_TYPE = "entity"
"""Default entity type name."""
DEFAULT_OBJECT_TYPE = DEFAULT_ENTITY_TYPE
"""Default object type name."""
DEFAULT_STATE = EntityState.DRAFT
"""Default entity state."""
DEFAULT_VERSION = 1
"""Default entity version number."""
# State transition rules (entity states are primary)
STATE_TRANSITIONS: dict[EntityState, list[EntityState]] = {
    EntityState.DRAFT: [EntityState.DRAFT, EntityState.VALIDATED, EntityState.ARCHIVED, EntityState.ACTIVE],
    EntityState.VALIDATED: [
        EntityState.COMMITTED,
        EntityState.DRAFT,
        EntityState.ARCHIVED
    ],
    EntityState.COMMITTED: [EntityState.ARCHIVED],
    EntityState.ARCHIVED: [EntityState.DRAFT],  # Can restore to draft
    EntityState.ACTIVE: [EntityState.INACTIVE, EntityState.ARCHIVED, EntityState.DELETED],
    EntityState.INACTIVE: [EntityState.ACTIVE, EntityState.ARCHIVED, EntityState.DELETED],
    EntityState.DELETED: [],  # Terminal state
}
"""Valid state transitions for entity lifecycle."""
# Performance configuration
DEFAULT_CACHE_SIZE = 512
"""Default cache size for entity operations."""
DEFAULT_THREAD_SAFETY = False
"""Default thread safety setting."""
DEFAULT_PERFORMANCE_MODE = PerformanceMode.AUTO
"""Default performance mode for entity property access."""
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
    # Type aliases (Entity types - primary)
    "EntityType",
    "EntityID",
    "EntityData",
    "EntityMetadata",
    # Type aliases (Object types)
    "ObjectID",
    "ObjectType",
    "ObjectData",
    "ObjectMetadata",
    # Enums
    "EntityState",
    "ObjectState",
    "PerformanceMode",
    # Constants
    "DEFAULT_ENTITY_TYPE",
    "DEFAULT_OBJECT_TYPE",
    "DEFAULT_STATE",
    "DEFAULT_VERSION",
    "STATE_TRANSITIONS",
    "DEFAULT_CACHE_SIZE",
    "DEFAULT_THREAD_SAFETY",
    "DEFAULT_PERFORMANCE_MODE",
    # Protocols
    "IEntityProtocol",
]
