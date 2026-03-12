#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/contracts.py
XWEntity Interfaces and Contracts
This module defines all interfaces for the xwentity library following
GUIDE_DEV.md standards. All interfaces use 'I' prefix.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 08-Nov-2025
"""

from __future__ import annotations
from typing import Any, Protocol, runtime_checkable, TYPE_CHECKING
from pathlib import Path
from datetime import datetime
from exonware.xwsystem.shared import IObject
from exonware.xwdata.contracts import IData
from exonware.xwschema.contracts import ISchema
from exonware.xwaction.contracts import IAction
from .defs import (
    EntityType,
    EntityID,
    EntityData,
    EntityState,
)
if TYPE_CHECKING:
    from typing import Any as EntityTypeHint
else:
    EntityTypeHint = Any
@runtime_checkable

class IEntity(IObject, Protocol):
    """
    Core interface for all entities in the XWEntity system.
    This interface defines the fundamental operations that all entities
    must support, ensuring consistency across different entity types.
    These methods are considered internal-facing, to be called by the
    public facade, hence the underscore prefix.
    """
    # Identity and basic metadata come from xwsystem.shared.IObject (id, uid, created_at, etc.).
    # IEntity only specialises the "type" and entity-specific aspects.
    @property

    def type(self) -> EntityType: #This will get the type from the schema
        """Get the entity type name."""
        ...
    # Schema and data (entity-aware view over underlying XWData/XWSchema)
    @property

    def schema(self) -> ISchema | None:  # XWSchema type
        """Get the entity schema."""
        ...
    # Schema and data (entity-aware view over underlying XWData/XWSchema)
    @property

    def actions(self) -> list[IAction] | None:  # List of XWAction type
        """Get the entity schema."""
        ...
    @property

    def data(self) -> IData | None:  # XWData type
        """Get the entity data."""
        ...
    @property

    def version(self) -> int:
        """Get the entity version number."""
        ...
    # Entity lifecycle state and versioning
    @property

    def state(self) -> EntityState:
        """Get the current entity state."""
        ...

    def _update(self, updates: EntityData) -> None:
        """Update multiple values."""
        ...

    def _validate(self) -> bool:
        """Validate data against schema."""
        ...
    # Actions

    def _execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        ...

    def _list_actions(self) -> list[str]:
        """List available action names."""
        ...

    def _export_actions(self) -> dict[str, dict[str, Any]]:
        """Export action metadata."""
        ...

    def _register_action(self, action: Any) -> None:  # XWAction type
        """Register an action for this entity."""
        ...
# ==============================================================================
# STATE INTERFACE
# ==============================================================================
@runtime_checkable

class IEntityState(Protocol):
    """
    Interface for entities that support state management.
    This interface extends IEntity with state transition capabilities.
    """

    def _transition_to(self, target_state: EntityState) -> None:
        """Transition to a new state."""
        ...

    def _can_transition_to(self, target_state: EntityState) -> bool:
        """Check if state transition is allowed."""
        ...

    def _update_version(self) -> None:
        """Update the entity version."""
        ...
# ==============================================================================
# SERIALIZATION INTERFACE
# ==============================================================================
@runtime_checkable

class IEntitySerialization(Protocol):
    """
    Interface for entities that support serialization.
    This interface extends IEntity with serialization capabilities.
    """

    def _to_file(self, path: str | Path, format: str | None = None) -> bool:
        """Save entity to file."""
        ...

    def _from_file(self, path: str | Path, format: str | None = None) -> None:
        """Load entity from file."""
        ...


# ==============================================================================
# COLLECTION INTERFACE
# ==============================================================================
@runtime_checkable
class ICollection[TEntity](Protocol):
    """
    Interface for lightweight logical collections of entities.

    Storage, indexing, and persistence concerns are left to higher-level libs.
    """

    @property
    def id(self) -> str:
        """Identifier for this collection (from IObject)."""
        ...

    @property
    def entity_type(self) -> type[TEntity] | str:
        """Get the entity type managed by this collection."""
        ...

    def list_actions(self) -> list[str]:
        """List available collection-level actions."""
        ...

    def execute_action(self, action_name: str, **kwargs: Any) -> Any:
        """Execute a collection-level action."""
        ...

    def register_action(self, action: Any) -> None:
        """Register a collection-level action."""
        ...


# ==============================================================================
# GROUP INTERFACE
# ==============================================================================
@runtime_checkable
class IGroup(Protocol):
    """
    Interface for lightweight logical groups of collections.

    Groups are purely logical scopes; storage concerns are handled elsewhere.
    """

    @property
    def id(self) -> str:
        """Identifier for this group (from IObject)."""
        ...

    def collections(self) -> dict[str, ICollection[Any]]:
        """Get collections by id."""
        ...

    def add_collection(self, collection: ICollection[Any]) -> None:
        """Register a collection with this group."""
        ...

    def remove_collection(self, collection_id: str) -> bool:
        """Remove a collection from this group."""
        ...

    def list_actions(self) -> list[str]:
        """List available group-level actions."""
        ...

    def execute_action(self, action_name: str, **kwargs: Any) -> Any:
        """Execute a group-level action."""
        ...

    def register_action(self, action: Any) -> None:
        """Register a group-level action."""
        ...

    def _to_native(self) -> EntityData:
        """Get entity as native dictionary."""
        ...

    def _from_native(self, data: EntityData) -> None:
        """Create entity from native dictionary."""
        ...
# ==============================================================================
# EXPORTS
# ==============================================================================
__all__ = [
    # Entity interfaces
    "IEntity",
    "IEntityState",
    "IEntitySerialization",
    # Collection / group interfaces
    "ICollection",
    "IGroup",
]
