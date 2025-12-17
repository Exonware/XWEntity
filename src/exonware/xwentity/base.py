#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/base.py

XWEntity Abstract Base Classes

This module defines abstract base classes that extend interfaces from contracts.py.
Following GUIDE_DEV.md: All abstract classes start with 'A' and extend 'I' interfaces.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union
from datetime import datetime
import threading
import uuid

from exonware.xwsystem import get_logger

from .contracts import (
    IEntity,
    IEntityActions,
    IEntityState,
    IEntitySerialization,
)
from .defs import (
    EntityState,
    EntityID,
    EntityType,
    EntityData,
    EntityMetadata,
    DEFAULT_ENTITY_TYPE,
    DEFAULT_STATE,
    DEFAULT_VERSION,
    STATE_TRANSITIONS,
    DEFAULT_CACHE_SIZE,
)
from .errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
)
from .config import get_config

logger = get_logger(__name__)


# ==============================================================================
# ENTITY METADATA
# ==============================================================================

class EntityMetadata:
    """
    Internal metadata management for entities.
    
    Manages entity identity, state, versioning, and timestamps.
    """
    
    def __init__(self, entity_type: Optional[str] = None):
        """Initialize entity metadata."""
        self._id: EntityID = str(uuid.uuid4())
        self._type: EntityType = entity_type or DEFAULT_ENTITY_TYPE
        self._state: EntityState = DEFAULT_STATE
        self._version: int = DEFAULT_VERSION
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = self._created_at
    
    @property
    def id(self) -> EntityID:
        """Get entity ID."""
        return self._id
    
    @property
    def type(self) -> EntityType:
        """Get entity type."""
        return self._type
    
    @property
    def state(self) -> EntityState:
        """Get entity state."""
        return self._state
    
    @state.setter
    def state(self, value: EntityState) -> None:
        """Set entity state."""
        self._state = value
        self._updated_at = datetime.now()
    
    @property
    def version(self) -> int:
        """Get entity version."""
        return self._version
    
    def update_version(self) -> None:
        """Increment entity version."""
        self._version += 1
        self._updated_at = datetime.now()
    
    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at
    
    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary."""
        return {
            "id": self._id,
            "type": self._type,
            "state": str(self._state),
            "version": self._version,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }
    
    def from_dict(self, data: dict[str, Any]) -> None:
        """Load metadata from dictionary."""
        self._id = data.get("id", str(uuid.uuid4()))
        self._type = data.get("type", DEFAULT_ENTITY_TYPE)
        self._state = EntityState(data.get("state", DEFAULT_STATE.value))
        self._version = data.get("version", DEFAULT_VERSION)
        
        if "created_at" in data:
            self._created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data:
            self._updated_at = datetime.fromisoformat(data["updated_at"])


# ==============================================================================
# ABSTRACT ENTITY
# ==============================================================================

class AEntity(IEntity, IEntityActions, IEntityState, IEntitySerialization):
    """
    Abstract base class for all entity implementations.
    
    Provides default implementations for common functionality while requiring
    subclasses to implement core data operations. Manages metadata, caching,
    performance stats, and state transitions.
    """
    
    def __init__(
        self,
        schema: Optional[Any] = None,  # XWSchema type
        data: Optional[Any] = None,  # XWData type or dict
        entity_type: Optional[str] = None,
        config: Optional[Any] = None,  # XWEntityConfig type
    ):
        """
        Initialize abstract entity.
        
        Args:
            schema: Optional entity schema
            data: Optional initial data (dict or XWData)
            entity_type: Optional entity type name
            config: Optional entity configuration
        """
        # Core components
        self._metadata = EntityMetadata(entity_type)
        self._schema = schema
        self._config = config or get_config()
        
        # Data will be initialized by subclass
        self._data: Optional[Any] = None  # XWData type
        
        # Actions storage
        self._actions: dict[str, Any] = {}
        
        # Performance optimizations
        self._cache: dict[str, Any] = {}
        self._cache_size = self._config.cache_size if hasattr(self._config, 'cache_size') else DEFAULT_CACHE_SIZE
        self._performance_stats: dict[str, Any] = {
            "access_count": 0,
            "validation_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        
        # Thread safety
        enable_thread_safety = (
            self._config.enable_thread_safety
            if hasattr(self._config, 'enable_thread_safety')
            else False
        )
        self._lock = threading.RLock() if enable_thread_safety else None
    
    # ==========================================================================
    # CORE PROPERTIES (IEntity)
    # ==========================================================================
    
    @property
    def id(self) -> EntityID:
        """Get the unique entity identifier."""
        return self._metadata.id
    
    @property
    def type(self) -> EntityType:
        """Get the entity type name."""
        return self._metadata.type
    
    @property
    def schema(self) -> Optional[Any]:  # XWSchema type
        """Get the entity schema."""
        return self._schema
    
    @property
    @abstractmethod
    def data(self) -> Any:  # XWData type
        """Get the entity data. Must be implemented by subclass."""
        pass
    
    @property
    def state(self) -> EntityState:
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
    
    # ==========================================================================
    # DATA OPERATIONS (IEntity)
    # ==========================================================================
    
    def _get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        self._performance_stats["access_count"] += 1
        
        # Check cache first
        cache_key = f"get:{path}"
        if cache_key in self._cache:
            self._performance_stats["cache_hits"] += 1
            return self._cache[cache_key]
        
        self._performance_stats["cache_misses"] += 1
        
        # Delegate to data (must be implemented by subclass)
        if self._data is None:
            return default
        
        # Use async-safe get if available, otherwise sync
        if hasattr(self._data, 'get'):
            result = self._data.get(path, default)
        elif hasattr(self._data, 'get_value'):
            result = self._data.get_value(path, default)
        else:
            # Fallback: try to access as dict
            result = self._get_from_dict(path, default)
        
        # Cache result
        if len(self._cache) < self._cache_size:
            self._cache[cache_key] = result
        
        return result
    
    def _get_from_dict(self, path: str, default: Any = None) -> Any:
        """Get value from dict-like data structure."""
        if not hasattr(self._data, 'to_native'):
            return default
        
        data_dict = self._data.to_native()
        if not isinstance(data_dict, dict):
            return default
        
        # Simple path navigation (supports dot notation)
        parts = path.split('.')
        current = data_dict
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return default
        return current
    
    def _set(self, path: str, value: Any) -> None:
        """Set value at path."""
        if self._lock:
            with self._lock:
                self._set_impl(path, value)
        else:
            self._set_impl(path, value)
    
    def _set_impl(self, path: str, value: Any) -> None:
        """Internal set implementation."""
        if self._data is None:
            raise XWEntityError("Data not initialized")
        
        # Use async-safe set if available, otherwise sync
        if hasattr(self._data, 'set'):
            self._data.set(path, value)
        elif hasattr(self._data, 'put'):
            self._data.put(path, value)
        else:
            # Fallback: update native dict
            self._update_dict(path, value)
        
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change
    
    def _update_dict(self, path: str, value: Any) -> None:
        """Update dict-like data structure."""
        if not hasattr(self._data, 'to_native'):
            raise XWEntityError("Cannot update: data does not support native conversion")
        
        data_dict = self._data.to_native()
        if not isinstance(data_dict, dict):
            raise XWEntityError("Cannot update: data is not a dictionary")
        
        # Simple path navigation and update
        parts = path.split('.')
        current = data_dict
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value
    
    def _delete(self, path: str) -> None:
        """Delete value at path."""
        if self._lock:
            with self._lock:
                self._delete_impl(path)
        else:
            self._delete_impl(path)
    
    def _delete_impl(self, path: str) -> None:
        """Internal delete implementation."""
        if self._data is None:
            raise XWEntityError("Data not initialized")
        
        # Use async-safe delete if available
        if hasattr(self._data, 'delete'):
            self._data.delete(path)
        elif hasattr(self._data, 'remove'):
            self._data.remove(path)
        else:
            # Fallback: update native dict
            self._delete_from_dict(path)
        
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change
    
    def _delete_from_dict(self, path: str) -> None:
        """Delete from dict-like data structure."""
        if not hasattr(self._data, 'to_native'):
            return
        
        data_dict = self._data.to_native()
        if not isinstance(data_dict, dict):
            return
        
        # Simple path navigation and delete
        parts = path.split('.')
        current = data_dict
        for part in parts[:-1]:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return
        if isinstance(current, dict) and parts[-1] in current:
            del current[parts[-1]]
    
    def _update(self, updates: EntityData) -> None:
        """Update multiple values."""
        for path, value in updates.items():
            self._set(path, value)
    
    def _validate(self) -> bool:
        """Validate data against schema."""
        self._performance_stats["validation_count"] += 1
        
        if not self._schema:
            return True  # No schema means no validation
        
        if self._data is None:
            return False
        
        # Get native data for validation
        if hasattr(self._data, 'to_native'):
            data_dict = self._data.to_native()
        else:
            return False
        
        # Validate using schema
        if hasattr(self._schema, 'validate'):
            return self._schema.validate(data_dict)
        elif hasattr(self._schema, 'validate_schema'):
            return self._schema.validate_schema(data_dict)
        else:
            logger.warning("Schema does not support validation")
            return True
    
    def _to_dict(self) -> EntityData:
        """Export entity as dictionary."""
        result: EntityData = {
            "_metadata": self._metadata.to_dict(),
        }
        
        if self._data and hasattr(self._data, 'to_native'):
            result["_data"] = self._data.to_native()
        else:
            result["_data"] = {}
        
        if self._schema:
            # Schema serialization depends on implementation
            if hasattr(self._schema, 'to_dict'):
                result["_schema"] = self._schema.to_dict()
            elif hasattr(self._schema, 'to_native'):
                result["_schema"] = self._schema.to_native()
        
        if self._actions:
            result["_actions"] = {
                name: self._export_action(action)
                for name, action in self._actions.items()
            }
        
        return result
    
    def _export_action(self, action: Any) -> dict[str, Any]:
        """Export action metadata."""
        if hasattr(action, 'to_dict'):
            return action.to_dict()
        elif hasattr(action, 'to_native'):
            return action.to_native()
        elif hasattr(action, 'api_name'):
            return {"api_name": action.api_name}
        else:
            return {"type": type(action).__name__}
    
    def _from_dict(self, data: EntityData) -> None:
        """Import entity from dictionary."""
        if "_metadata" in data:
            self._metadata.from_dict(data["_metadata"])
        
        if "_data" in data:
            # Data initialization depends on subclass
            self._init_data_from_dict(data["_data"])
    
    @abstractmethod
    def _init_data_from_dict(self, data: EntityData) -> None:
        """Initialize data from dictionary. Must be implemented by subclass."""
        pass
    
    # ==========================================================================
    # ACTIONS (IEntityActions)
    # ==========================================================================
    
    def _execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        if action_name not in self._actions:
            raise XWEntityActionError(
                f"Action '{action_name}' not found",
                action_name=action_name
            )
        
        action = self._actions[action_name]
        
        # Handle different action types
        if hasattr(action, 'execute'):
            return action.execute(context=self, **kwargs)
        elif callable(action):
            return action(self, **kwargs)
        else:
            raise XWEntityActionError(
                f"Action '{action_name}' is not callable",
                action_name=action_name
            )
    
    def _list_actions(self) -> list[str]:
        """List available action names."""
        return list(self._actions.keys())
    
    def _export_actions(self) -> dict[str, dict[str, Any]]:
        """Export action metadata."""
        return {
            name: self._export_action(action)
            for name, action in self._actions.items()
        }
    
    def _register_action(self, action: Any) -> None:  # XWAction type
        """Register an action for this entity."""
        # Get action name
        if hasattr(action, 'api_name'):
            name = action.api_name
        elif hasattr(action, 'name'):
            name = action.name
        elif hasattr(action, '__name__'):
            name = action.__name__
        else:
            name = f"action_{len(self._actions)}"
        
        self._actions[name] = action
        logger.debug(f"Registered action: {name}")
    
    # ==========================================================================
    # STATE (IEntityState)
    # ==========================================================================
    
    def _transition_to(self, target_state: EntityState) -> None:
        """Transition to a new state."""
        if not self._can_transition_to(target_state):
            raise XWEntityStateError(
                f"Cannot transition from {self._metadata.state} to {target_state}",
                current_state=str(self._metadata.state),
                target_state=str(target_state)
            )
        
        self._metadata.state = target_state
        self._metadata.update_version()
        logger.debug(f"Entity {self._metadata.id} transitioned to {target_state}")
    
    def _can_transition_to(self, target_state: EntityState) -> bool:
        """Check if state transition is allowed."""
        current_state = self._metadata.state
        allowed_transitions = STATE_TRANSITIONS.get(current_state, [])
        return target_state in allowed_transitions
    
    def _update_version(self) -> None:
        """Update the entity version."""
        self._metadata.update_version()
    
    # ==========================================================================
    # SERIALIZATION (IEntitySerialization)
    # ==========================================================================
    
    def _to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        try:
            import json
            from pathlib import Path as PathLib
            
            file_path = PathLib(path)
            data = self._to_dict()
            
            # Determine format
            if format is None:
                format = file_path.suffix.lstrip('.') or 'json'
            
            if format == 'json':
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            else:
                # For other formats, delegate to data if available
                if self._data and hasattr(self._data, 'save'):
                    return self._data.save(path, format=format)
                else:
                    raise XWEntityError(f"Unsupported format: {format}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to save entity to file: {e}")
            return False
    
    def _from_file(self, path: Union[str, Path], format: Optional[str] = None) -> None:
        """Load entity from file."""
        try:
            import json
            from pathlib import Path as PathLib
            
            file_path = PathLib(path)
            
            # Determine format
            if format is None:
                format = file_path.suffix.lstrip('.') or 'json'
            
            if format == 'json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                self._from_dict(data)
            else:
                # For other formats, delegate to data if available
                if self._data and hasattr(self._data, 'load'):
                    loaded_data = self._data.load(path, format=format)
                    if hasattr(loaded_data, 'to_native'):
                        self._init_data_from_dict(loaded_data.to_native())
                else:
                    raise XWEntityError(f"Unsupported format: {format}")
        except Exception as e:
            logger.error(f"Failed to load entity from file: {e}")
            raise XWEntityError(f"Failed to load entity from file: {e}", cause=e)
    
    def _to_native(self) -> EntityData:
        """Get entity as native dictionary."""
        return self._to_dict()
    
    def _from_native(self, data: EntityData) -> None:
        """Create entity from native dictionary."""
        self._from_dict(data)
    
    # ==========================================================================
    # UTILITY METHODS
    # ==========================================================================
    
    def _clear_cache(self) -> None:
        """Clear performance cache."""
        self._cache.clear()
    
    def get_performance_stats(self) -> dict[str, Any]:
        """Get performance statistics."""
        return self._performance_stats.copy()


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "EntityMetadata",
    "AEntity",
]
