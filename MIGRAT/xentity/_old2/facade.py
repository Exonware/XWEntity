#!/usr/bin/env python3
"""
🎯 xEntity Facade
Clean, simple interface for entity management with configurable performance modes.
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
from src.xlib.xwsystem import get_logger

logger = get_logger(__name__)


class xEntity(metaclass=create_xentity_metaclass()):
    """
    Smart data container that combines schema, data, and actions.
    
    This class provides:
    - Schema-based validation
    - Stateful lifecycle management
    - Action discovery and execution
    - Clean serialization
    """
    
    def __init__(self, 
                 schema: Optional[Union[str, Path, xSchema]] = None,
                 data: Optional[Union[Dict, xData]] = None,
                 entity_type: Optional[str] = None,
                 **kwargs):
        """
        Initialize entity with optional schema and data.
        
        Args:
            schema: Schema definition (file path, xSchema instance, or None)
            data: Initial data (dict, xData instance, or None)  
            entity_type: Type name for this entity (e.g., "user", "product")
            **kwargs: Property values for decorator-defined properties
        """
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
        
        # For memory mode (Option C), properties delegate to self.data
        # so no initialization needed
        
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
    
    # --- Serialization ---
    
    def to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        return self._engine.to_dict()
    
    def to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """Save entity to file."""
        data = self.to_dict()
        xData(data).to_file(str(path), format_hint=format)
        return True
    
    @classmethod
    def export_schema_and_actions(cls, output_dir: Union[str, Path] = 'output') -> None:
        """Export schema and actions (static class-level data)."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export schema
        if hasattr(cls, 'schema') and cls.schema:
            cls.schema.to_file(output_dir / f'{cls.__name__.lower()}_schema.json')
        
        # Export actions (from class, not instance)
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
        
        import json
        with open(output_dir / f'{cls.__name__.lower()}_actions.json', 'w') as f:
            json.dump(actions, f, indent=2)
    
    def export_data(self, output_dir: Union[str, Path] = 'output') -> None:
        """Export entity data (instance-specific data)."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export data
        self.to_file(output_dir / f'{self.type}_{self.id}_data.json')
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], 
                  schema: Optional[xSchema] = None) -> 'xEntity':
        """Create entity from dictionary."""
        entity = cls(schema=schema)
        entity._engine.from_dict(data)
        return entity
    
    @classmethod
    def from_file(cls, path: Union[str, Path], 
                  schema: Optional[xSchema] = None) -> 'xEntity':
        """Load entity from file."""
        from src.xlib.xdata.facade import xDataFacade
        data = xDataFacade.from_file(str(path), format_hint=None).to_native()
        return cls.from_dict(data, schema)
    
    # --- Factory Methods ---
    
    @classmethod
    def from_schema(cls, schema: Union[str, Path, xSchema], 
                    initial_data: Optional[Dict] = None) -> 'xEntity':
        """Create entity with schema and optional initial data."""
        return cls(schema=schema, data=initial_data)
    
    @classmethod
    def from_data(cls, data: Union[Dict, xData], 
                  schema: Optional[xSchema] = None) -> 'xEntity':
        """Create entity with data and optional schema."""
        return cls(schema=schema, data=data)
    
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