#!/usr/bin/env python3
"""
The internal, mutable data model for the xEntity system.

This module is not intended for public use. It defines the `aEntity` classes
that provide the underlying structure and performance optimizations used by
the public `xEntity` facade. Each class formally implements its corresponding
abstract interface from `abc.py`.
"""

import threading
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Union, Iterator, Tuple, Callable
from pathlib import Path
from datetime import datetime

from .errors import (
    xEntityError, xEntityValidationError, xEntityStateError, 
    xEntityActionError, xEntityNotFoundError
)
from .config import get_config, PerformanceMode
from .abc import (
    iEntity, iEntityActions, iEntityState, iEntitySerialization,
    iEntityFactory, iPerformanceOptimized, iExtensible
)

# Import xData and xSchema for type hints
from src.xlib.xdata import xData, xSchema
from src.xlib.xaction import xAction


# ============================================================================
# ENTITY STATE MANAGEMENT
# ============================================================================

class xEntityState:
    """Entity lifecycle states."""
    DRAFT = "draft"
    VALIDATED = "validated"
    COMMITTED = "committed"
    ARCHIVED = "archived"


class xEntityMetadata:
    """Entity metadata management."""
    
    def __init__(self, entity_type: Optional[str] = None):
        self.id: str = str(uuid.uuid4())
        self.type: str = entity_type or "entity"
        self.state: str = xEntityState.DRAFT
        self.version: int = 1
        self.created_at: datetime = datetime.now()
        self.updated_at: datetime = datetime.now()
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "state": self.state,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load metadata from dictionary."""
        self.id = data.get("id", str(uuid.uuid4()))
        self.type = data.get("type", "entity")
        self.state = data.get("state", xEntityState.DRAFT)
        self.version = data.get("version", 1)
        self.created_at = datetime.fromisoformat(data.get("created_at", datetime.now().isoformat()))
        self.updated_at = datetime.fromisoformat(data.get("updated_at", datetime.now().isoformat()))
        self.tags = data.get("tags", [])
        self.metadata = data.get("metadata", {})
    
    def update_version(self) -> None:
        """Update version and timestamp."""
        self.version += 1
        self.updated_at = datetime.now()


# ============================================================================
# ABSTRACT ENTITY IMPLEMENTATIONS
# ============================================================================

class aEntity(iEntity, iEntityActions, iEntityState, iEntitySerialization, iPerformanceOptimized, iExtensible):
    """
    Abstract base for all internal entities, implementing the iEntity interface.
    
    This class provides the core functionality for entities with performance
    optimizations, caching, and extensibility.
    """
    
    def __init__(self, 
                 schema: Optional[xSchema] = None,
                 data: Optional[Union[Dict, xData]] = None,
                 entity_type: Optional[str] = None):
        """Initialize the abstract entity."""
        # Core components
        self._metadata = xEntityMetadata(entity_type)
        self._schema = schema
        self._data = self._init_data(data)
        self._actions: Dict[str, Any] = {}
        
        # Performance optimizations
        self._cache: Dict[str, Any] = {}
        self._schema_cache: Optional[Dict[str, Any]] = None
        self._performance_stats: Dict[str, Any] = {
            "access_count": 0,
            "validation_count": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Extensibility
        self._extensions: Dict[str, Any] = {}
        
        # Thread safety
        self._lock = threading.RLock() if getattr(get_config(), 'enable_thread_safety', False) else None
        
        # State validation rules
        self._state_transitions = {
            xEntityState.DRAFT: [xEntityState.VALIDATED, xEntityState.ARCHIVED],
            xEntityState.VALIDATED: [xEntityState.COMMITTED, xEntityState.DRAFT, xEntityState.ARCHIVED],
            xEntityState.COMMITTED: [xEntityState.ARCHIVED],
            xEntityState.ARCHIVED: [xEntityState.DRAFT]  # Can restore to draft
        }
    
    def _init_data(self, data: Optional[Union[Dict, xData]]) -> xData:
        """Initialize data component."""
        if data is None:
            return xData({})
        elif isinstance(data, dict):
            return xData(data)
        elif isinstance(data, xData):
            return data
        else:
            raise TypeError(f"Data must be dict or xData, got {type(data)}")
    
    # ============================================================================
    # CORE PROPERTIES (iEntity)
    # ============================================================================
    
    @property
    def id(self) -> str:
        """Get the unique entity identifier."""
        return self._metadata.id
    
    @property
    def type(self) -> str:
        """Get the entity type name."""
        return self._metadata.type
    
    @property
    def schema(self) -> Optional[xSchema]:
        """Get the entity schema."""
        return self._schema
    
    @property
    def data(self) -> xData:
        """Get the entity data."""
        return self._data
    
    @property
    def state(self) -> str:
        """Get the current entity state."""
        return self._metadata.state
    
    @property
    def version(self) -> int:
        """Get the entity version number."""
        return self._metadata.version
    
    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._metadata.created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        return self._metadata.updated_at
    
    # ============================================================================
    # DATA OPERATIONS (iEntity)
    # ============================================================================
    
    def _get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        self._performance_stats["access_count"] += 1
        return self._data.get(path, default)
    
    def _set(self, path: str, value: Any) -> None:
        """Set value at path."""
        self._data.set(path, value)
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change
    
    def _delete(self, path: str) -> None:
        """Delete value at path."""
        self._data.delete(path)
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change
    
    def _update(self, updates: Dict[str, Any]) -> None:
        """Update multiple values."""
        for path, value in updates.items():
            self._set(path, value)
    
    def _validate(self) -> bool:
        """Validate data against schema."""
        self._performance_stats["validation_count"] += 1
        
        if not self._schema:
            return True  # No schema means no validation
        
        return self._schema.validate_data(self._data.to_native())
    
    def _to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        result = {
            "_metadata": self._metadata.to_dict(),
            "_data": self._data.to_native()
        }
        
        if self._schema:
            result["_schema"] = {
                "uri": self._schema.value if hasattr(self._schema, 'value') else None,
                "version": getattr(self._schema, 'version', None)
            }
        
        if self._actions:
            result["_actions"] = {
                name: action.to_native() if hasattr(action, 'to_native') else action
                for name, action in self._actions.items()
            }
        
        return result
    
    def _from_dict(self, data: Dict[str, Any]) -> None:
        """Import entity from dictionary."""
        if "_metadata" in data:
            self._metadata.from_dict(data["_metadata"])
        
        if "_data" in data:
            self._data = xData(data["_data"])
        
        # Note: Schema and actions would need to be handled separately
        # as they require more complex reconstruction
    
    # ============================================================================
    # ACTIONS (iEntityActions)
    # ============================================================================
    
    def _execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        if action_name not in self._actions:
            raise xEntityActionError(action_name, "Action not registered")
        
        action = self._actions[action_name]
        
        # Handle both Action instances and decorated functions
        if hasattr(action, '_action_instance'):
            # This is a decorated function, use the action instance
            return action._action_instance.execute(context=self, **kwargs)
        elif hasattr(action, 'execute'):
            # This is an Action instance
            return action.execute(context=self, **kwargs)
        else:
            # Fallback: call the function directly
            return action(self, **kwargs)
    
    def _list_actions(self) -> List[str]:
        """List available action names."""
        return list(self._actions.keys())
    
    def _export_actions(self) -> Dict[str, Dict[str, Any]]:
        """Export action metadata."""
        result = {}
        for name, action in self._actions.items():
            if hasattr(action, '_action_instance'):
                # This is a decorated function, use the action instance
                result[name] = action._action_instance.to_native()
            elif hasattr(action, 'to_native'):
                # This is an Action instance
                result[name] = action.to_native()
            else:
                # Fallback: create basic metadata
                result[name] = {
                    "api_name": name,
                    "description": getattr(action, '__doc__', ''),
                    "roles": getattr(action, 'roles', ['*'])
                }
        return result
    
    def _register_action(self, action: Any) -> None:
        """Register an action for this entity."""
        # Handle both Action instances and decorated functions
        if hasattr(action, '_action_instance'):
            # This is a decorated function, use its api_name
            self._actions[action.api_name] = action
        elif hasattr(action, 'api_name'):
            # This is an Action instance
            self._actions[action.api_name] = action
        else:
            # Fallback: use function name
            self._actions[action.__name__] = action
    
    # ============================================================================
    # STATE MANAGEMENT (iEntityState)
    # ============================================================================
    
    def _transition_to(self, target_state: str) -> None:
        """Transition to a new state."""
        if not self._can_transition_to(target_state):
            raise xEntityStateError(
                self._metadata.state,
                target_state,
                "Transition not allowed"
            )
        
        # Additional validation for certain transitions
        if target_state == xEntityState.VALIDATED:
            if not self._validate():
                raise xEntityStateError(
                    self._metadata.state,
                    target_state,
                    "Validation failed"
                )
        
        self._metadata.state = target_state
        self._metadata.update_version()
    
    def _can_transition_to(self, target_state: str) -> bool:
        """Check if state transition is allowed."""
        current_state = self._metadata.state
        allowed_states = self._state_transitions.get(current_state, [])
        return target_state in allowed_states
    
    def _update_version(self) -> None:
        """Update the entity version."""
        self._metadata.update_version()
    
    # ============================================================================
    # SERIALIZATION (iEntitySerialization)
    # ============================================================================
    
    def _to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        data = self._to_dict()
        self._data.to_file(str(path), format_hint=format)
        return True
    
    def _from_file(self, path: Union[str, Path], format: Optional[str] = None) -> None:
        """Load entity from file."""
        path = Path(path)
        data = xData.from_file(str(path), format_hint=format)
        self._data = data
    
    def _to_native(self) -> Dict[str, Any]:
        """Get entity as native dictionary."""
        return self._to_dict()
    
    def _from_native(self, data: Dict[str, Any]) -> None:
        """Create entity from native dictionary."""
        self._from_dict(data)
    
    # ============================================================================
    # PERFORMANCE OPTIMIZATION (iPerformanceOptimized)
    # ============================================================================
    
    def _optimize_for_access(self) -> None:
        """Optimize the entity for fast access operations."""
        # Pre-cache frequently accessed paths
        self._cache_schema()
    
    def _optimize_for_validation(self) -> None:
        """Optimize the entity for fast validation operations."""
        self._cache_schema()
    
    def _cache_schema(self) -> None:
        """Cache the schema for faster validation."""
        if self._schema and not self._schema_cache:
            self._schema_cache = self._schema.to_native() if hasattr(self._schema, 'to_native') else None
    
    def _clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
        self._schema_cache = None
    
    def _get_memory_usage(self) -> int:
        """Get the memory usage in bytes."""
        # Simple estimation
        import sys
        return sys.getsizeof(self._data) + sys.getsizeof(self._metadata) + sys.getsizeof(self._actions)
    
    def _optimize_memory(self) -> None:
        """Optimize memory usage."""
        # Clear unnecessary caches
        self._clear_cache()
        
        # Compact data if possible
        if hasattr(self._data, 'compact'):
            self._data.compact()
    
    def _get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self._performance_stats.copy()
    
    # ============================================================================
    # EXTENSIBILITY (iExtensible)
    # ============================================================================
    
    def register_extension(self, name: str, extension: Any) -> None:
        """Register an extension with the entity."""
        self._extensions[name] = extension
    
    def get_extension(self, name: str) -> Optional[Any]:
        """Get an extension by name."""
        return self._extensions.get(name)
    
    def has_extension(self, name: str) -> bool:
        """Check if an extension exists."""
        return name in self._extensions
    
    def list_extensions(self) -> List[str]:
        """List all registered extensions."""
        return list(self._extensions.keys())
    
    def remove_extension(self, name: str) -> bool:
        """Remove an extension by name."""
        if name in self._extensions:
            del self._extensions[name]
            return True
        return False
    
    def has_extension_type(self, extension_type: str) -> bool:
        """Check if an extension of a specific type exists."""
        return any(
            hasattr(ext, '__class__') and extension_type in ext.__class__.__name__.lower()
            for ext in self._extensions.values()
        )


# ============================================================================
# FACTORY IMPLEMENTATION
# ============================================================================

class aEntityFactory(iEntityFactory):
    """
    Factory for creating entities.
    """
    
    @staticmethod
    def from_dict(data: Dict[str, Any], schema: Optional[xSchema] = None) -> aEntity:
        """Create entity from dictionary."""
        entity = aEntity(schema=schema)
        entity._from_dict(data)
        return entity
    
    @staticmethod
    def from_file(path: Union[str, Path], schema: Optional[xSchema] = None) -> aEntity:
        """Create entity from file."""
        entity = aEntity(schema=schema)
        entity._from_file(path)
        return entity
    
    @staticmethod
    def from_schema(schema: Union[str, Path, xSchema], initial_data: Optional[Dict] = None) -> aEntity:
        """Create entity with schema and optional initial data."""
        if isinstance(schema, (str, Path)):
            schema = xSchema.from_file(str(schema))
        
        entity = aEntity(schema=schema, data=initial_data)
        return entity
    
    @staticmethod
    def from_data(data: Union[Dict, xData], schema: Optional[xSchema] = None) -> aEntity:
        """Create entity with data and optional schema."""
        entity = aEntity(schema=schema, data=data)
        return entity
    
    @staticmethod
    def to_dict(entity: aEntity) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return entity._to_dict()
    
    @staticmethod
    def to_file(entity: aEntity, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        return entity._to_file(path, format)
