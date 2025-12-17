#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/facade.py

XWEntity Facade - Main Public API

This module provides the main public API for the xwentity library,
implementing the facade pattern to hide complexity and provide
a clean, intuitive interface.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""

from typing import Any, Optional, Union
from pathlib import Path
from datetime import datetime

from exonware.xwsystem import get_logger

from .base import AEntity, EntityMetadata
from .contracts import IEntity
from .defs import EntityState, EntityID, EntityType, EntityData
from .errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
)
from .config import XWEntityConfig, get_config

logger = get_logger(__name__)


# ==============================================================================
# XWENTITY - MAIN FACADE CLASS
# ==============================================================================

class XWEntity(AEntity):
    """
    Main XWEntity class providing a unified interface for entity operations.
    
    This class implements the facade pattern, composing:
    - XWSchema for validation
    - List[XWAction] for actions
    - XWData (using XWNode) for data storage
    
    XWData is configured with XWNode strategies (node_mode, edge_mode,
    graph_manager_enabled, etc.) as specified in the configuration.
    """
    
    def __init__(
        self,
        schema: Optional[Any] = None,  # XWSchema type
        data: Optional[Union[Dict, Any]] = None,  # XWData type or dict
        actions: Optional[list[Any]] = None,  # List[XWAction] type
        entity_type: Optional[str] = None,
        config: Optional[XWEntityConfig] = None,
        # XWNode configuration options
        node_mode: Optional[str] = None,
        edge_mode: Optional[str] = None,
        graph_manager_enabled: Optional[bool] = None,
        **node_options
    ):
        """
        Initialize XWEntity with composition of schema, actions, and data.
        
        Args:
            schema: Optional XWSchema instance
            data: Optional initial data (dict or XWData)
            actions: Optional list of XWAction instances
            entity_type: Optional entity type name
            config: Optional entity configuration
            node_mode: Optional node strategy mode (overrides config)
            edge_mode: Optional edge strategy mode (overrides config)
            graph_manager_enabled: Optional graph manager flag (overrides config)
            **node_options: Additional XWNode options
        """
        # Store configuration
        self._config = config or get_config()
        
        # Override config with explicit parameters
        if node_mode is not None:
            self._config.node_mode = node_mode
        if edge_mode is not None:
            self._config.edge_mode = edge_mode
        if graph_manager_enabled is not None:
            self._config.graph_manager_enabled = graph_manager_enabled
        if node_options:
            self._config.node_options.update(node_options)
        
        # Initialize base class
        super().__init__(
            schema=schema,
            data=None,  # Will initialize separately
            entity_type=entity_type,
            config=self._config,
        )
        
        # Initialize schema
        self._schema = schema
        
        # Initialize actions list
        self._actions_list: list[Any] = actions or []
        for action in self._actions_list:
            self._register_action(action)
        
        # Initialize data with XWNode configuration
        self._data = self._init_data_with_node(data)
    
    def _init_data_with_node(self, data: Optional[Union[Dict, Any]]) -> Any:
        """
        Initialize XWData with XWNode configuration.
        
        Args:
            data: Initial data (dict or XWData)
            
        Returns:
            XWData instance configured with XWNode
        """
        # Import XWData and XWNode
        try:
            from exonware.xwdata import XWData
            from exonware.xwnode import XWNode
            from exonware.xwnode.defs import NodeMode, EdgeMode
        except ImportError as e:
            logger.warning(f"XWData/XWNode not available, using dict fallback: {e}")
            # Fallback to simple dict if dependencies not available
            return data if isinstance(data, dict) else {}
        
        # Prepare XWNode configuration
        node_config = self._config.get_node_config()
        
        # Convert string modes to enums if needed
        if isinstance(node_config.get('mode'), str):
            try:
                node_config['mode'] = NodeMode[node_config['mode']]
            except (KeyError, AttributeError):
                node_config['mode'] = NodeMode.AUTO
        
        if 'edge_mode' in node_config and isinstance(node_config['edge_mode'], str):
            try:
                node_config['edge_mode'] = EdgeMode[node_config['edge_mode']]
            except (KeyError, AttributeError):
                node_config['edge_mode'] = EdgeMode.AUTO
        
        # Create XWNode with configuration
        if data is None:
            initial_data = {}
        elif isinstance(data, dict):
            initial_data = data
        elif hasattr(data, 'to_native'):
            initial_data = data.to_native()
        else:
            initial_data = data
        
        # Create XWNode with configured strategies
        node = XWNode(
            data=initial_data,
            mode=node_config.get('mode', NodeMode.AUTO),
            **{k: v for k, v in node_config.items() if k != 'mode'}
        )
        
        # If graph manager is enabled, wrap with graph capabilities
        if self._config.graph_manager_enabled:
            try:
                from exonware.xwnode.facades.graph import XWNodeGraph
                # Convert to graph node if needed
                if not isinstance(node, XWNodeGraph):
                    # Create graph wrapper
                    graph_data = node.to_native() if hasattr(node, 'to_native') else initial_data
                    node = XWNodeGraph(
                        data=graph_data,
                        node_mode=node_config.get('mode', NodeMode.AUTO),
                        edge_mode=node_config.get('edge_mode', EdgeMode.AUTO),
                        **{k: v for k, v in node_config.items() if k not in ('mode', 'edge_mode')}
                    )
            except ImportError:
                logger.warning("Graph manager requested but XWNodeGraph not available")
        
        # Create XWData with the configured node
        try:
            # XWData can accept a node or data
            if hasattr(XWData, '__init__'):
                # Check if XWData accepts node parameter
                import inspect
                sig = inspect.signature(XWData.__init__)
                if 'node' in sig.parameters:
                    xwdata = XWData(node=node, config=None)
                else:
                    # XWData will create its own node from data
                    xwdata = XWData(data=initial_data, config=None)
                    # Replace internal node if possible
                    if hasattr(xwdata, '_node'):
                        xwdata._node = node
            else:
                xwdata = XWData(data=initial_data, config=None)
        except Exception as e:
            logger.error(f"Failed to create XWData with node: {e}")
            # Fallback to simple dict
            return initial_data if isinstance(initial_data, dict) else {}
        
        return xwdata
    
    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    
    @property
    def data(self) -> Any:  # XWData type
        """Get the entity data."""
        return self._data
    
    @property
    def schema(self) -> Optional[Any]:  # XWSchema type
        """Get the entity schema."""
        return self._schema
    
    @property
    def actions(self) -> list[Any]:  # List[XWAction] type
        """Get the list of entity actions."""
        return self._actions_list.copy()
    
    # ==========================================================================
    # DATA INITIALIZATION
    # ==========================================================================
    
    def _init_data_from_dict(self, data: EntityData) -> None:
        """Initialize data from dictionary."""
        self._data = self._init_data_with_node(data)
    
    # ==========================================================================
    # FACTORY METHODS
    # ==========================================================================
    
    @classmethod
    def from_dict(
        cls,
        data: EntityData,
        schema: Optional[Any] = None,  # XWSchema type
        entity_type: Optional[str] = None,
        config: Optional[XWEntityConfig] = None,
        **kwargs
    ) -> "XWEntity":
        """
        Create entity from dictionary.
        
        Args:
            data: Entity data dictionary
            schema: Optional schema
            entity_type: Optional entity type
            config: Optional configuration
            **kwargs: Additional options (node_mode, edge_mode, etc.)
            
        Returns:
            XWEntity instance
        """
        return cls(
            schema=schema,
            data=data,
            entity_type=entity_type,
            config=config,
            **kwargs
        )
    
    @classmethod
    def from_file(
        cls,
        path: Union[str, Path],
        schema: Optional[Any] = None,  # XWSchema type
        format: Optional[str] = None,
        config: Optional[XWEntityConfig] = None,
        **kwargs
    ) -> "XWEntity":
        """
        Create entity from file.
        
        Args:
            path: File path
            schema: Optional schema
            format: Optional file format
            config: Optional configuration
            **kwargs: Additional options
            
        Returns:
            XWEntity instance
        """
        entity = cls(schema=schema, config=config, **kwargs)
        entity._from_file(path, format)
        return entity
    
    @classmethod
    def from_schema(
        cls,
        schema: Any,  # XWSchema type
        initial_data: Optional[EntityData] = None,
        entity_type: Optional[str] = None,
        config: Optional[XWEntityConfig] = None,
        **kwargs
    ) -> "XWEntity":
        """
        Create entity with schema and optional initial data.
        
        Args:
            schema: Entity schema
            initial_data: Optional initial data
            entity_type: Optional entity type
            config: Optional configuration
            **kwargs: Additional options
            
        Returns:
            XWEntity instance
        """
        return cls(
            schema=schema,
            data=initial_data or {},
            entity_type=entity_type,
            config=config,
            **kwargs
        )
    
    @classmethod
    def from_data(
        cls,
        data: Union[EntityData, Any],  # XWData type or dict
        schema: Optional[Any] = None,  # XWSchema type
        entity_type: Optional[str] = None,
        config: Optional[XWEntityConfig] = None,
        **kwargs
    ) -> "XWEntity":
        """
        Create entity with data and optional schema.
        
        Args:
            data: Entity data (dict or XWData)
            schema: Optional schema
            entity_type: Optional entity type
            config: Optional configuration
            **kwargs: Additional options
            
        Returns:
            XWEntity instance
        """
        return cls(
            schema=schema,
            data=data,
            entity_type=entity_type,
            config=config,
            **kwargs
        )
    
    # ==========================================================================
    # PUBLIC API METHODS
    # ==========================================================================
    
    def get(self, path: str, default: Any = None) -> Any:
        """
        Get value at path (public API).
        
        Args:
            path: Dot-separated path
            default: Default value if path not found
            
        Returns:
            Value at path or default
        """
        return self._get(path, default)
    
    def set(self, path: str, value: Any) -> None:
        """
        Set value at path (public API).
        
        Args:
            path: Dot-separated path
            value: Value to set
        """
        self._set(path, value)
    
    def delete(self, path: str) -> None:
        """
        Delete value at path (public API).
        
        Args:
            path: Dot-separated path
        """
        self._delete(path)
    
    def update(self, updates: EntityData) -> None:
        """
        Update multiple values (public API).
        
        Args:
            updates: Dictionary of path -> value updates
        """
        self._update(updates)
    
    def validate(self) -> bool:
        """
        Validate entity data against schema (public API).
        
        Returns:
            True if valid, False otherwise
            
        Raises:
            XWEntityValidationError: If validation fails and strict mode is enabled
        """
        is_valid = self._validate()
        
        if not is_valid and self._config.strict_validation:
            raise XWEntityValidationError(
                "Entity validation failed",
                cause=None
            )
        
        return is_valid
    
    def execute_action(self, action_name: str, **kwargs) -> Any:
        """
        Execute a registered action (public API).
        
        Args:
            action_name: Name of the action to execute
            **kwargs: Action parameters
            
        Returns:
            Action result
            
        Raises:
            XWEntityActionError: If action not found or execution fails
        """
        return self._execute_action(action_name, **kwargs)
    
    def list_actions(self) -> list[str]:
        """
        List available action names (public API).
        
        Returns:
            List of action names
        """
        return self._list_actions()
    
    def register_action(self, action: Any) -> None:  # XWAction type
        """
        Register an action for this entity (public API).
        
        Args:
            action: XWAction instance to register
        """
        self._register_action(action)
        if action not in self._actions_list:
            self._actions_list.append(action)
    
    def transition_to(self, target_state: EntityState) -> None:
        """
        Transition to a new state (public API).
        
        Args:
            target_state: Target state
            
        Raises:
            XWEntityStateError: If transition is not allowed
        """
        self._transition_to(target_state)
    
    def can_transition_to(self, target_state: EntityState) -> bool:
        """
        Check if state transition is allowed (public API).
        
        Args:
            target_state: Target state
            
        Returns:
            True if transition is allowed
        """
        return self._can_transition_to(target_state)
    
    def to_dict(self) -> EntityData:
        """
        Export entity as dictionary (public API).
        
        Returns:
            Entity data dictionary
        """
        return self._to_dict()
    
    def to_file(self, path: Union[str, Path], format: Optional[str] = None) -> bool:
        """
        Save entity to file (public API).
        
        Args:
            path: File path
            format: Optional file format
            
        Returns:
            True if successful
        """
        return self._to_file(path, format)
    
    def from_file(self, path: Union[str, Path], format: Optional[str] = None) -> None:
        """
        Load entity from file (public API).
        
        Args:
            path: File path
            format: Optional file format
        """
        self._from_file(path, format)
    
    def to_native(self) -> EntityData:
        """
        Get entity as native dictionary (public API).
        
        Returns:
            Entity data dictionary
        """
        return self._to_native()


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "XWEntity",
]
