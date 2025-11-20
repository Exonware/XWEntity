#!/usr/bin/env python3
"""
🔧 xEntity Internal Models
Internal components for entity management.
"""

from typing import Any, Dict, Optional, List, Union
from datetime import datetime
from enum import Enum
import uuid

from src.xlib.xdata import xData, xSchema
from src.xlib.xaction import xAction, ActionContext
from .errors import xEntityStateError, xEntityActionError


class EntityState(Enum):
    """Entity lifecycle states."""
    DRAFT = "draft"
    VALIDATED = "validated"
    COMMITTED = "committed"
    ARCHIVED = "archived"


class EntityMetadata:
    """Metadata for entity tracking."""
    
    def __init__(self, entity_type: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.type = entity_type or "entity"
        self.version = 1
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.state = EntityState.DRAFT
        self.tags: List[str] = []
        self.metadata: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "state": self.state.value,
            "tags": self.tags,
            "metadata": self.metadata
        }
    
    def update_version(self):
        """Increment version and update timestamp."""
        self.version += 1
        self.updated_at = datetime.now()


class EntityEngine:
    """
    Internal engine for xEntity operations.
    Manages the composition of schema, data, and actions.
    """
    
    def __init__(self, 
                 schema: Optional[xSchema] = None,
                 data: Optional[Union[Dict, xData]] = None,
                 entity_type: Optional[str] = None):
        # Core components
        self.schema = schema
        self.data = self._init_data(data)
        self.metadata = EntityMetadata(entity_type)
        self.actions: Dict[str, xAction] = {}
        
        # State validation rules
        self._state_transitions = {
            EntityState.DRAFT: [EntityState.VALIDATED, EntityState.ARCHIVED],
            EntityState.VALIDATED: [EntityState.COMMITTED, EntityState.DRAFT, EntityState.ARCHIVED],
            EntityState.COMMITTED: [EntityState.ARCHIVED],
            EntityState.ARCHIVED: [EntityState.DRAFT]  # Can restore to draft
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
    
    def validate(self) -> bool:
        """Validate data against schema."""
        if not self.schema:
            return True  # No schema means no validation
        
        return self.schema.validate_data(self.data.to_native())
    
    def can_transition_to(self, target_state: EntityState) -> bool:
        """Check if state transition is allowed."""
        current_state = self.metadata.state
        allowed_states = self._state_transitions.get(current_state, [])
        return target_state in allowed_states
    
    def transition_to(self, target_state: EntityState):
        """Transition to new state."""
        if not self.can_transition_to(target_state):
            raise xEntityStateError(
                self.metadata.state.value,
                target_state.value,
                "Transition not allowed"
            )
        
        # Additional validation for certain transitions
        if target_state == EntityState.VALIDATED:
            if not self.validate():
                raise xEntityStateError(
                    self.metadata.state.value,
                    target_state.value,
                    "Validation failed"
                )
        
        self.metadata.state = target_state
        self.metadata.update_version()
    
    def register_action(self, action):
        """Register an action for this entity."""
        # Handle both Action instances and decorated functions
        if hasattr(action, '_action_instance'):
            # This is a decorated function, use its api_name
            self.actions[action.api_name] = action
        elif hasattr(action, 'api_name'):
            # This is an Action instance
            self.actions[action.api_name] = action
        else:
            # Fallback: use function name
            self.actions[action.__name__] = action
    
    def execute_action(self, action_name: str, context: Any = None, **kwargs) -> Any:
        """Execute a registered action."""
        if action_name not in self.actions:
            raise xEntityActionError(action_name, "Action not registered")
        
        action = self.actions[action_name]
        
        # Handle both Action instances and decorated functions
        if hasattr(action, '_action_instance'):
            # This is a decorated function, use the action instance
            # Create context with admin roles for demonstration
            demo_context = ActionContext()
            demo_context.metadata = {"roles": ["admin", "manager", "editor", "user"]}
            return action._action_instance.execute(context=demo_context, instance=context, **kwargs)
        elif hasattr(action, 'execute'):
            # This is an Action instance
            # Create context with admin roles for demonstration
            demo_context = ActionContext()
            demo_context.metadata = {"roles": ["admin", "manager", "editor", "user"]}
            return action.execute(context=demo_context, instance=context, **kwargs)
        else:
            # Fallback: call the function directly
            return action(context, **kwargs)
    
    def to_dict(self) -> Dict[str, Any]:
        """Export entity as dictionary."""
        result = {
            "_metadata": self.metadata.to_dict(),
            "_data": self.data.to_native()
        }
        
        if self.schema:
            result["_schema"] = {
                "uri": self.schema.value,
                "version": getattr(self.schema, 'version', None)
            }
        
        if self.actions:
            result["_actions"] = {
                name: action.to_native() 
                for name, action in self.actions.items()
            }
        
        return result
    
    def from_dict(self, data: Dict[str, Any]):
        """Load entity from dictionary."""
        # Load metadata
        if "_metadata" in data:
            meta = data["_metadata"]
            self.metadata.id = meta.get("id", self.metadata.id)
            self.metadata.type = meta.get("type", self.metadata.type)
            self.metadata.version = meta.get("version", 1)
            self.metadata.state = EntityState(meta.get("state", "draft"))
            self.metadata.tags = meta.get("tags", [])
            self.metadata.metadata = meta.get("metadata", {})
        
        # Load data
        if "_data" in data:
            self.data = xData(data["_data"])
        
        # Note: Schema and actions would need to be re-registered 