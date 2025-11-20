"""
xEntity - Enhanced Entity Management System
==========================================

A comprehensive entity management system built on top of xData.
Provides structured entity lifecycle management, validation, and relationships.

Key Features:
- Entity lifecycle management (create, read, update, delete)
- Schema-based validation and type safety
- Relationship management and reference handling
- Event-driven architecture with hooks
- Flexible storage backends
- Query and filtering capabilities
- Audit trail and versioning support

Core Components:
- xEntity: Main entity class with data management
- EntityManager: Centralized entity operations
- EntitySchema: Schema definition and validation
- EntityRelationship: Relationship management
- EntityHooks: Event-driven extensibility

Usage Example:
    from xlib.xentity import xEntity, EntityManager
    
    # Create entity with schema
    user = xEntity(
        data={"name": "John", "email": "john@example.com"},
        schema=user_schema
    )
    
    # Manage entities
    manager = EntityManager()
    manager.register(user)
    manager.save(user)

Version: 0.1.0
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union, List, Callable
from pathlib import Path
from enum import Enum

# Import from facade instead of monolithic file
from ...xdata.data import xData


class ReadOnlyError(Exception):
    """🔒 Exception raised when attempting to modify read-only data."""
    pass


class EntityError(Exception):
    """Base exception for xEntity-related errors."""
    pass


class EntityValidationError(EntityError):
    """🚨 Exception raised when entity validation fails."""
    def __init__(self, message: str, field_name: str, value: Any, validation_rules: Dict[str, Any]):
        self.field_name = field_name
        self.value = value
        self.validation_rules = validation_rules
        super().__init__(message)


class ReadOnlyProxy:
    """
    🔒 Read-only proxy wrapper for xData instances.
    
    This proxy exposes all read methods of xData while preventing write operations.
    Any attempt to use write methods will raise ReadOnlyError.
    """
    
    def __init__(self, target: xData):
        # Use object.__setattr__ to avoid triggering our own __setattr__
        object.__setattr__(self, '_target', target)
        object.__setattr__(self, '_read_methods', {
            'get_value', 'has_path', 'export', 'to_dict', 'keys', 'values', 'items',
            '__getitem__', '__contains__', '__iter__', '__len__', '__str__', '__repr__'
        })
        object.__setattr__(self, '_write_methods', {
            'set_value', 'merge', 'clear', 'load_and_merge', 'save_to_file',
            '__setitem__', '__delitem__'
        })
    
    def __getattr__(self, name: str) -> Any:
        if name in self._read_methods:
            return getattr(self._target, name)
        elif name in self._write_methods:
            raise ReadOnlyError(f"Cannot use write method '{name}' on read-only proxy")
        else:
            # Allow access to other attributes (like properties)
            try:
                return getattr(self._target, name)
            except AttributeError:
                raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")
    
    def __setattr__(self, name: str, value: Any) -> None:
        raise ReadOnlyError("Cannot modify read-only proxy")
    
    def __delattr__(self, name: str) -> None:
        raise ReadOnlyError("Cannot delete attributes from read-only proxy")
    
    def __getitem__(self, key: str) -> Any:
        return self._target[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        raise ReadOnlyError("Cannot modify read-only proxy using item assignment")
    
    def __delitem__(self, key: str) -> None:
        raise ReadOnlyError("Cannot delete items from read-only proxy")
    
    def __contains__(self, key: str) -> bool:
        return key in self._target
    
    def __iter__(self) -> Iterator[str]:
        return iter(self._target)
    
    def __len__(self) -> int:
        return len(self._target)
    
    def __str__(self) -> str:
        return str(self._target)
    
    def __repr__(self) -> str:
        return f"ReadOnlyProxy({repr(self._target)})"


class BaseDescriptor(ABC):
    """
    🏗️ Abstract base class for xEntity descriptors.
    
    Provides common functionality for xlive and xlink descriptors.
    """
    
    def __init__(self, 
                 default: Any = None,
                 policy: Optional[Dict[str, Any]] = None,
                 validation: Optional[Dict[str, Any]] = None,
                 **meta: Any):
        self.default = default
        self.policy = policy or {}
        self.validation = validation or {}
        self.meta = meta
        self.name: Optional[str] = None
        self._lock = threading.RLock()
    
    def __set_name__(self, owner: Type, name: str) -> None:
        """🏷️ Capture the attribute name when assigned to a class."""
        self.name = name
    
    def __get__(self, instance: Optional['xEntity'], owner: Type) -> Any:
        """🔍 Descriptor getter protocol."""
        if instance is None:
            # Class access - return the descriptor itself
            return self
        
        if self.name is None:
            raise RuntimeError("Descriptor name not set - __set_name__ was not called")
        
        # Instance access - get value from internal data
        with self._lock:
            return instance._data.get_value(self.name, self.default)
    
    def __set__(self, instance: 'xEntity', value: Any) -> None:
        """✏️ Descriptor setter protocol with validation."""
        if self.name is None:
            raise RuntimeError("Descriptor name not set - __set_name__ was not called")
        
        # Validate the value
        self._validate_value(value)
        
        # Set value in internal data
        with self._lock:
            instance._data.set_value(self.name, value)
    
    def _validate_value(self, value: Any) -> None:
        """🔍 Validate value against validation rules."""
        if not self.validation:
            return
        
        # Required validation
        if self.validation.get('required', False) and value is None:
            raise EntityValidationError(
                f"Field '{self.name}' is required",
                self.name, value, self.validation
            )
        
        # Skip further validation if value is None and not required
        if value is None:
            return
        
        # Type validation
        if 'type' in self.validation:
            expected_type = self.validation['type']
            if not isinstance(value, expected_type):
                raise EntityValidationError(
                    f"Field '{self.name}' must be of type {expected_type.__name__}, got {type(value).__name__}",
                    self.name, value, self.validation
                )
        
        # String validations
        if isinstance(value, str):
            if 'min_length' in self.validation:
                min_len = self.validation['min_length']
                if len(value) < min_len:
                    raise EntityValidationError(
                        f"Field '{self.name}' must be at least {min_len} characters long",
                        self.name, value, self.validation
                    )
            
            if 'max_length' in self.validation:
                max_len = self.validation['max_length']
                if len(value) > max_len:
                    raise EntityValidationError(
                        f"Field '{self.name}' must be at most {max_len} characters long",
                        self.name, value, self.validation
                    )
        
        # Numeric validations
        if isinstance(value, (int, float)):
            if 'minimum' in self.validation:
                minimum = self.validation['minimum']
                if value < minimum:
                    raise EntityValidationError(
                        f"Field '{self.name}' must be at least {minimum}",
                        self.name, value, self.validation
                    )
            
            if 'maximum' in self.validation:
                maximum = self.validation['maximum']
                if value > maximum:
                    raise EntityValidationError(
                        f"Field '{self.name}' must be at most {maximum}",
                        self.name, value, self.validation
                    )
        
        # Custom validator function
        if 'validator' in self.validation:
            validator = self.validation['validator']
            if callable(validator):
                try:
                    if not validator(value):
                        raise EntityValidationError(
                            f"Field '{self.name}' failed custom validation",
                            self.name, value, self.validation
                        )
                except Exception as e:
                    raise EntityValidationError(
                        f"Field '{self.name}' validation error: {str(e)}",
                        self.name, value, self.validation
                    )


class xlive(BaseDescriptor):
    """
    🔥 Live data descriptor for xEntity.
    
    Represents data that is actively managed and copied deeply by default.
    Suitable for primitive types and data that should be independent across instances.
    """
    
    def __init__(self, 
                 default: Any = None,
                 policy: Optional[Dict[str, Any]] = None,
                 validation: Optional[Dict[str, Any]] = None,
                 **meta: Any):
        # Set default policy for live data
        default_policy = {'copy': 'deep', 'serialize': 'embed'}
        if policy:
            default_policy.update(policy)
        
        super().__init__(default=default, policy=default_policy, validation=validation, **meta)


class xlink(BaseDescriptor):
    """
    🔗 Link data descriptor for xEntity.
    
    Represents data that is linked/referenced rather than owned.
    Suitable for relationships and data that should be shared across instances.
    """
    
    def __init__(self, 
                 default: Any = None,
                 policy: Optional[Dict[str, Any]] = None,
                 validation: Optional[Dict[str, Any]] = None,
                 **meta: Any):
        # Set default policy for linked data
        default_policy = {'copy': 'link', 'serialize': 'reference'}
        if policy:
            default_policy.update(policy)
        
        super().__init__(default=default, policy=default_policy, validation=validation, **meta)


class xEntity(collections.abc.MutableMapping):
    """
    🏗️ Base class for all entity models.
    
    Provides a schema-driven, object-oriented interface for structured data management.
    Built on top of xData with composition over inheritance principles.
    
    Key Features:
    - 🎯 **Schema-driven behavior**: Runtime behavior dictated by descriptors
    - 🔒 **Encapsulation**: Private data with controlled access
    - 📋 **Validation**: Automatic validation through descriptors
    - 🔄 **Intelligent copying**: Policy-aware copying strategies
    - 📊 **Metadata access**: Rich introspection capabilities
    """
    
    def __init__(self, **initial_data: Any):
        """
        🚀 Initialize xEntity with initial data.
        
        Args:
            **initial_data: Initial field values
        """
        # Initialize private data store
        self._data = xData()
        self._schema_cache: Optional[xData] = None
        self._schema_lock = threading.RLock()
        
        # Initialize default values from descriptors
        for name, attr in inspect.getmembers(self.__class__):
            if isinstance(attr, BaseDescriptor):
                if attr.default is not None:
                    # Set default value directly in data (skip validation for defaults)
                    self._data.set_value(name, attr.default)
        
        # Set initial data using setattr to trigger validation
        for key, value in initial_data.items():
            setattr(self, key, value)
    
    @property
    def data(self) -> ReadOnlyProxy:
        """🔒 Read-only access to internal data."""
        return ReadOnlyProxy(self._data)
    
    @property
    def schema(self) -> ReadOnlyProxy:
        """🔒 Read-only access to entity schema."""
        with self._schema_lock:
            if self._schema_cache is None:
                self._schema_cache = self._generate_schema()
            return ReadOnlyProxy(self._schema_cache)
    
    def _generate_schema(self) -> xData:
        """🏗️ Generate schema from class descriptors."""
        schema_data = {}
        
        # Introspect class for descriptors
        for name, attr in inspect.getmembers(self.__class__):
            if isinstance(attr, BaseDescriptor):
                field_schema = {
                    'type': 'unknown',  # Will be inferred from default or validation
                    'default': attr.default,
                    'policy': attr.policy,
                    'validation': attr.validation,
                    'meta': attr.meta
                }
                
                # Try to infer type from validation rules
                if 'type' in attr.validation:
                    field_schema['type'] = attr.validation['type'].__name__
                elif attr.default is not None:
                    field_schema['type'] = type(attr.default).__name__
                
                schema_data[name] = field_schema
        
        return xData(schema_data)
    
    def copy(self) -> 'xEntity':
        """
        🔄 Create a copy of this entity using schema-driven policies.
        
        Returns:
            New entity instance with copied data
        """
        # Create new instance of the same class
        new_instance = self.__class__()
        
        # Copy each field according to its policy
        for name, attr in inspect.getmembers(self.__class__):
            if isinstance(attr, BaseDescriptor):
                current_value = getattr(self, name)
                copy_policy = attr.policy.get('copy', 'deep')
                
                if copy_policy == 'deep':
                    # Deep copy the value
                    new_value = copy.deepcopy(current_value)
                elif copy_policy == 'link':
                    # Link to the same value
                    new_value = current_value
                elif copy_policy == 'shallow':
                    # Shallow copy the value
                    new_value = copy.copy(current_value)
                else:
                    # Default to deep copy
                    new_value = copy.deepcopy(current_value)
                
                setattr(new_instance, name, new_value)
        
        return new_instance
    
    @classmethod
    def create_type(cls, name: str, schema: xData) -> Type['xEntity']:
        """
        🏭 Factory method to create new xEntity subclass from schema.
        
        Args:
            name: Name of the new class
            schema: xData instance containing field definitions
            
        Returns:
            New xEntity subclass
        """
        # Prepare class attributes
        attrs = {}
        
        # Process schema to create descriptors
        for field_name, field_def in schema.items():
            if not isinstance(field_def, dict):
                continue
            
            # Extract field configuration
            default = field_def.get('default')
            policy = field_def.get('policy', {})
            validation = field_def.get('validation', {})
            meta = field_def.get('meta', {})
            
            # Determine descriptor type based on policy
            copy_policy = policy.get('copy', 'deep')
            if copy_policy == 'link':
                descriptor = xlink(default=default, policy=policy, validation=validation, **meta)
            else:
                descriptor = xlive(default=default, policy=policy, validation=validation, **meta)
            
            attrs[field_name] = descriptor
        
        # Create new class using type()
        return type(name, (cls,), attrs)
    
    # MutableMapping protocol implementation
    def __getitem__(self, key: str) -> Any:
        """🔍 Get item from internal data."""
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """✏️ Set item in internal data, strictly enforcing the schema."""
        descriptor = getattr(self.__class__, key, None)
        if isinstance(descriptor, BaseDescriptor):
            # Use the descriptor's __set__ to trigger validation
            descriptor.__set__(self, value)
        else:
            # The field is not defined in the schema. Forbid it.
            raise AttributeError(f"'{self.__class__.__name__}' has no attribute '{key}'. Cannot set undefined field.")
    
    def __delitem__(self, key: str) -> None:
        """🗑️ Delete item from internal data."""
        del self._data[key]
    
    def __iter__(self) -> Iterator[str]:
        """🔄 Iterate over data keys."""
        return iter(self._data)
    
    def __len__(self) -> int:
        """📊 Return number of data items."""
        return len(self._data)
    
    def __str__(self) -> str:
        """🔤 String representation."""
        class_name = self.__class__.__name__
        data_str = str(dict(self._data))
        return f"{class_name}({data_str})"
    
    def __repr__(self) -> str:
        """🔍 Detailed representation."""
        class_name = self.__class__.__name__
        data_repr = repr(dict(self._data))
        return f"{class_name}({data_repr})"


def xatt(entity_class_or_instance: Union[Type[xEntity], xEntity], attribute_name: str) -> BaseDescriptor:
    """
    🔍 Access descriptor metadata for an entity attribute.
    
    Args:
        entity_class_or_instance: Entity class or instance
        attribute_name: Name of the attribute
        
    Returns:
        The descriptor instance for the attribute
        
    Raises:
        AttributeError: If attribute doesn't exist or isn't a descriptor
    """
    # Get the class if instance was passed
    if isinstance(entity_class_or_instance, xEntity):
        entity_class = entity_class_or_instance.__class__
    else:
        entity_class = entity_class_or_instance
    
    # Get the attribute
    attr = getattr(entity_class, attribute_name, None)
    
    if attr is None:
        raise AttributeError(f"'{entity_class.__name__}' has no attribute '{attribute_name}'")
    
    if not isinstance(attr, BaseDescriptor):
        raise AttributeError(f"Attribute '{attribute_name}' is not a descriptor")
    
    return attr


# Export public API
__all__ = [
    'xEntity',
    'xlive', 
    'xlink',
    'xatt',
    'BaseDescriptor',
    'ReadOnlyProxy',
    'EntityError',
    'EntityValidationError',
    'ReadOnlyError'
]
