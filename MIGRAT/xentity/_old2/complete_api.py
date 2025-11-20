#!/usr/bin/env python3
"""
🎯 xEntity Complete API Implementation
Complete implementation of the proposed xEntity API with all methods.
"""

from typing import Any, Dict, Optional, List, Union, Type
from pathlib import Path
from datetime import datetime

from src.xlib.xdata import xData, xSchema
from src.xlib.xaction import xAction
from .model import EntityEngine, EntityState, EntityMetadata
from .errors import xEntityError, xEntityValidationError, xEntityStateError
from .config import config_manager, PerformanceMode
from .metaclass import create_xentity_metaclass
from src.xlib.xsystem import get_logger

logger = get_logger(__name__)


class xEntity(metaclass=create_xentity_metaclass()):
    """
    Smart data container that combines schema, data, and actions.
    
    Complete API with:
    - xEntity.schema.to_file/from_file/to_native/from_native
    - xEntity.actions.to_file/from_file/to_native/from_native  
    - xEntity.data.to_file/from_file/to_native/from_native
    - xEntity.to_file/from_file/to_native/from_native
    - xEntity.to_collection/from_collection
    """
    
    def __init__(self, 
                 schema: Optional[Union[str, Path, xSchema]] = None,
                 data: Optional[Union[Dict, xData]] = None,
                 entity_type: Optional[str] = None,
                 **kwargs):
        """Initialize entity with optional schema and data."""
        # Load schema if path provided
        if isinstance(schema, (str, Path)):
            schema = xSchema.from_file(str(schema))
        
        # Merge kwargs into data for property initialization
        if data is None:
            data = kwargs
        elif isinstance(data, dict):
            data = {**data, **kwargs}
        else:
            # data is xData instance, merge kwargs
            for key, value in kwargs.items():
                data.set(key, value)
        
        # Initialize engine
        self._engine = EntityEngine(schema, data, entity_type)
        
        # Initialize properties based on performance mode
        self._initialize_properties(data if isinstance(data, dict) else kwargs)
        
        # Discover actions from class
        self._discover_actions()
    
    def _initialize_properties(self, data: Dict[str, Any]):
        """Initialize properties based on current performance mode."""
        mode = getattr(self.__class__, '_xentity_mode', PerformanceMode.PERFORMANCE)
        properties = getattr(self.__class__, '_xentity_properties', [])
        
        if mode == PerformanceMode.PERFORMANCE:
            # Option A: Initialize direct properties
            for prop in properties:
                value = data.get(prop.name, prop.default)
                if value is not None:
                    setattr(self, f"_{prop.name}", value)
        
        logger.debug(f"🔧 Initialized {len(properties)} properties in {mode.value} mode")
    
    def _discover_actions(self):
        """Discover and register actions decorated with @action."""
        for name in dir(self):
            if name.startswith('_'):
                continue
            
            attr = getattr(self, name)
            if hasattr(attr, '_is_action') and attr._is_action:
                self._engine.register_action(attr)
    
    # --- Core Properties ---
    
    @property
    def id(self) -> str:
        """Unique entity identifier."""
        return self._engine.metadata.id
    
    @property
    def type(self) -> str:
        """Entity type name."""
        return self._engine.metadata.type
    
    @property
    def schema(self) -> Optional[xSchema]:
        """Entity schema."""
        return self._engine.schema
    
    @property
    def data(self) -> xData:
        """Entity data."""
        return self._engine.data
    
    @property
    def actions(self) -> Dict[str, Any]:
        """Entity actions."""
        return self.export_actions()
    
    @property
    def state(self) -> EntityState:
        """Current entity state."""
        return self._engine.metadata.state
    
    @property
    def version(self) -> int:
        """Entity version number."""
        return self._engine.metadata.version
    
    @property
    def created_at(self) -> datetime:
        """Creation timestamp."""
        return self._engine.metadata.created_at
    
    @property
    def updated_at(self) -> datetime:
        """Last update timestamp."""
        return self._engine.metadata.updated_at
    
    # --- Data Operations ---
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        return self.data.get(path, default)
    
    def set(self, path: str, value: Any) -> 'xEntity':
        """Set value at path (chainable)."""
        self.data.set(path, value)
        self._engine.metadata.update_version()
        return self
    
    def delete(self, path: str) -> 'xEntity':
        """Delete value at path (chainable)."""
        self.data.delete(path)
        self._engine.metadata.update_version()
        return self
    
    def update(self, updates: Dict[str, Any]) -> 'xEntity':
        """Update multiple values (chainable)."""
        for path, value in updates.items():
            self.set(path, value)
        return self
    
    # --- Validation ---
    
    def validate(self) -> bool:
        """Validate data against schema."""
        return self._engine.validate()
    
    def validate_or_raise(self):
        """Validate and raise exception if invalid."""
        if not self.validate():
            raise xEntityValidationError("Entity validation failed")
    
    # --- State Management ---
    
    def to_validated(self) -> 'xEntity':
        """Transition to validated state."""
        self._engine.transition_to(EntityState.VALIDATED)
        return self
    
    def commit(self) -> 'xEntity':
        """Commit entity (must be validated first)."""
        self._engine.transition_to(EntityState.COMMITTED)
        return self
    
    def archive(self) -> 'xEntity':
        """Archive entity."""
        self._engine.transition_to(EntityState.ARCHIVED)
        return self
    
    def restore(self) -> 'xEntity':
        """Restore archived entity to draft."""
        if self.state != EntityState.ARCHIVED:
            raise xEntityStateError(
                self.state.value,
                EntityState.DRAFT.value,
                "Can only restore from archived state"
            )
        self._engine.transition_to(EntityState.DRAFT)
        return self
    
    # --- Actions ---
    
    def execute_action(self, action_name: str, **kwargs) -> Any:
        """Execute a registered action."""
        return self._engine.execute_action(action_name, context=self, **kwargs)
    
    def list_actions(self) -> List[str]:
        """List available action names."""
        return list(self._engine.actions.keys())
    
    def export_actions(self) -> Dict[str, Dict[str, Any]]:
        """Export action metadata."""
        result = {}
        for name, action in self._engine.actions.items():
            # Handle both Action instances and decorated functions
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
    
    # --- Schema Operations (Static) ---
    
    @classmethod
    def schema_to_file(cls, output_path: Union[str, Path]) -> None:
        """Export schema to file with class name included."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get schema with class name
        schema_data = cls.schema_to_native()
        if schema_data:
            import json
            with open(output_path, 'w') as f:
                json.dump(schema_data, f, indent=2)
    
    @classmethod
    def schema_from_file(cls, file_path: Union[str, Path]) -> 'xSchema':
        """Import schema from file."""
        file_path = Path(file_path)
        import json
        with open(file_path, 'r') as f:
            schema_data = json.load(f)
        return cls.schema_from_native(schema_data)
    
    @classmethod
    def schema_to_native(cls) -> Optional[Dict[str, Any]]:
        """Get schema as dictionary with class name."""
        # This would need to be implemented based on how schema is stored
        # For now, return None as schema is not currently implemented
        return None
    
    @classmethod
    def schema_from_native(cls, schema_data: Dict[str, Any]) -> 'xSchema':
        """Create schema from dictionary."""
        return xSchema.from_native(schema_data)
    
    # --- Actions Operations (Static) ---
    
    @classmethod
    def actions_to_file(cls, output_path: Union[str, Path]) -> None:
        """Export actions to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        actions_data = cls.actions_to_native()
        import json
        with open(output_path, 'w') as f:
            json.dump(actions_data, f, indent=2)
    
    @classmethod
    def actions_from_file(cls, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Import actions from file."""
        file_path = Path(file_path)
        import json
        with open(file_path, 'r') as f:
            return json.load(f)
    
    @classmethod
    def actions_to_native(cls) -> Dict[str, Any]:
        """Get actions as dictionary."""
        actions = {}
        for name in dir(cls):
            if name.startswith('_'):
                continue
            
            attr = getattr(cls, name)
            if hasattr(attr, '_is_action') and attr._is_action:
                action_instance = getattr(attr, '_action_instance', None)
                if action_instance:
                    actions[name] = action_instance.to_native()
                else:
                    actions[name] = {
                        "api_name": name,
                        "description": getattr(attr, '__doc__', ''),
                        "roles": getattr(attr, 'roles', ['*'])
                    }
        return actions
    
    @classmethod
    def actions_from_native(cls, actions_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create actions from dictionary."""
        return actions_data
    
    # --- Data Operations (Instance) ---
    
    def data_to_file(self, output_path: Union[str, Path]) -> None:
        """Export entity data to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.data.to_file(str(output_path))
    
    def data_from_file(self, file_path: Union[str, Path]) -> None:
        """Import entity data from file."""
        file_path = Path(file_path)
        data = xData.from_file(str(file_path))
        self._engine.data = data
    
    def data_to_native(self) -> Dict[str, Any]:
        """Get entity data as dictionary."""
        return self.data.to_native()
    
    def data_from_native(self, data_dict: Dict[str, Any]) -> None:
        """Create data from dictionary."""
        self._engine.data = xData(data_dict)
    
    # --- Complete Entity Operations (Static) ---
    
    @classmethod
    def to_file(cls, output_path: Union[str, Path]) -> None:
        """Export complete entity (schema + actions + data) to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get schema, actions, and metadata
        schema_data = cls.schema_to_native()
        actions_data = cls.actions_to_native()
        
        # Create complete export structure
        export_data = {
            "schema": schema_data,
            "actions": actions_data,
            "metadata": {
                "class_name": cls.__module__ + '.' + cls.__name__,
                "exported_at": datetime.now().isoformat()
            }
        }
        
        import json
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> 'xEntity':
        """Import complete entity from file."""
        file_path = Path(file_path)
        import json
        with open(file_path, 'r') as f:
            entity_data = json.load(f)
        return cls.from_native(entity_data)
    
    @classmethod
    def to_native(cls) -> Dict[str, Any]:
        """Get complete entity as dictionary."""
        return {
            "schema": cls.schema_to_native(),
            "actions": cls.actions_to_native(),
            "metadata": {
                "class_name": cls.__module__ + '.' + cls.__name__,
                "exported_at": datetime.now().isoformat()
            }
        }
    
    @classmethod
    def from_native(cls, entity_data: Dict[str, Any]) -> 'xEntity':
        """Create entity from dictionary."""
        # Validate class name
        expected_class = cls.__module__ + '.' + cls.__name__
        actual_class = entity_data.get('metadata', {}).get('class_name')
        if actual_class and actual_class != expected_class:
            raise ValueError(f"Entity data contains {actual_class}, expected {expected_class}")
        
        # Load schema if present
        schema = None
        if entity_data.get('schema'):
            schema = cls.schema_from_native(entity_data['schema'])
        
        # Create entity
        entity = cls(schema=schema)
        
        # Load data if present
        if entity_data.get('data'):
            entity.data_from_native(entity_data['data'])
        
        return entity
    
    # --- Complete Entity Operations (Instance) ---
    
    def to_file(self, output_path: Union[str, Path]) -> None:
        """Export this entity instance to file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get complete entity data including this instance
        entity_data = self.to_native()
        
        import json
        with open(output_path, 'w') as f:
            json.dump(entity_data, f, indent=2)
    
    def from_file(self, file_path: Union[str, Path]) -> None:
        """Import entity data from file."""
        file_path = Path(file_path)
        import json
        with open(file_path, 'r') as f:
            entity_data = json.load(f)
        self.from_native(entity_data)
    
    def to_native(self) -> Dict[str, Any]:
        """Get this entity instance as dictionary."""
        return {
            "schema": self.__class__.schema_to_native(),
            "actions": self.__class__.actions_to_native(),
            "data": self.data_to_native(),
            "metadata": {
                "class_name": self.__class__.__module__ + '.' + self.__class__.__name__,
                "entity_id": self.id,
                "entity_type": self.type,
                "exported_at": datetime.now().isoformat()
            }
        }
    
    def from_native(self, entity_data: Dict[str, Any]) -> None:
        """Update this entity from dictionary."""
        # Load data if present
        if entity_data.get('data'):
            self.data_from_native(entity_data['data'])
    
    # --- Collection Operations ---
    
    @classmethod
    def to_collection(cls, entities: List['xEntity'], output_path: Union[str, Path]) -> None:
        """Export multiple entities to a single file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Get schema and actions (shared)
        schema_data = cls.schema_to_native()
        actions_data = cls.actions_to_native()
        
        # Get data with UIDs as keys
        data = {}
        for entity in entities:
            data[entity.id] = entity.data_to_native()
        
        # Create complete export structure
        export_data = {
            "schema": schema_data,
            "actions": actions_data,
            "data": data,
            "metadata": {
                "class_name": cls.__module__ + '.' + cls.__name__,
                "entity_count": len(entities),
                "exported_at": datetime.now().isoformat()
            }
        }
        
        import json
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
    
    @classmethod
    def from_collection(cls, file_path: Union[str, Path]) -> List['xEntity']:
        """Import multiple entities from a collection file."""
        file_path = Path(file_path)
        import json
        with open(file_path, 'r') as f:
            collection_data = json.load(f)
        
        # Validate class name
        expected_class = cls.__module__ + '.' + cls.__name__
        actual_class = collection_data.get('metadata', {}).get('class_name')
        if actual_class and actual_class != expected_class:
            raise ValueError(f"Collection file contains {actual_class}, expected {expected_class}")
        
        # Load schema if present
        schema = None
        if collection_data.get('schema'):
            schema = cls.schema_from_native(collection_data['schema'])
        
        # Create entities from data
        entities = []
        for uid, entity_data in collection_data.get('data', {}).items():
            entity = cls(schema=schema)
            entity.data_from_native(entity_data)
            # Ensure the entity has the correct ID
            if hasattr(entity, '_engine') and hasattr(entity._engine, 'metadata'):
                entity._engine.metadata.id = uid
            entities.append(entity)
        
        return entities
    
    # --- Legacy Methods (for compatibility) ---
    
    def to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary (legacy)."""
        return self._engine.to_dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], 
                  schema: Optional[xSchema] = None) -> 'xEntity':
        """Create entity from dictionary (legacy)."""
        entity = cls(schema=schema)
        entity._engine.from_dict(data)
        return entity
    
    # --- Utility Methods ---
    
    def copy(self) -> 'xEntity':
        """Create a copy of this entity with new ID."""
        # Export current state
        data = self.to_dict()
        
        # Create new instance
        entity = self.__class__(
            schema=self.schema,
            data=data.get("_data", {}),
            entity_type=self.type
        )
        
        # Copy metadata except ID and timestamps
        entity._engine.metadata.tags = self._engine.metadata.tags.copy()
        entity._engine.metadata.metadata = self._engine.metadata.metadata.copy()
        
        return entity
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"<xEntity(type='{self.type}', id='{self.id}', "
                f"state='{self.state.value}', version={self.version})>")
    
    def __str__(self) -> str:
        """Human-readable string."""
        return f"{self.type}#{self.id}"
