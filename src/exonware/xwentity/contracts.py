#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/contracts.py

XWEntity Interfaces and Contracts

This module defines all interfaces for the xwentity library following
GUIDE_DEV.md standards. All interfaces use 'I' prefix.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union, Protocol, runtime_checkable
from pathlib import Path
from datetime import datetime

from .defs import EntityState, EntityType, EntityID, EntityData, EntityMetadata
from .errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
)


# ==============================================================================
# CORE ENTITY INTERFACE
# ==============================================================================

class IEntity(ABC):
    """
    Core interface for all entities in the XWEntity system.
    
    This interface defines the fundamental operations that all entities
    must support, ensuring consistency across different entity types.
    These methods are considered internal-facing, to be called by the
    public facade, hence the underscore prefix.
    """
    
    @property
    @abstractmethod
    def id(self) -> EntityID:
        """Get the unique entity identifier."""
        pass
    
    @property
    @abstractmethod
    def type(self) -> EntityType:
        """Get the entity type name."""
        pass
    
    @property
    @abstractmethod
    def schema(self) -> Optional[Any]:  # XWSchema type
        """Get the entity schema."""
        pass
    
    @property
    @abstractmethod
    def data(self) -> Any:  # XWData type
        """Get the entity data."""
        pass
    
    @property
    @abstractmethod
    def state(self) -> EntityState:
        """Get the current entity state."""
        pass
    
    @property
    @abstractmethod
    def version(self) -> int:
        """Get the entity version number."""
        pass
    
    @property
    @abstractmethod
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        pass
    
    @property
    @abstractmethod
    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        pass
    
    @abstractmethod
    def _get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        pass
    
    @abstractmethod
    def _set(self, path: str, value: Any) -> None:
        """Set value at path."""
        pass
    
    @abstractmethod
    def _delete(self, path: str) -> None:
        """Delete value at path."""
        pass
    
    @abstractmethod
    def _update(self, updates: EntityData) -> None:
        """Update multiple values."""
        pass
    
    @abstractmethod
    def _validate(self) -> bool:
        """Validate data against schema."""
        pass
    
    @abstractmethod
    def _to_dict(self) -> EntityData:
        """Export entity as dictionary."""
        pass
    
    @abstractmethod
    def _from_dict(self, data: EntityData) -> None:
        """Import entity from dictionary."""
        pass


# ==============================================================================
# ACTION INTERFACE
# ==============================================================================

class IEntityActions(ABC):
    """
    Interface for entities that support actions.
    
    This interface extends IEntity with action-related capabilities.
    """
    
    @abstractmethod
    def _execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        pass
    
    @abstractmethod
    def _list_actions(self) -> list[str]:
        """List available action names."""
        pass
    
    @abstractmethod
    def _export_actions(self) -> dict[str, dict[str, Any]]:
        """Export action metadata."""
        pass
    
    @abstractmethod
    def _register_action(self, action: Any) -> None:  # XWAction type
        """Register an action for this entity."""
        pass


# ==============================================================================
# STATE INTERFACE
# ==============================================================================

class IEntityState(ABC):
    """
    Interface for entities that support state management.
    
    This interface extends IEntity with state transition capabilities.
    """
    
    @abstractmethod
    def _transition_to(self, target_state: EntityState) -> None:
        """Transition to a new state."""
        pass
    
    @abstractmethod
    def _can_transition_to(self, target_state: EntityState) -> bool:
        """Check if state transition is allowed."""
        pass
    
    @abstractmethod
    def _update_version(self) -> None:
        """Update the entity version."""
        pass


# ==============================================================================
# SERIALIZATION INTERFACE
# ==============================================================================

class IEntitySerialization(ABC):
    """
    Interface for entities that support serialization.
    
    This interface extends IEntity with serialization capabilities.
    """
    
    @abstractmethod
    def _to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        pass
    
    @abstractmethod
    def _from_file(self, path: Union[str, Path], format: Optional[str] = None) -> None:
        """Load entity from file."""
        pass
    
    @abstractmethod
    def _to_native(self) -> EntityData:
        """Get entity as native dictionary."""
        pass
    
    @abstractmethod
    def _from_native(self, data: EntityData) -> None:
        """Create entity from native dictionary."""
        pass


# ==============================================================================
# PROTOCOL INTERFACES (for runtime checking)
# ==============================================================================

@runtime_checkable
class IEntityProtocol(Protocol):
    """
    Protocol for internal entities that can be checked at runtime.
    
    This allows for duck typing and runtime type checking of entity implementations
    without requiring explicit inheritance from IEntity.
    """
    
    id: EntityID
    type: EntityType
    state: EntityState
    version: int
    created_at: datetime
    updated_at: datetime
    
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
    "IEntity",
    "IEntityActions",
    "IEntityState",
    "IEntitySerialization",
    "IEntityProtocol",
]
