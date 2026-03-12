#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/metaclass.py
XWEntity Metaclass System - Full MIGRAT Implementation
This module provides complete metaclass functionality for automatic property discovery
and action registration based on decorators and type hints, matching the full MIGRAT
implementation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 08-Nov-2025
"""

from typing import Any, get_type_hints, get_origin, get_args
from collections.abc import Callable
from exonware.xwsystem import get_logger
from exonware.xwaction import XWAction
from exonware.xwschema import XWSchema
from .config import get_config
from .defs import PerformanceMode
logger = get_logger(__name__)


class PropertyInfo:
    """Information about a discovered property."""

    def __init__(
        self,
        name: str,
        property_type: type | None = None,
        default: Any = None,
        schema: Any | None = None,  # XWSchema type
    ):
        """
        Initialize property info.
        Args:
            name: Property name
            property_type: Python type hint
            default: Default value
            schema: Optional XWSchema instance
        """
        self.name = name
        self.property_type = property_type
        self.default = default
        self.schema = schema
        # Check if Optional type hint is used (field is optional if Optional[T] or has default)
        self.is_required = default is None and not DecoratorScanner._is_optional_type(property_type)


class ActionInfo:
    """Information about a discovered action."""

    def __init__(
        self,
        name: str,
        func: Callable,
        action_instance: Any | None = None,  # XWAction type
    ):
        """
        Initialize action info.
        Args:
            name: Action name
            func: Function/method
            action_instance: XWAction instance if decorated
        """
        self.name = name
        self.func = func
        self.action_instance = action_instance


class DecoratorScanner:
    """Scans class definitions for decorators and type hints - Full MIGRAT implementation."""
    @staticmethod

    def scan_properties(
        namespace: dict[str, Any],
        annotations: dict[str, Any]
    ) -> list[PropertyInfo]:
        """
        Scan for property definitions using all supported decorators.
        Reuses XWSchema.extract_properties for @XWSchema decorated methods.
        Args:
            namespace: Class namespace
            annotations: Type annotations
        Returns:
            List of discovered properties
        """
        properties: list[PropertyInfo] = []
        # 1. Scan @XWSchema decorated methods - reuse XWSchema.extract_properties
        # Create a temporary class to use extract_properties
        temp_class = type('TempClass', (), namespace)
        extracted_schemas = XWSchema.extract_properties(temp_class)
        # Map extracted schemas back to PropertyInfo by matching schema objects
        processed_names = set()
        for schema in extracted_schemas:
            # Find the attribute that has this schema
            for name, attr in namespace.items():
                if name in processed_names:
                    continue
                if hasattr(attr, '_schema') and hasattr(attr, '_is_schema_decorated'):
                    schema_obj = getattr(attr, '_schema')
                    if isinstance(schema_obj, XWSchema) and id(schema_obj) == id(schema):
                        processed_names.add(name)
                        original_schema = attr._schema
                # Auto-detect type from function annotation if not specified in schema
                func_annotation = getattr(attr, '__annotations__', {}).get('return', None)
                if func_annotation and (not hasattr(original_schema, 'type') or original_schema.type is None):
                    # Create new schema with inferred type
                    try:
                        schema_params = {
                            'type': func_annotation,
                            'description': getattr(original_schema, 'description', None),
                        }
                        # Copy all schema attributes
                        for key in ['title', 'format', 'enum', 'default', 'nullable', 'deprecated',
                                   'confidential', 'strict', 'alias', 'exclude', 'pattern',
                                   'length_min', 'length_max', 'strip_whitespace', 'to_upper',
                                   'to_lower', 'value_min', 'value_max', 'value_min_exclusive',
                                   'value_max_exclusive', 'value_multiple_of', 'items',
                                   'items_min', 'items_max', 'items_unique', 'properties',
                                   'required', 'properties_additional', 'properties_min',
                                   'properties_max']:
                            if hasattr(original_schema, key):
                                val = getattr(original_schema, key)
                                if val is not None:
                                    schema_params[key] = val
                        # Remove None values
                        schema_params = {k: v for k, v in schema_params.items() if v is not None}
                        schema = XWSchema(**schema_params)
                        logger.debug(f"Auto-detected type {func_annotation} for {name}")
                    except Exception as e:
                        logger.warning(f"Failed to create schema for {name}: {e}")
                        schema = original_schema
                else:
                    schema = original_schema
                # Extract default from schema
                default_value = getattr(schema, '_default', None) or getattr(schema, 'default', None)
                # Determine if field is required:
                # 1. If 'required' is explicitly set in schema, respect it
                # 2. Otherwise, if type hint is Optional[T], field is optional
                # 3. Otherwise, if there's a default value, field is optional
                # 4. Otherwise, field is required
                schema_required = None
                # Check both 'required' and '_required' attributes
                if hasattr(schema, 'required'):
                    schema_required = getattr(schema, 'required', None)
                if schema_required is None and hasattr(schema, '_required'):
                    schema_required = getattr(schema, '_required', None)
                # If required is not explicitly set, infer from Optional type hint
                if schema_required is None and func_annotation:
                    is_optional_type = DecoratorScanner._is_optional_type(func_annotation)
                    # If Optional type, it's not required (can be None)
                    # Otherwise, if no default, it's required
                    schema_required = not is_optional_type and default_value is None
                properties.append(PropertyInfo(
                    name=name,
                    schema=schema,
                    default=default_value,
                    property_type=func_annotation
                ))
                logger.debug(f"Found @XWSchema property: {name} (type: {func_annotation}, default: {default_value}, required: {schema_required})")
        # 2. Scan @property decorated methods with type hints
        for name, attr in namespace.items():
            if isinstance(attr, property):
                # Extract type from property getter
                prop_type = None
                if attr.fget and hasattr(attr.fget, '__annotations__'):
                    return_type = attr.fget.__annotations__.get('return')
                    if return_type:
                        prop_type = return_type
                # Try to create schema from property
                schema = DecoratorScanner._convert_property_to_xschema(attr, name)
                properties.append(PropertyInfo(
                    name=name,
                    property_type=prop_type,
                    default=None,
                    schema=schema
                ))
                logger.debug(f"Found @property: {name} (type: {prop_type})")
        # 3. Scan Annotated type hints
        for name, annotation in annotations.items():
            # Skip if already found
            if name in [p.name for p in properties]:
                continue
            if name in namespace and callable(namespace[name]):
                continue
            if name.startswith('_'):
                continue
            if DecoratorScanner._is_annotated(annotation):
                schema = DecoratorScanner._extract_schema_from_annotated(annotation)
                default_value = namespace.get(name)
                if schema:
                    if default_value is not None and getattr(schema, '_default', None) is None:
                        schema._default = default_value
                    properties.append(PropertyInfo(
                        name=name,
                        schema=schema,
                        default=default_value,
                        property_type=get_args(annotation)[0] if get_args(annotation) else None
                    ))
                    logger.debug(f"Found Annotated property: {name} (default: {default_value})")
            else:
                # Simple type annotation
                default_value = namespace.get(name)
                properties.append(PropertyInfo(
                    name=name,
                    property_type=annotation,
                    default=default_value
                ))
                logger.debug(f"Found annotated property: {name} (type: {annotation}, default: {default_value})")
        # 4. Scan library-specific decorators (Pydantic, attrs, dataclass, etc.)
        properties.extend(DecoratorScanner._scan_library_decorators(namespace, annotations))
        return properties
    @staticmethod

    def _is_optional_type(annotation: Any) -> bool:
        """Check if annotation is optional type (T | None or Union[T, None])."""
        if annotation is None:
            return False
        try:
            args = get_args(annotation)
            return type(None) in args or None in args
        except Exception:
            return False
    @staticmethod

    def _is_annotated(annotation: Any) -> bool:
        """Check if annotation uses Annotated."""
        try:
            return get_origin(annotation) is not None and hasattr(annotation, '__metadata__')
        except Exception:
            return False
    @staticmethod

    def _extract_schema_from_annotated(annotation: Any) -> Any | None:
        """Extract XWSchema from Annotated type hint."""
        if not DecoratorScanner._is_annotated(annotation):
            return None
        try:
            # Get base type
            base_type = get_args(annotation)[0] if get_args(annotation) else str
            metadata = getattr(annotation, '__metadata__', ())
            # Look for existing XWSchema instance
            for item in metadata:
                if isinstance(item, XWSchema):
                    return item
            # Create XWSchema from metadata
            schema_params = {'type': base_type}
            for item in metadata:
                if isinstance(item, dict):
                    schema_params.update(item)
                elif isinstance(item, str):
                    schema_params['description'] = item
            # Only create schema if we have meaningful metadata
            if len(schema_params) > 1:
                return XWSchema(**schema_params)
        except Exception as e:
            logger.debug(f"Failed to extract schema from Annotated: {e}")
        return None
    @staticmethod

    def _convert_property_to_xschema(prop: property, name: str) -> Any | None:
        """Convert @property decorator to XWSchema."""
        try:
            prop_type = str
            description = f"Property {name}"
            if prop.fget and hasattr(prop.fget, '__annotations__'):
                return_type = prop.fget.__annotations__.get('return')
                if return_type:
                    prop_type = return_type
            if prop.fget and prop.fget.__doc__:
                description = prop.fget.__doc__.strip()
            return XWSchema(type=prop_type, description=description)
        except Exception as e:
            logger.debug(f"Failed to convert @property {name}: {e}")
            return None
    @staticmethod

    def _scan_library_decorators(
        namespace: dict[str, Any],
        annotations: dict[str, Any]
    ) -> list[PropertyInfo]:
        """Scan for supported library decorators (Pydantic, attrs, dataclass, etc.)."""
        properties: list[PropertyInfo] = []
        for name, attr in namespace.items():
            # Skip if already processed
            if name.startswith('_'):
                continue
            # Dataclass field detection
            if hasattr(attr, 'metadata') and hasattr(attr, 'default'):
                try:
                    annotation = annotations.get(name)
                    field_type = annotation if annotation else str
                    schema_params = {'type': field_type}
                    if hasattr(attr, 'metadata') and attr.metadata:
                        for key, value in attr.metadata.items():
                            if key in ['description', 'length_min', 'length_max', 'value_min', 'value_max', 'pattern']:
                                schema_params[key] = value
                    if hasattr(attr, 'default') and attr.default is not None:
                        schema_params['default'] = attr.default
                    schema = XWSchema(**schema_params)
                    properties.append(PropertyInfo(
                        name=name,
                        schema=schema,
                        default=attr.default,
                        property_type=field_type
                    ))
                    logger.debug(f"Found dataclass field: {name}")
                except Exception as e:
                    logger.debug(f"Failed to convert dataclass field {name}: {e}")
            # Pydantic FieldInfo detection
            elif str(type(attr)).find('FieldInfo') != -1 or (hasattr(attr, 'annotation') and hasattr(attr, 'default')):
                try:
                    field_type = getattr(attr, 'annotation', str)
                    schema_params = {'type': field_type}
                    if hasattr(attr, 'description') and attr.description:
                        schema_params['description'] = attr.description
                    if hasattr(attr, 'default') and attr.default is not None:
                        schema_params['default'] = attr.default
                    schema = XWSchema(**schema_params)
                    properties.append(PropertyInfo(
                        name=name,
                        schema=schema,
                        default=getattr(attr, 'default', None),
                        property_type=field_type
                    ))
                    logger.debug(f"Found Pydantic FieldInfo: {name}")
                except Exception as e:
                    logger.debug(f"Failed to convert Pydantic field {name}: {e}")
            # attrs field detection
            elif hasattr(attr, '_attrs_field') or (hasattr(attr, 'metadata') and hasattr(attr, 'default') and hasattr(attr, 'validator')):
                try:
                    schema_params = {'type': str}
                    if hasattr(attr, 'metadata') and attr.metadata:
                        if 'description' in attr.metadata:
                            schema_params['description'] = attr.metadata['description']
                    if hasattr(attr, 'default') and attr.default is not None:
                        schema_params['default'] = attr.default
                    schema = XWSchema(**schema_params)
                    properties.append(PropertyInfo(
                        name=name,
                        schema=schema,
                        default=getattr(attr, 'default', None)
                    ))
                    logger.debug(f"Found attrs field: {name}")
                except Exception as e:
                    logger.debug(f"Failed to convert attrs field {name}: {e}")
        return properties
    @staticmethod

    def scan_actions(namespace: dict[str, Any]) -> list[ActionInfo]:
        """
        Scan for action methods decorated with XWAction.
        Args:
            namespace: Class namespace
        Returns:
            List of discovered actions
        """
        actions: list[ActionInfo] = []
        for name, attr in namespace.items():
            # Check for XWAction decorated methods
            # Pattern 1: Has _is_action attribute (MIGRAT pattern)
            if hasattr(attr, '_is_action') and attr._is_action:
                action_instance = getattr(attr, '_action_instance', None)
                actions.append(ActionInfo(name, attr, action_instance))
                logger.debug(f"Found @XWAction (pattern 1): {name}")
            # Pattern 2: Is XWAction instance (current implementation)
            elif hasattr(attr, 'api_name') or (hasattr(attr, 'profile') or hasattr(attr, '_profile')):
                if isinstance(attr, XWAction) or hasattr(attr, 'execute'):
                    action_instance = attr if hasattr(attr, 'execute') else None
                    func = getattr(attr, 'func', None) or getattr(attr, '_func', None) or attr
                    actions.append(ActionInfo(name, func, action_instance))
                    logger.debug(f"Found @XWAction (pattern 2): {name}")
            # Pattern 3: Has xwaction attribute (wrapper pattern)
            elif hasattr(attr, 'xwaction'):
                action_obj = getattr(attr, 'xwaction')
                if isinstance(action_obj, XWAction):
                    actions.append(ActionInfo(name, attr, action_obj))
                    logger.debug(f"Found @XWAction (pattern 3): {name}")
        return actions
# ==============================================================================
# PROPERTY CREATION HELPERS
# ==============================================================================


def _create_direct_property(prop: PropertyInfo) -> property:
    """Create direct property accessor for performance mode."""
    private_name = f"_{prop.name}"
    default_val = prop.default
    def getter(self):
        # Try direct attribute first
        if hasattr(self, private_name):
            return getattr(self, private_name)
        # Fallback to data access
        if hasattr(self, 'data') and self.data:
            return self.get(prop.name, default_val)
        return default_val
    def setter(self, value):
        # Validate using schema if available
        config = get_config()
        if prop.schema and config.auto_validate:
            try:
                if hasattr(prop.schema, 'validate_sync'):
                    is_valid, _ = prop.schema.validate_sync(value)
                    if not is_valid:
                        raise ValueError(f"Validation failed for {prop.name}: {value}")
                elif hasattr(prop.schema, 'validate'):
                    # Note: async validate not supported in sync context
                    pass
            except Exception as e:
                logger.warning(f"Validation error for {prop.name}: {e}")
        # Store in direct attribute
        setattr(self, private_name, value)
        # Also update in data if available
        if hasattr(self, 'data') and self.data:
            self.set(prop.name, value)
    return property(getter, setter)


def _create_delegated_property(prop: PropertyInfo) -> property:
    """Create XWData-delegated property accessor for memory mode."""
    default_val = prop.default
    def getter(self):
        if hasattr(self, 'data') and self.data:
            return self.get(prop.name, default_val)
        return default_val
    def setter(self, value):
        # Validate using schema if available
        config = get_config()
        if prop.schema and config.auto_validate:
            try:
                if hasattr(prop.schema, 'validate_sync'):
                    is_valid, _ = prop.schema.validate_sync(value)
                    if not is_valid:
                        raise ValueError(f"Validation failed for {prop.name}: {value}")
            except Exception as e:
                logger.warning(f"Validation error for {prop.name}: {e}")
        if hasattr(self, 'data') and self.data:
            self.set(prop.name, value)
    return property(getter, setter)


def _is_frequently_accessed(prop: PropertyInfo) -> bool:
    """Determine if property is frequently accessed (heuristic)."""
    frequent_names = {'id', 'name', 'username', 'email', 'status', 'active', 'type', 'state'}
    return prop.name.lower() in frequent_names
# ==============================================================================
# EXPORTS
# ==============================================================================
__all__ = [
    "PropertyInfo",
    "ActionInfo",
    "DecoratorScanner",
    "_create_direct_property",
    "_create_delegated_property",
    "_is_frequently_accessed",
]
