#!/usr/bin/env python3
"""
🏗️ xEntity Metaclass Factory
Creates different xEntity implementations based on performance mode.
"""

import inspect
from typing import Any, Dict, Optional, List, Type, get_type_hints, get_origin, get_args
from functools import wraps

from .config import config_manager, PerformanceMode
from src.xlib.xdata.new_3.schema import xSchema
from src.xlib.xaction import xAction
from src.xlib.xsystem import get_logger

logger = get_logger(__name__)


class PropertyInfo:
    """Information about a discovered property."""
    
    def __init__(self, name: str, schema: Optional[xSchema] = None, 
                 property_type: Optional[Type] = None, default: Any = None):
        self.name = name
        self.schema = schema
        self.property_type = property_type
        
        # Use schema default if no explicit default provided
        if default is None and schema and getattr(schema, '_default', None) is not None:
            self.default = getattr(schema, '_default')
        else:
            self.default = default
            
        self.is_required = self.default is None


class ActionInfo:
    """Information about a discovered action."""
    
    def __init__(self, name: str, func: callable, action_instance: Optional[xAction] = None):
        self.name = name
        self.func = func
        self.action_instance = action_instance


class DecoratorScanner:
    """Scans class definitions for supported decorators."""
    
    @staticmethod
    def scan_properties(namespace: Dict[str, Any], annotations: Dict[str, Any]) -> List[PropertyInfo]:
        """Scan for property definitions using supported decorators."""
        properties = []
        
        # 1. Scan @xSchema decorated methods
        for name, attr in namespace.items():
            if hasattr(attr, '_schema') and hasattr(attr, '_is_schema_decorated'):
                # Extract schema from decorator
                original_schema = attr._schema
                
                # Auto-detect type from function annotation if not specified in schema
                func_annotation = getattr(attr, '__annotations__', {}).get('return', None)
                if func_annotation and (not hasattr(original_schema, 'type') or original_schema.type is None):
                    # Create new schema with inferred type
                    schema_params = {
                        'type': func_annotation,
                        'title': getattr(original_schema, 'title', None),
                        'description': getattr(original_schema, 'description', None),
                        'format': getattr(original_schema, 'format', None),
                        'enum': getattr(original_schema, 'enum', None),
                        'default': getattr(original_schema, 'default', None),
                        'nullable': getattr(original_schema, 'nullable', False),
                        'deprecated': getattr(original_schema, 'deprecated', False),
                        'confidential': getattr(original_schema, 'confidential', False),
                        'strict': getattr(original_schema, 'strict', False),
                        'alias': getattr(original_schema, 'alias', None),
                        'exclude': getattr(original_schema, 'exclude', False),
                        'pattern': getattr(original_schema, 'pattern', None),
                        'length_min': getattr(original_schema, 'length_min', None),
                        'length_max': getattr(original_schema, 'length_max', None),
                        'strip_whitespace': getattr(original_schema, 'strip_whitespace', False),
                        'to_upper': getattr(original_schema, 'to_upper', False),
                        'to_lower': getattr(original_schema, 'to_lower', False),
                        'value_min': getattr(original_schema, 'value_min', None),
                        'value_max': getattr(original_schema, 'value_max', None),
                        'value_min_exclusive': getattr(original_schema, 'value_min_exclusive', False),
                        'value_max_exclusive': getattr(original_schema, 'value_max_exclusive', False),
                        'value_multiple_of': getattr(original_schema, 'value_multiple_of', None),
                        'items': getattr(original_schema, 'items', None),
                        'items_min': getattr(original_schema, 'items_min', None),
                        'items_max': getattr(original_schema, 'items_max', None),
                        'items_unique': getattr(original_schema, 'items_unique', False),
                        'properties': getattr(original_schema, 'properties', None),
                        'required': getattr(original_schema, 'required', None),
                        'properties_additional': getattr(original_schema, 'properties_additional', None),
                        'properties_min': getattr(original_schema, 'properties_min', None),
                        'properties_max': getattr(original_schema, 'properties_max', None),
                    }
                    # Remove None values
                    schema_params = {k: v for k, v in schema_params.items() if v is not None}
                    schema = xSchema(**schema_params)
                    logger.debug(f"🔍 Auto-detected type {func_annotation} for {name}")
                else:
                    schema = original_schema
                
                # Extract default from schema
                default_value = getattr(schema, '_default', None)
                properties.append(PropertyInfo(name, schema=schema, default=default_value))
                logger.debug(f"🔍 Found @xSchema property: {name} (type: {getattr(schema, 'type', 'None')}, default: {default_value})")
        
        # 2. Scan @property decorated methods with type hints
        for name, attr in namespace.items():
            if isinstance(attr, property):
                schema = DecoratorScanner._convert_property_to_xschema(attr, name)
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found @property: {name} -> auto-converted to xSchema")
        
        # 3. Scan Annotated type hints (excluding simple type hints as requested)
        for name, annotation in annotations.items():
            if DecoratorScanner._is_annotated(annotation):
                schema = DecoratorScanner._extract_schema_from_annotated(annotation)
                default_value = namespace.get(name)  # Get the default value from namespace
                if schema:
                    # Update schema with default if found
                    if default_value is not None and getattr(schema, '_default', None) is None:
                        schema._default = default_value
                    properties.append(PropertyInfo(name, schema=schema, default=default_value))
                    logger.debug(f"🔍 Found Annotated property: {name} (default: {default_value})")
            
            # Also check for dataclass field
            elif name in namespace:
                attr = namespace[name]
                if hasattr(attr, 'metadata') and hasattr(attr, 'default'):
                    schema = DecoratorScanner._convert_dataclass_field_to_xschema(attr, name, annotation)
                    if schema:
                        properties.append(PropertyInfo(name, schema=schema, default=attr.default))
                        logger.debug(f"🔍 Found dataclass field: {name} (default: {attr.default})")
        
        # 4. Scan library-specific decorators (Pydantic, SQLAlchemy, etc.)
        properties.extend(DecoratorScanner._scan_library_decorators(namespace, annotations))
        
        return properties
    
    @staticmethod
    def scan_actions(namespace: Dict[str, Any]) -> List[ActionInfo]:
        """Scan for action methods using @xAction decorator."""
        actions = []
        
        for name, attr in namespace.items():
            if hasattr(attr, '_is_action') and attr._is_action:
                action_instance = getattr(attr, '_action_instance', None)
                actions.append(ActionInfo(name, attr, action_instance))
                logger.debug(f"🔍 Found @xAction: {name}")
        
        return actions
    
    @staticmethod
    def _is_annotated(annotation: Any) -> bool:
        """Check if annotation uses Annotated."""
        return get_origin(annotation) is not None and hasattr(annotation, '__metadata__')
    
    @staticmethod
    def _extract_schema_from_annotated(annotation: Any) -> Optional[xSchema]:
        """Extract xSchema from Annotated type hint."""
        if not DecoratorScanner._is_annotated(annotation):
            return None
        
        # Get base type
        base_type = get_args(annotation)[0] if get_args(annotation) else str
        metadata = getattr(annotation, '__metadata__', ())
        
        # Look for existing xSchema instance
        for item in metadata:
            if isinstance(item, xSchema):
                return item
        
        # Create xSchema from metadata
        schema_params = {'type': base_type}
        
        for item in metadata:
            if isinstance(item, dict):
                # Convert dict constraints to xSchema parameters
                schema_params.update(item)
            elif isinstance(item, str):
                # Use string as description
                schema_params['description'] = item
        
        # Only create schema if we have meaningful metadata
        if len(schema_params) > 1:  # More than just type
            return xSchema(**schema_params)
        
        return None
    
    @staticmethod
    def _scan_library_decorators(namespace: Dict[str, Any], annotations: Dict[str, Any]) -> List[PropertyInfo]:
        """Scan for supported library decorators."""
        properties = []
        
        for name, attr in namespace.items():
            # Pydantic FieldInfo detection (real Pydantic Field)
            if str(type(attr)).find('FieldInfo') != -1 or hasattr(attr, 'annotation'):
                schema = DecoratorScanner._convert_pydantic_fieldinfo_to_xschema(attr, name, annotations.get(name))
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found Pydantic FieldInfo: {name}")
            
            # @Field decorator detection (mock Field)
            elif hasattr(attr, '_field_info'):
                schema = DecoratorScanner._convert_field_to_xschema(attr, name)
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found @Field decorator: {name}")
            
            # attrs field detection
            elif hasattr(attr, '_attrs_field') or (hasattr(attr, 'metadata') and hasattr(attr, 'default') and hasattr(attr, 'validator')):
                schema = DecoratorScanner._convert_attrs_to_xschema(attr, name)
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found attrs field: {name}")
            
            # marshmallow field detection  
            elif hasattr(attr, '_marshmallow_field') or str(type(attr)).find('marshmallow') != -1:
                schema = DecoratorScanner._convert_marshmallow_to_xschema(attr, name)
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found marshmallow field: {name}")
            
            # SQLAlchemy Column detection
            elif hasattr(attr, '_sqlalchemy_column') or (hasattr(attr, 'type') and str(type(attr)).find('sqlalchemy') != -1):
                schema = DecoratorScanner._convert_sqlalchemy_to_xschema(attr, name)
                if schema:
                    properties.append(PropertyInfo(name, schema=schema))
                    logger.debug(f"🔍 Found SQLAlchemy column: {name}")
            
            # Add more library detections here...
        
        return properties
    
    @staticmethod
    def _convert_property_to_xschema(prop: property, name: str) -> Optional[xSchema]:
        """Convert @property decorator to xSchema."""
        try:
            # Extract type from property getter if available
            prop_type = str
            description = f"Property {name}"
            
            if prop.fget and hasattr(prop.fget, '__annotations__'):
                return_type = prop.fget.__annotations__.get('return')
                if return_type:
                    prop_type = return_type
            
            # Extract description from docstring
            if prop.fget and prop.fget.__doc__:
                description = prop.fget.__doc__.strip()
            
            return xSchema(
                type=prop_type,
                description=description
            )
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert @property {name}: {e}")
            return None
    
    @staticmethod
    def _convert_field_to_xschema(field_func, name: str) -> Optional[xSchema]:
        """Convert @Field decorator to xSchema."""
        try:
            field_info = getattr(field_func, '_field_info', {})
            
            # Extract type from function annotation
            field_type = str
            if hasattr(field_func, '__annotations__'):
                return_type = field_func.__annotations__.get('return')
                if return_type:
                    field_type = return_type
            
            # Map common Field parameters to xSchema parameters
            schema_params = {'type': field_type}
            
            if 'description' in field_info:
                schema_params['description'] = field_info['description']
            
            if 'pattern' in field_info:
                schema_params['pattern'] = field_info['pattern']
            elif 'regex' in field_info:  # Handle older Pydantic versions
                schema_params['pattern'] = field_info['regex']
            
            if 'min_length' in field_info:
                schema_params['length_min'] = field_info['min_length']
            if 'max_length' in field_info:
                schema_params['length_max'] = field_info['max_length']
            
            if 'gt' in field_info:
                schema_params['value_min_exclusive'] = field_info['gt']
            if 'ge' in field_info:
                schema_params['value_min'] = field_info['ge']
            if 'lt' in field_info:
                schema_params['value_max_exclusive'] = field_info['lt']
            if 'le' in field_info:
                schema_params['value_max'] = field_info['le']
            
            if 'default' in field_info:
                schema_params['default'] = field_info['default']
            
            return xSchema(**schema_params)
            
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert @Field {name}: {e}")
            return None
    
    @staticmethod
    def _convert_attrs_to_xschema(attr, name: str) -> Optional[xSchema]:
        """Convert attrs field to xSchema."""
        try:
            schema_params = {'type': str}  # Default type
            
            # Extract from metadata
            if hasattr(attr, 'metadata') and attr.metadata:
                metadata = attr.metadata
                if 'description' in metadata:
                    schema_params['description'] = metadata['description']
            
            # Extract default
            if hasattr(attr, 'default') and attr.default is not None:
                schema_params['default'] = attr.default
            
            schema_params['description'] = schema_params.get('description', f"attrs field: {name}")
            
            return xSchema(**schema_params)
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert attrs field {name}: {e}")
            return None
    
    @staticmethod
    def _convert_dataclass_field_to_xschema(field, name: str, annotation) -> Optional[xSchema]:
        """Convert dataclass field to xSchema."""
        try:
            # Extract base type from annotation
            field_type = annotation if annotation else str
            schema_params = {'type': field_type}
            
            # Extract from metadata
            if hasattr(field, 'metadata') and field.metadata:
                metadata = field.metadata
                for key, value in metadata.items():
                    if key in ['description', 'length_min', 'length_max', 'value_min', 'value_max', 'pattern']:
                        schema_params[key] = value
            
            # Extract default
            if hasattr(field, 'default') and field.default is not None:
                schema_params['default'] = field.default
            
            schema_params['description'] = schema_params.get('description', f"dataclass field: {name}")
            
            return xSchema(**schema_params)
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert dataclass field {name}: {e}")
            return None
    
    @staticmethod
    def _convert_marshmallow_to_xschema(field, name: str) -> Optional[xSchema]:
        """Convert marshmallow field to xSchema."""
        try:
            schema_params = {'type': str}  # Default type
            
            # Extract from metadata
            if hasattr(field, 'metadata') and field.metadata:
                metadata = field.metadata
                if 'description' in metadata:
                    schema_params['description'] = metadata['description']
            
            # Extract default/missing/load_default
            if hasattr(field, 'load_default') and field.load_default is not None:
                schema_params['default'] = field.load_default
            elif hasattr(field, 'missing') and field.missing is not None:
                schema_params['default'] = field.missing
            
            schema_params['description'] = schema_params.get('description', f"marshmallow field: {name}")
            
            return xSchema(**schema_params)
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert marshmallow field {name}: {e}")
            return None
    
    @staticmethod
    def _convert_sqlalchemy_to_xschema(column, name: str) -> Optional[xSchema]:
        """Convert SQLAlchemy column to xSchema."""
        try:
            schema_params = {}
            
            # Extract type
            if hasattr(column, 'type'):
                if column.type == int:
                    schema_params['type'] = int
                elif column.type == str:
                    schema_params['type'] = str
                else:
                    schema_params['type'] = str  # Default
            
            # Extract default
            if hasattr(column, 'default') and column.default is not None:
                schema_params['default'] = column.default
            
            # Extract nullable
            if hasattr(column, 'nullable'):
                schema_params['nullable'] = column.nullable
            
            schema_params['description'] = f"SQLAlchemy column: {name}"
            
            return xSchema(**schema_params)
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert SQLAlchemy column {name}: {e}")
            return None
    
    @staticmethod
    def _convert_pydantic_fieldinfo_to_xschema(field_info, name: str, annotation) -> Optional[xSchema]:
        """Convert Pydantic FieldInfo to xSchema."""
        try:
            # Extract base type from annotation
            field_type = annotation if annotation else str
            schema_params = {'type': field_type}
            
            # Extract properties from FieldInfo
            if hasattr(field_info, 'description') and field_info.description:
                schema_params['description'] = field_info.description
            
            if hasattr(field_info, 'default') and field_info.default is not None:
                schema_params['default'] = field_info.default
            
            # Handle constraints
            constraints = getattr(field_info, 'constraints', [])
            for constraint in constraints:
                constraint_type = type(constraint).__name__
                if constraint_type == 'Ge':
                    schema_params['value_min'] = constraint.ge
                elif constraint_type == 'Le':
                    schema_params['value_max'] = constraint.le
                elif constraint_type == 'Gt':
                    schema_params['value_min_exclusive'] = constraint.gt
                elif constraint_type == 'Lt':
                    schema_params['value_max_exclusive'] = constraint.lt
                elif constraint_type == 'Pattern':
                    schema_params['pattern'] = constraint.pattern
                elif constraint_type == 'MultipleOf':
                    schema_params['value_multiple_of'] = constraint.multiple_of
            
            # Handle direct attributes (newer Pydantic)
            for attr_name in ['ge', 'le', 'gt', 'lt', 'multiple_of', 'pattern']:
                if hasattr(field_info, attr_name):
                    value = getattr(field_info, attr_name)
                    if value is not None:
                        if attr_name == 'ge':
                            schema_params['value_min'] = value
                        elif attr_name == 'le':
                            schema_params['value_max'] = value
                        elif attr_name == 'gt':
                            schema_params['value_min_exclusive'] = value
                        elif attr_name == 'lt':
                            schema_params['value_max_exclusive'] = value
                        elif attr_name == 'multiple_of':
                            schema_params['value_multiple_of'] = value
                        elif attr_name == 'pattern':
                            schema_params['pattern'] = value
            
            if 'description' not in schema_params:
                schema_params['description'] = f"Pydantic field: {name}"
            
            return xSchema(**schema_params)
            
        except Exception as e:
            logger.debug(f"⚠️ Failed to convert Pydantic FieldInfo {name}: {e}")
            return None
    
    @staticmethod
    def _convert_pydantic_to_xschema(field) -> Optional[xSchema]:
        """Convert Pydantic field to xSchema."""
        try:
            # Basic conversion - can be expanded
            return xSchema(
                type=str,  # Default type
                description=f"Pydantic field: {field}"
            )
        except Exception:
            return None


class PerformanceModeMetaclass(type):
    """Metaclass that creates performance-optimized xEntity (Option A)."""
    
    def __new__(cls, name, bases, namespace):
        # Scan for decorators
        annotations = namespace.get('__annotations__', {})
        properties = DecoratorScanner.scan_properties(namespace, annotations)
        actions = DecoratorScanner.scan_actions(namespace)
        
        # Register with config manager
        effective_mode = config_manager.register_entity_creation(
            type(name, (), {}), len(properties)
        )
        
        # Create direct property accessors (Option A)
        for prop in properties:
            cls._create_direct_property(namespace, prop)
        
        # Store metadata
        namespace['_xentity_properties'] = properties
        namespace['_xentity_actions'] = actions
        namespace['_xentity_mode'] = PerformanceMode.PERFORMANCE
        
        logger.debug(f"🚀 Created Performance xEntity: {name} with {len(properties)} properties")
        return super().__new__(cls, name, bases, namespace)
    
    @staticmethod
    def _create_direct_property(namespace: Dict[str, Any], prop: PropertyInfo):
        """Create direct property accessor for performance."""
        private_name = f"_{prop.name}"
        
        def getter(self):
            return getattr(self, private_name, prop.default)
        
        def setter(self, value):
            # Validate using schema if available (temporarily disabled due to xSchema bug)
            # TODO: Re-enable once xSchema validation bug is fixed (value_min=0 becomes False)
            # if prop.schema and config_manager.config.enable_validation:
            #     if not prop.schema.validate(value):
            #         raise ValueError(f"Validation failed for {prop.name}: {value}")
            setattr(self, private_name, value)
        
        # Create property
        namespace[prop.name] = property(getter, setter)


class MemoryModeMetaclass(type):
    """Metaclass that creates memory-optimized xEntity (Option C)."""
    
    def __new__(cls, name, bases, namespace):
        # Scan for decorators
        annotations = namespace.get('__annotations__', {})
        properties = DecoratorScanner.scan_properties(namespace, annotations)
        actions = DecoratorScanner.scan_actions(namespace)
        
        # Create xData-delegated properties (Option C)
        for prop in properties:
            cls._create_delegated_property(namespace, prop)
        
        # Store metadata
        namespace['_xentity_properties'] = properties
        namespace['_xentity_actions'] = actions
        namespace['_xentity_mode'] = PerformanceMode.MEMORY
        
        logger.debug(f"💾 Created Memory xEntity: {name} with {len(properties)} properties")
        return super().__new__(cls, name, bases, namespace)
    
    @staticmethod
    def _create_delegated_property(namespace: Dict[str, Any], prop: PropertyInfo):
        """Create xData-delegated property for memory efficiency."""
        
        def getter(self):
            return self.data.get(prop.name, prop.default)
        
        def setter(self, value):
            # Validate using schema if available
            if prop.schema and config_manager.config.enable_validation:
                if not prop.schema.validate(value):
                    raise ValueError(f"Validation failed for {prop.name}: {value}")
            self.data.set(prop.name, value)
        
        # Create property
        namespace[prop.name] = property(getter, setter)


class BalancedModeMetaclass(type):
    """Metaclass that creates balanced xEntity (hybrid approach)."""
    
    def __new__(cls, name, bases, namespace):
        # Scan for decorators
        annotations = namespace.get('__annotations__', {})
        properties = DecoratorScanner.scan_properties(namespace, annotations)
        actions = DecoratorScanner.scan_actions(namespace)
        
        # Use performance for frequently accessed, memory for others
        for prop in properties:
            if cls._is_frequently_accessed(prop):
                PerformanceModeMetaclass._create_direct_property(namespace, prop)
            else:
                MemoryModeMetaclass._create_delegated_property(namespace, prop)
        
        # Store metadata
        namespace['_xentity_properties'] = properties
        namespace['_xentity_actions'] = actions
        namespace['_xentity_mode'] = PerformanceMode.BALANCED
        
        logger.debug(f"⚖️ Created Balanced xEntity: {name} with {len(properties)} properties")
        return super().__new__(cls, name, bases, namespace)
    
    @staticmethod
    def _is_frequently_accessed(prop: PropertyInfo) -> bool:
        """Determine if property is frequently accessed (heuristic)."""
        # Simple heuristic - can be made more sophisticated
        frequent_names = {'id', 'name', 'username', 'email', 'status', 'active'}
        return prop.name.lower() in frequent_names


def create_xentity_metaclass() -> type:
    """Factory function that returns appropriate metaclass based on config."""
    mode = config_manager.config.performance_mode
    
    if mode == PerformanceMode.PERFORMANCE:
        return PerformanceModeMetaclass
    elif mode == PerformanceMode.MEMORY:
        return MemoryModeMetaclass
    elif mode == PerformanceMode.BALANCED:
        return BalancedModeMetaclass
    else:  # AUTO mode
        # For AUTO, we'll decide at entity creation time
        # For now, default to performance
        return PerformanceModeMetaclass


# Export the current metaclass
xEntityMetaclass = create_xentity_metaclass()
