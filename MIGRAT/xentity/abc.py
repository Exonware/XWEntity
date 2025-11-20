#!/usr/bin/env python3
"""
Abstract Base Classes and Interfaces for xEntity library.

This module defines the core interfaces that ensure consistency,
extensibility, and maintainability across the xEntity library.
"""

import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union, Callable, Protocol, runtime_checkable
from pathlib import Path
from datetime import datetime

# B4: For Python < 3.8, Protocol must be imported from typing_extensions.
if sys.version_info < (3, 8):
    from typing_extensions import Protocol
else:
    from typing import Protocol

# Import custom exceptions to be used in docstrings
from .errors import (
    xEntityError,
    xEntityValidationError,
    xEntityStateError,
    xEntityActionError
)

# Import xData and xSchema for type hints
from src.xlib.xdata import xData, xSchema
from src.xlib.xaction import xAction


# ============================================================================
# CORE ENTITY INTERFACES
# ============================================================================

class iEntity(ABC):
    """
    Core interface for all entities in the xEntity system.

    This interface defines the fundamental operations that all entities
    must support, ensuring consistency across different entity types.
    These methods are considered internal-facing, to be called by the
    public facade, hence the underscore prefix.
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """Get the unique entity identifier."""
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Get the entity type name."""
        pass

    @property
    @abstractmethod
    def schema(self) -> Optional[xSchema]:
        """Get the entity schema."""
        pass

    @property
    @abstractmethod
    def data(self) -> xData:
        """Get the entity data."""
        pass

    @property
    @abstractmethod
    def state(self) -> str:
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
    def _update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values."""
        pass

    @abstractmethod
    def _validate(self) -> bool:
        """Validate data against schema."""
        pass

    @abstractmethod
    def _to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        pass

    @abstractmethod
    def _from_dict(self, data: Dict[str, Any]) -> None:
        """Import entity from dictionary."""
        pass


class iEntityActions(ABC):
    """
    Interface for entities that support actions.

    This interface extends iEntity with action-related capabilities.
    """

    @abstractmethod
    def _execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        pass

    @abstractmethod
    def _list_actions(self) -> List[str]:
        """List available action names."""
        pass

    @abstractmethod
    def _export_actions(self) -> Dict[str, Dict[str, Any]]:
        """Export action metadata."""
        pass

    @abstractmethod
    def _register_action(self, action: Any) -> None:
        """Register an action for this entity."""
        pass


class iEntityState(ABC):
    """
    Interface for entities that support state management.

    This interface extends iEntity with state transition capabilities.
    """

    @abstractmethod
    def _transition_to(self, target_state: str) -> None:
        """Transition to a new state."""
        pass

    @abstractmethod
    def _can_transition_to(self, target_state: str) -> bool:
        """Check if state transition is allowed."""
        pass

    @abstractmethod
    def _update_version(self) -> None:
        """Update the entity version."""
        pass


class iEntitySerialization(ABC):
    """
    Interface for entities that support serialization.

    This interface extends iEntity with serialization capabilities.
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
    def _to_native(self) -> Dict[str, Any]:
        """Get entity as native dictionary."""
        pass

    @abstractmethod
    def _from_native(self, data: Dict[str, Any]) -> None:
        """Create entity from native dictionary."""
        pass


# ============================================================================
# PUBLIC FACADE INTERFACES
# ============================================================================

class iEntityFacade(ABC):
    """
    Public facade interface for entities.

    This interface defines the public API that users interact with.
    It provides a clean, immutable-style interface built on top of
    the internal, mutable model.
    """

    @staticmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any], schema: Optional[xSchema] = None) -> 'iEntityFacade':
        """Create entity from dictionary."""
        pass

    @staticmethod
    @abstractmethod
    def from_file(cls, path: Union[str, Path], schema: Optional[xSchema] = None) -> 'iEntityFacade':
        """Create entity from file."""
        pass

    @staticmethod
    @abstractmethod
    def from_schema(cls, schema: Union[str, Path, xSchema], initial_data: Optional[Dict] = None) -> 'iEntityFacade':
        """Create entity with schema and optional initial data."""
        pass

    @staticmethod
    @abstractmethod
    def from_data(cls, data: Union[Dict, xData], schema: Optional[xSchema] = None) -> 'iEntityFacade':
        """Create entity with data and optional schema."""
        pass

    # Properties
    @property
    @abstractmethod
    def id(self) -> str:
        """Get the unique entity identifier."""
        pass

    @property
    @abstractmethod
    def type(self) -> str:
        """Get the entity type name."""
        pass

    @property
    @abstractmethod
    def schema(self) -> Optional[xSchema]:
        """Get the entity schema."""
        pass

    @property
    @abstractmethod
    def data(self) -> xData:
        """Get the entity data."""
        pass

    @property
    @abstractmethod
    def actions(self) -> Dict[str, Any]:
        """Get the entity actions."""
        pass

    @property
    @abstractmethod
    def state(self) -> str:
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

    # Data Operations
    @abstractmethod
    def get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        pass

    @abstractmethod
    def set(self, path: str, value: Any) -> 'iEntityFacade':
        """Set value at path (chainable)."""
        pass

    @abstractmethod
    def delete(self, path: str) -> 'iEntityFacade':
        """Delete value at path (chainable)."""
        pass

    @abstractmethod
    def update(self, updates: Dict[str, Any]) -> 'iEntityFacade':
        """Update multiple values (chainable)."""
        pass

    # Validation
    @abstractmethod
    def validate(self) -> bool:
        """Validate data against schema."""
        pass

    @abstractmethod
    def validate_or_raise(self) -> None:
        """Validate and raise exception if invalid."""
        pass

    # State Management
    @abstractmethod
    def to_validated(self) -> 'iEntityFacade':
        """Transition to validated state."""
        pass

    @abstractmethod
    def commit(self) -> 'iEntityFacade':
        """Commit entity (must be validated first)."""
        pass

    @abstractmethod
    def archive(self) -> 'iEntityFacade':
        """Archive entity."""
        pass

    @abstractmethod
    def restore(self) -> 'iEntityFacade':
        """Restore archived entity to draft."""
        pass

    # Actions
    @abstractmethod
    def execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        pass

    @abstractmethod
    def list_actions(self) -> List[str]:
        """List available action names."""
        pass

    @abstractmethod
    def export_actions(self) -> Dict[str, Dict[str, Any]]:
        """Export action metadata."""
        pass

    # Serialization
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        pass

    @abstractmethod
    def to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        pass

    @abstractmethod
    def to_native(self) -> Dict[str, Any]:
        """Get entity as native dictionary."""
        pass

    # Utility
    @abstractmethod
    def copy(self) -> 'iEntityFacade':
        """Create a copy of this entity with new ID."""
        pass

    @abstractmethod
    def __repr__(self) -> str:
        """String representation."""
        pass

    @abstractmethod
    def __str__(self) -> str:
        """Human-readable string."""
        pass


# ============================================================================
# FACTORY INTERFACES
# ============================================================================

class iEntityFactory(ABC):
    """
    Factory interface for creating entities.
    """

    @staticmethod
    @abstractmethod
    def from_dict(data: Dict[str, Any], schema: Optional[xSchema] = None) -> iEntity:
        """Create entity from dictionary."""
        pass

    @staticmethod
    @abstractmethod
    def from_file(path: Union[str, Path], schema: Optional[xSchema] = None) -> iEntity:
        """Create entity from file."""
        pass

    @staticmethod
    @abstractmethod
    def from_schema(schema: Union[str, Path, xSchema], initial_data: Optional[Dict] = None) -> iEntity:
        """Create entity with schema and optional initial data."""
        pass

    @staticmethod
    @abstractmethod
    def from_data(data: Union[Dict, xData], schema: Optional[xSchema] = None) -> iEntity:
        """Create entity with data and optional schema."""
        pass

    @staticmethod
    @abstractmethod
    def to_dict(entity: iEntity) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        pass

    @staticmethod
    @abstractmethod
    def to_file(entity: iEntity, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        pass


# ============================================================================
# PROTOCOL INTERFACES
# ============================================================================

@runtime_checkable
class iEntityProtocol(Protocol):
    """
    Protocol for internal entities that can be checked at runtime.

    This allows for duck typing and runtime type checking of entity implementations
    without requiring explicit inheritance from iEntity.
    """

    id: str
    type: str
    schema: Optional[xSchema]
    data: xData
    state: str
    version: int
    created_at: datetime
    updated_at: datetime

    def _get(self, path: str, default: Any = None) -> Any: ...
    def _set(self, path: str, value: Any) -> None: ...
    def _delete(self, path: str) -> None: ...
    def _update(self, updates: Dict[str, Any]) -> None: ...
    def _validate(self) -> bool: ...
    def _to_dict(self) -> Dict[str, Any]: ...
    def _from_dict(self, data: Dict[str, Any]) -> None: ...


@runtime_checkable
class iEntityFacadeProtocol(Protocol):
    """Protocol for the public Entity Facade that can be checked at runtime."""

    id: str
    type: str
    schema: Optional[xSchema]
    data: xData
    actions: Dict[str, Any]
    state: str
    version: int
    created_at: datetime
    updated_at: datetime

    def get(self, path: str, default: Any = None) -> Any: ...
    def set(self, path: str, value: Any) -> 'iEntityFacadeProtocol': ...
    def delete(self, path: str) -> 'iEntityFacadeProtocol': ...
    def update(self, updates: Dict[str, Any]) -> 'iEntityFacadeProtocol': ...
    def validate(self) -> bool: ...
    def validate_or_raise(self) -> None: ...
    def to_validated(self) -> 'iEntityFacadeProtocol': ...
    def commit(self) -> 'iEntityFacadeProtocol': ...
    def archive(self) -> 'iEntityFacadeProtocol': ...
    def restore(self) -> 'iEntityFacadeProtocol': ...
    def execute_action(self, action_name: str, **kwargs) -> Any: ...
    def list_actions(self) -> List[str]: ...
    def export_actions(self) -> Dict[str, Dict[str, Any]]: ...
    def to_dict(self) -> Dict[str, Any]: ...
    def to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool: ...
    def to_native(self) -> Dict[str, Any]: ...
    def copy(self) -> 'iEntityFacadeProtocol': ...


# ============================================================================
# PERFORMANCE INTERFACES
# ============================================================================

class iPerformanceOptimized(ABC):
    """
    Interface for performance-optimized entities.

    This interface provides methods for performance monitoring and optimization.
    """

    @abstractmethod
    def _optimize_for_access(self) -> None:
        """Optimize the entity for fast access operations."""
        pass

    @abstractmethod
    def _optimize_for_validation(self) -> None:
        """Optimize the entity for fast validation operations."""
        pass

    @abstractmethod
    def _cache_schema(self) -> None:
        """Cache the schema for faster validation."""
        pass

    @abstractmethod
    def _clear_cache(self) -> None:
        """Clear all caches."""
        pass

    @abstractmethod
    def _get_memory_usage(self) -> int:
        """Get the memory usage in bytes."""
        pass

    @abstractmethod
    def _optimize_memory(self) -> None:
        """Optimize memory usage."""
        pass

    @abstractmethod
    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        pass


# ============================================================================
# EXTENSIBILITY INTERFACES
# ============================================================================

class iExtensible(ABC):
    """
    Interface for extensible entities.

    This interface allows entities to be extended with custom functionality.
    """

    @abstractmethod
    def register_extension(self, name: str, extension: Any) -> None:
        """Register an extension with the entity."""
        pass

    @abstractmethod
    def get_extension(self, name: str) -> Optional[Any]:
        """Get an extension by name."""
        pass

    @abstractmethod
    def has_extension(self, name: str) -> bool:
        """Check if an extension exists."""
        pass

    @abstractmethod
    def list_extensions(self) -> List[str]:
        """List all registered extensions."""
        pass

    @abstractmethod
    def remove_extension(self, name: str) -> bool:
        """Remove an extension by name."""
        pass

    @abstractmethod
    def has_extension_type(self, extension_type: str) -> bool:
        """Check if an extension of a specific type exists."""
        pass


class iEntityCustom(iEntity, iExtensible):
    """
    Interface for custom entities with extensions.
    """

    @abstractmethod
    def get_custom_type(self) -> str:
        """Get the custom entity type."""
        pass

    @abstractmethod
    def get_custom_data(self) -> Any:
        """Get custom entity data."""
        pass

    @abstractmethod
    def set_custom_data(self, data: Any) -> None:
        """Set custom entity data."""
        pass


# ============================================================================
# VALIDATION INTERFACES
# ============================================================================

class iValidatable(ABC):
    """
    Interface for entities that support validation.
    """

    @abstractmethod
    def validate(self) -> bool:
        """Validate the entity."""
        pass

    @abstractmethod
    def get_validation_errors(self) -> List[str]:
        """Get validation errors."""
        pass

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if the entity is valid."""
        pass

    @abstractmethod
    def validate_schema(self, schema: Any) -> bool:
        """Validate against a specific schema."""
        pass

    @abstractmethod
    def get_validation_warnings(self) -> List[str]:
        """Get validation warnings."""
        pass

    @abstractmethod
    def fix_validation_errors(self) -> bool:
        """Attempt to fix validation errors."""
        pass


# ============================================================================
# SERIALIZATION INTERFACES
# ============================================================================

class iSerializable(ABC):
    """
    Interface for entities that support serialization.
    """

    @abstractmethod
    def serialize(self, format: str = "native") -> Any:
        """Serialize the entity to the specified format."""
        pass

    @abstractmethod
    def deserialize(self, data: Any, format: str = "native") -> None:
        """Deserialize the entity from the specified format."""
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get supported serialization formats."""
        pass

    @abstractmethod
    def to_file(self, path: str, format: str = "auto") -> None:
        """Save entity to file."""
        pass

    @abstractmethod
    def from_file(self, path: str, format: str = "auto") -> None:
        """Load entity from file."""
        pass

    @abstractmethod
    def get_format_from_extension(self, extension: str) -> Optional[str]:
        """Get format from file extension."""
        pass
