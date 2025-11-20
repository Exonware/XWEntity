#!/usr/bin/env python3
"""
The public-facing xEntity facade with enhanced performance.

This module provides the primary `xEntity` class that users interact with.
It is an immutable-style facade built on top of the internal, mutable aEntity model,
offering enhanced performance through caching, lazy loading, and optimized operations.
"""

import threading
import weakref
from collections import OrderedDict
from typing import Any, Dict, Optional, List, Union, Iterator, Tuple, Callable
from pathlib import Path
from datetime import datetime

# --- Core xEntity Imports ---
from .model import aEntity, aEntityFactory, xEntityState
from .errors import (
    xEntityError, xEntityValidationError, xEntityStateError, 
    xEntityActionError, xEntityNotFoundError
)
from .config import get_config
from .abc import iEntityFacade, iEntityFactory, iEntity
from .metaclass import create_xentity_metaclass

# --- System-level Imports (Optional) ---
try:
    from src.xlib.xsystem.security import get_resource_limits
    from src.xlib.xsystem.validation import validate_untrusted_data
    from src.xlib.xsystem.monitoring import create_component_metrics
    from src.xlib.xsystem import get_logger
    logger = get_logger('xentity.facade')
except (ImportError, TypeError):
    import logging
    from contextlib import nullcontext
    logger = logging.getLogger('xentity.facade')
    def create_component_metrics(component_name):
        return {
            'measure_operation': lambda name: nullcontext(),
            'record_cache_hit': lambda: None,
            'record_cache_miss': lambda: None,
        }
    class MockResourceLimits:
        def increment_resource_count(self): pass
    def get_resource_limits(component_name): return MockResourceLimits()
    def validate_untrusted_data(data): pass

# --- Metrics Setup ---
_metrics = create_component_metrics('xentity')
measure_operation = _metrics['measure_operation']
record_cache_hit = _metrics['record_cache_hit']
record_cache_miss = _metrics['record_cache_miss']


class xEntityCache:
    """
    A thread-safe cache for entity operations with performance monitoring.
    """
    __slots__ = ('_cache', '_lock', '_max_size', '_hit_count', '_miss_count')

    def __init__(self, max_size: int = 1024):
        self._cache = OrderedDict()
        self._lock = threading.RLock() if get_config().enable_thread_safety else None
        self._max_size = max_size
        self._hit_count = 0
        self._miss_count = 0

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._lock:
            with self._lock:
                return self._get_impl(key)
        return self._get_impl(key)

    def _get_impl(self, key: str) -> Optional[Any]:
        """Internal cache get implementation."""
        if key in self._cache:
            self._hit_count += 1
            record_cache_hit()
            self._cache.move_to_end(key)
            return self._cache[key]
        
        self._miss_count += 1
        record_cache_miss()
        return None

    def put(self, key: str, value: Any) -> None:
        """Put value in cache."""
        if self._lock:
            with self._lock:
                self._put_impl(key, value)
        else:
            self._put_impl(key, value)

    def _put_impl(self, key: str, value: Any) -> None:
        """Internal cache put implementation."""
        self._cache[key] = value
        self._cache.move_to_end(key)
        
        if len(self._cache) > self._max_size:
            self._cache.popitem(last=False)

    def clear(self) -> None:
        """Clear the cache."""
        if self._lock:
            with self._lock:
                self._cache.clear()
        else:
            self._cache.clear()

    @property
    def hit_rate(self) -> float:
        """Get cache hit rate."""
        total = self._hit_count + self._miss_count
        return self._hit_count / total if total > 0 else 0.0

    def stats(self) -> Dict[str, Union[int, float]]:
        """Get cache statistics."""
        return {
            'size': len(self._cache),
            'max_size': self._max_size,
            'hits': self._hit_count,
            'misses': self._miss_count,
            'hit_rate': self.hit_rate
        }


# --- Global Cache Instance ---
_entity_cache_instance: Optional[xEntityCache] = None
def get_entity_cache() -> xEntityCache:
    global _entity_cache_instance
    if _entity_cache_instance is None:
        _entity_cache_instance = xEntityCache(get_config().entity_cache_size)
    return _entity_cache_instance


class xEntity(metaclass=create_xentity_metaclass()):
    """
    The public facade for an xEntity, implementing the iEntityFacade interface.
    
    This class provides a clean, immutable-style interface built on top of
    the internal, mutable aEntity model. It offers enhanced performance through
    caching, lazy loading, and optimized operations.
    """
    
    __slots__ = ('_internal', '_hash_cache', '_type_cache', '_cache')
    
    def __init__(self, internal: Optional[aEntity] = None, **kwargs):
        """Initialize the xEntity facade with an internal aEntity or direct properties."""
        if internal is not None:
            # Initialize with existing aEntity (factory usage)
            self._internal = internal
        else:
            # Create new aEntity from property values (direct usage)
            entity_type = getattr(self.__class__, '__name__', 'entity').lower()
            self._internal = aEntity(entity_type=entity_type, data=kwargs)
            
            # Set properties using the metaclass-created property setters
            for key, value in kwargs.items():
                if hasattr(self, key):
                    setattr(self, key, value)
        
        self._hash_cache: Optional[int] = None
        self._type_cache: Optional[str] = None
        self._cache = get_entity_cache()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], schema: Optional['xSchema'] = None) -> 'xEntity':
        """Create entity from dictionary."""
        internal = aEntityFactory.from_dict(data, schema)
        return cls(internal)
    
    @classmethod
    def from_file(cls, path: Union[str, Path], schema: Optional['xSchema'] = None) -> 'xEntity':
        """Create entity from file."""
        internal = aEntityFactory.from_file(path, schema)
        return cls(internal)
    
    @classmethod
    def from_schema(cls, schema: Union[str, Path, 'xSchema'], initial_data: Optional[Dict] = None) -> 'xEntity':
        """Create entity with schema and optional initial data."""
        internal = aEntityFactory.from_schema(schema, initial_data)
        return cls(internal)
    
    @classmethod
    def from_data(cls, data: Union[Dict, 'xData'], schema: Optional['xSchema'] = None) -> 'xEntity':
        """Create entity with data and optional schema."""
        internal = aEntityFactory.from_data(data, schema)
        return cls(internal)
    
    @classmethod
    def from_untrusted(cls, data: Any) -> 'xEntity':
        """Create entity from untrusted data with validation."""
        validate_untrusted_data(data)
        return cls.from_dict(data) if isinstance(data, dict) else cls.from_data(data)
    
    @staticmethod
    def clear_caches():
        """Clear all entity caches."""
        get_entity_cache().clear()
    
    # ============================================================================
    # PROPERTIES
    # ============================================================================
    
    @property
    def id(self) -> str:
        """Get the unique entity identifier."""
        return self._internal.id
    
    @property
    def type(self) -> str:
        """Get the entity type name."""
        return self._internal.type
    
    @property
    def schema(self) -> Optional['xSchema']:
        """Get the entity schema."""
        return self._internal.schema
    
    @property
    def data(self) -> 'xData':
        """Get the entity data."""
        return self._internal.data
    
    @property
    def actions(self) -> Dict[str, Any]:
        """Get the entity actions."""
        return self._internal._export_actions()
    
    @property
    def state(self) -> str:
        """Get the current entity state."""
        return self._internal.state
    
    @property
    def version(self) -> int:
        """Get the entity version number."""
        return self._internal.version
    
    @property
    def created_at(self) -> datetime:
        """Get the creation timestamp."""
        return self._internal.created_at
    
    @property
    def updated_at(self) -> datetime:
        """Get the last update timestamp."""
        return self._internal.updated_at
    
    # ============================================================================
    # DATA OPERATIONS
    # ============================================================================
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        with measure_operation('entity_get'):
            return self._internal._get(path, default)
    
    def set(self, path: str, value: Any) -> 'xEntity':
        """Set value at path (chainable)."""
        with measure_operation('entity_set'):
            self._internal._set(path, value)
            return self
    
    def delete(self, path: str) -> 'xEntity':
        """Delete value at path (chainable)."""
        with measure_operation('entity_delete'):
            self._internal._delete(path)
            return self
    
    def update(self, updates: Dict[str, Any]) -> 'xEntity':
        """Update multiple values (chainable)."""
        with measure_operation('entity_update'):
            self._internal._update(updates)
            return self
    
    # ============================================================================
    # VALIDATION
    # ============================================================================
    
    def validate(self) -> bool:
        """Validate data against schema."""
        with measure_operation('entity_validate'):
            return self._internal._validate()
    
    def validate_or_raise(self) -> None:
        """Validate and raise exception if invalid."""
        if not self.validate():
            raise xEntityValidationError("Entity validation failed")
    
    # ============================================================================
    # STATE MANAGEMENT
    # ============================================================================
    
    def to_validated(self) -> 'xEntity':
        """Transition to validated state."""
        with measure_operation('entity_to_validated'):
            self._internal._transition_to(xEntityState.VALIDATED)
            return self
    
    def commit(self) -> 'xEntity':
        """Commit entity (must be validated first)."""
        with measure_operation('entity_commit'):
            self._internal._transition_to(xEntityState.COMMITTED)
            return self
    
    def archive(self) -> 'xEntity':
        """Archive entity."""
        with measure_operation('entity_archive'):
            self._internal._transition_to(xEntityState.ARCHIVED)
            return self
    
    def restore(self) -> 'xEntity':
        """Restore archived entity to draft."""
        with measure_operation('entity_restore'):
            if self.state != xEntityState.ARCHIVED:
                raise xEntityStateError(
                    self.state,
                    xEntityState.DRAFT,
                    "Can only restore from archived state"
                )
            self._internal._transition_to(xEntityState.DRAFT)
            return self
    
    # ============================================================================
    # ACTIONS
    # ============================================================================
    
    def execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        with measure_operation('entity_execute_action'):
            return self._internal._execute_action(action_name, **kwargs)
    
    def list_actions(self) -> List[str]:
        """List available action names."""
        return self._internal._list_actions()
    
    def export_actions(self) -> Dict[str, Dict[str, Any]]:
        """Export action metadata."""
        return self._internal._export_actions()
    
    # ============================================================================
    # SERIALIZATION
    # ============================================================================
    
    def to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        with measure_operation('entity_to_dict'):
            return self._internal._to_dict()
    
    def to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        with measure_operation('entity_to_file'):
            return self._internal._to_file(path, format)
    
    def to_native(self) -> Dict[str, Any]:
        """Get entity as native dictionary."""
        return self._internal._to_native()
    
    # ============================================================================
    # UTILITY METHODS
    # ============================================================================
    
    def copy(self) -> 'xEntity':
        """Create a copy of this entity with new ID."""
        with measure_operation('entity_copy'):
            # Export current state
            data = self.to_dict()
            
            # Create new instance
            entity = self.__class__.from_dict(data, self.schema)
            
            # Copy metadata except ID and timestamps
            entity._internal._metadata.tags = self._internal._metadata.tags.copy()
            entity._internal._metadata.metadata = self._internal._metadata.metadata.copy()
            
            return entity
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"<xEntity(type='{self.type}', id='{self.id}', "
                f"state='{self.state}', version={self.version})>")
    
    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.type}#{self.id}"
    
    def __hash__(self) -> int:
        """Hash based on entity ID."""
        if self._hash_cache is None:
            self._hash_cache = hash(self.id)
        return self._hash_cache
    
    def __eq__(self, other: Any) -> bool:
        """Equality based on entity ID."""
        if not isinstance(other, xEntity):
            return False
        return self.id == other.id
    
    # ============================================================================
    # ADVANCED OPERATIONS
    # ============================================================================
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self._internal._get_performance_stats()
    
    def optimize_for_access(self) -> 'xEntity':
        """Optimize the entity for fast access operations."""
        self._internal._optimize_for_access()
        return self
    
    def optimize_for_validation(self) -> 'xEntity':
        """Optimize the entity for fast validation operations."""
        self._internal._optimize_for_validation()
        return self
    
    def get_memory_usage(self) -> int:
        """Get the memory usage in bytes."""
        return self._internal._get_memory_usage()
    
    def optimize_memory(self) -> 'xEntity':
        """Optimize memory usage."""
        self._internal._optimize_memory()
        return self
    
    # ============================================================================
    # EXTENSIBILITY
    # ============================================================================
    
    def register_extension(self, name: str, extension: Any) -> 'xEntity':
        """Register an extension with the entity."""
        self._internal.register_extension(name, extension)
        return self
    
    def get_extension(self, name: str) -> Optional[Any]:
        """Get an extension by name."""
        return self._internal.get_extension(name)
    
    def has_extension(self, name: str) -> bool:
        """Check if an extension exists."""
        return self._internal.has_extension(name)
    
    def list_extensions(self) -> List[str]:
        """List all registered extensions."""
        return self._internal.list_extensions()
    
    def remove_extension(self, name: str) -> bool:
        """Remove an extension by name."""
        return self._internal.remove_extension(name)
    
    def has_extension_type(self, extension_type: str) -> bool:
        """Check if an extension of a specific type exists."""
        return self._internal.has_extension_type(extension_type)


class xEntityFactory(iEntityFactory):
    """
    Factory for creating xEntity instances.
    """
    
    @staticmethod
    def from_dict(data: Dict[str, Any], schema: Optional['xSchema'] = None) -> xEntity:
        """Create entity from dictionary."""
        return xEntity.from_dict(data, schema)
    
    @staticmethod
    def from_file(path: Union[str, Path], schema: Optional['xSchema'] = None) -> xEntity:
        """Create entity from file."""
        return xEntity.from_file(path, schema)
    
    @staticmethod
    def from_schema(schema: Union[str, Path, 'xSchema'], initial_data: Optional[Dict] = None) -> xEntity:
        """Create entity with schema and optional initial data."""
        return xEntity.from_schema(schema, initial_data)
    
    @staticmethod
    def from_data(data: Union[Dict, 'xData'], schema: Optional['xSchema'] = None) -> xEntity:
        """Create entity with data and optional schema."""
        return xEntity.from_data(data, schema)
    
    @staticmethod
    def to_dict(entity: xEntity) -> Dict[str, Any]:
        """Convert entity to dictionary."""
        return entity.to_dict()
    
    @staticmethod
    def to_file(entity: xEntity, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        return entity.to_file(path, format)
