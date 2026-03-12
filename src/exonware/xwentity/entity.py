#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/entity.py
XWEntity - Entity Implementation
This module provides the XWEntity class that composes schema, actions, data handling,
metadata, caching, performance stats, state management, and property discovery.
XWEntity is format-agnostic and storage-agnostic: it does not implement a storage
provider or auth provider. Persistence (file-tree, single file, or future xwstorage)
is the responsibility of the caller or a persistence layer. xwstorage works with
IData/XWData; entity content can be passed via entity.data or entity.to_dict() and
stored/loaded without XWEntity depending on xwstorage or auth.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
from typing import Any
from datetime import datetime
from pathlib import Path
from exonware.xwsystem import get_logger
from exonware.xwsystem.validation import validate_untrusted_data
from exonware.xwdata import XWData
from exonware.xwnode import XWNode
from exonware.xwnode.defs import NodeMode, EdgeMode
from exonware.xwnode.facades.graph import XWNodeGraph
from exonware.xwschema import XWSchema
from exonware.xwaction import XWAction, extract_actions
from .base import AEntity, XWEntityMetadata
from .contracts import IEntity
from .defs import EntityState, EntityID, EntityType, EntityData, PerformanceMode
from .metaclass import (
    DecoratorScanner,
    _create_direct_property,
    _create_delegated_property,
    _is_frequently_accessed,
)
from .errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
)
from .config import XWEntityConfig, get_config
logger = get_logger(__name__)
# ==============================================================================
# XWENTITY - FACADE CLASS
# ==============================================================================

class XWEntity(AEntity):
    """
    XWEntity class providing a complete interface for entity operations.
    This class composes:
    - XWSchema for validation
    - list[XWAction] for actions
    - XWData (using XWNode) for data storage
    This class implements the facade pattern, composing:
    - XWSchema for validation
    - list[XWAction] for actions
    - XWData (using XWNode) for data storage
    XWData is configured with XWNode strategies (node_mode, edge_mode,
    graph_manager_enabled, etc.) as specified in the configuration.
    Storage-agnostic: save/load use the given path and format only. Storage backends
    (e.g. xwstorage) consume IData/XWData; use entity.data or entity.to_dict() to
    pass content. XWEntity does not implement a storage provider or auth provider.
    Supports automatic property discovery via decorators and type hints
    when using subclasses with the metaclass functionality.
    """

    def __init_subclass__(cls, **kwargs):
        """Initialize subclass with automatic property/action discovery and creation."""
        super().__init_subclass__(**kwargs)
        # Scan for properties and actions
        annotations = getattr(cls, '__annotations__', {})
        namespace = dict(cls.__dict__)
        config = get_config()
        properties = DecoratorScanner.scan_properties(namespace, annotations)
        actions = DecoratorScanner.scan_actions(namespace)
        # Determine performance mode
        performance_mode = getattr(config, 'performance_mode', PerformanceMode.AUTO)
        if performance_mode == PerformanceMode.AUTO:
            performance_mode = (
                PerformanceMode.PERFORMANCE if len(properties) < 10
                else PerformanceMode.MEMORY
            )
        # Create properties based on performance mode
        for prop in properties:
            # Skip if property already exists as a non-property (user-defined attribute)
            existing = cls.__dict__.get(prop.name)
            if existing is not None:
                # If it's already a property, keep it (user-defined @property)
                if isinstance(existing, property):
                    continue
                # If it's a method or other callable, skip it
                if callable(existing):
                    continue
                # If it's a regular attribute, skip it
                if not isinstance(existing, property):
                    continue
            if performance_mode == PerformanceMode.PERFORMANCE:
                setattr(cls, prop.name, _create_direct_property(prop))
            elif performance_mode == PerformanceMode.MEMORY:
                setattr(cls, prop.name, _create_delegated_property(prop))
            elif performance_mode == PerformanceMode.BALANCED:
                if _is_frequently_accessed(prop):
                    setattr(cls, prop.name, _create_direct_property(prop))
                else:
                    setattr(cls, prop.name, _create_delegated_property(prop))
            else:
                setattr(cls, prop.name, _create_direct_property(prop))
        # Store metadata for later use
        cls._xwentity_properties = properties
        cls._xwentity_actions = actions
        cls._xwentity_performance_mode = performance_mode
        logger.debug(
            f"XWEntity subclass '{cls.__name__}' discovered "
            f"{len(properties)} properties, {len(actions)} actions, mode: {performance_mode}"
        )
    @staticmethod

    def _normalize_schema_id(schema_dict: dict[str, Any]) -> dict[str, Any]:
        """
        Ensure schema has $id for type_id / schema_file_base.
        Uses schema.name as fallback when $id and id are missing.
        """
        if "$id" in schema_dict or "id" in schema_dict:
            return schema_dict
        name = schema_dict.get("name")
        if name:
            return {**schema_dict, "$id": str(name)}
        return schema_dict

    def __init__(
        self,
        schema: XWSchema | dict[str, Any] | str | None = None,  # XWSchema, dict (JSON schema), JSON string, or None
        data: XWData | dict[str, Any] | list[Any] | None = None,  # XWData, dict, or None
        actions: list[XWAction] | dict[str, Any] | None = None,  # List of XWAction or dict of action definitions
        entity_type: str | None = None,
        config: XWEntityConfig | None = None,
        # XWNode configuration options
        node_mode: str | None = None,
        edge_mode: str | None = None,
        graph_manager_enabled: bool | None = None,
        **node_options
    ):
        """
        Initialize XWEntity with composition of schema, actions, and data.
        Supports:
        - Schema conversion (dict, JSON string, XWSchema)
        - Actions provided as list or dict
        - XWNode configuration
        - Entity metadata and caching
        Args:
            schema: Optional schema - can be:
                - XWSchema instance (used directly)
                - dict (JSON schema) - converted to XWSchema
                - str (JSON string) - parsed and converted to XWSchema
                - None
            data: Optional initial data - can be:
                - XWData instance (used directly)
                - dict - converted to XWData
                - list - converted to XWData
                - None
            actions: Optional actions - can be:
                - list[XWAction] - list of XWAction instances
                - dict[str, Any] - dictionary of action names to XWAction instances or action definitions
                - None
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
        # Resolve entity type (prefer explicit, then config default; use subclass name only for subclasses)
        resolved_type = entity_type
        if resolved_type is None:
            resolved_type = self._config.default_entity_type
            if resolved_type == "entity" and self.__class__ is not XWEntity:
                name = self.__class__.__name__
                if name.lower().endswith("entity"):
                    name = name[:-6]
                resolved_type = (name or "entity").lower()
        # Normalize schema (supports dict, JSON string, XWSchema)
        normalized_schema: XWSchema | None = None
        if schema is None:
            normalized_schema = None
        elif isinstance(schema, XWSchema):
            normalized_schema = schema
        elif isinstance(schema, str):
            # JSON string - parse it
            import json
            schema_dict = json.loads(schema)
            schema_dict = self._normalize_schema_id(schema_dict)
            normalized_schema = XWSchema(schema_dict)
        elif isinstance(schema, dict):
            # Dict - convert to XWSchema
            schema_dict = self._normalize_schema_id(dict(schema))
            normalized_schema = XWSchema(schema_dict)
        else:
            raise XWEntityError(f"Unsupported schema type: {type(schema).__name__}")
        # super() → AEntity → XWObject; pass object_id from data so parent init sets id
        object_id = (data.get("id") if isinstance(data, dict) and data and "id" in data else None) or ""
        super().__init__(
            schema=normalized_schema,
            data=None,  # initialized below
            entity_type=resolved_type,
            config=self._config,
            object_id=object_id,
        )
        self._created_at = self._metadata._created_at
        self._updated_at = self._metadata._updated_at
        # Initialize schema
        self._schema = normalized_schema
        # Initialize actions list + registry (supports both dict and list)
        self._actions_list: list[XWAction] = []
        if actions is not None:
            # Handle actions (dict or list)
            if isinstance(actions, list):
                # List of XWAction instances
                for action in actions:
                    self.register_action(action)
            elif isinstance(actions, dict):
                # Dict of action definitions - use internal _init_actions logic
                self._init_actions(actions)
        # Auto-discover actions decorated with @XWAction on this entity class (from XWEntity)
        if self._config.auto_register_actions:
            # Use metaclass-discovered actions if available
            discovered_actions = getattr(self.__class__, '_xwentity_actions', None)
            if discovered_actions:
                for action_info in discovered_actions:
                    # Get the actual action instance from the method
                    method = getattr(self, action_info.name, None)
                    if method and hasattr(method, 'api_name'):
                        # It's an XWAction instance
                        self.register_action(method)
                    elif method and callable(method):
                        # It's a regular method, wrap it if needed
                        self.register_action(method)
            else:
                # Fallback to old discovery method
                for action in self._discover_class_actions():
                    self.register_action(action)
        # Initialize data with XWNode configuration (from XWEntity)
        self._data = self._init_data_with_node(data)
        # Parent already got id via object_id; from_native only for uid, title, description, timestamps
        if isinstance(data, dict) and data:
            obj_data = {k: data[k] for k in ("uid", "title", "description", "desc", "created_at", "updated_at") if k in data}
            if "desc" in obj_data and "description" not in obj_data:
                obj_data["description"] = obj_data.pop("desc")
            if obj_data:
                super().from_native(obj_data)
            if "deleted_at" in data:
                raw = data["deleted_at"]
                if isinstance(raw, str):
                    self._metadata._deleted_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                elif isinstance(raw, datetime):
                    self._metadata._deleted_at = raw

    def _init_data_with_node(self, data: XWData | dict[str, Any] | list[Any] | None) -> XWData:
        """
        Initialize XWData with XWNode configuration.
        Fully reuses XWData for all data storage and operations.
        XWData provides path-based access, query capabilities, and format support.
        Args:
            data: Initial data (dict, list, or XWData)
        Returns:
            XWData instance configured with XWNode for graph capabilities
        """
        # Prepare XWNode configuration
        node_config = self._config.get_node_config()
        # Use XWData directly - fully reuses xwdata capabilities
        if isinstance(data, XWData):
            xwdata = data
        else:
            xwdata = XWData(data or {})
        native = xwdata.to_native()
        # Convert mode strings to enums if provided
        mode = node_config.get("mode", "AUTO")
        edge = node_config.get("edge_mode", "AUTO")
        if isinstance(mode, str):
            try:
                mode = NodeMode[mode]
            except Exception:
                mode = NodeMode.AUTO
        if isinstance(edge, str):
            try:
                edge = EdgeMode[edge]
            except Exception:
                edge = EdgeMode.AUTO
        # Create configured XWNode (or XWNodeGraph) and inject it into the XWDataNode
        # Filter node_options to avoid duplicate/conflicting kwargs (node_mode, edge_mode, immutable)
        node_opts = {
            k: v for k, v in self._config.node_options.items()
            if k not in ("node_mode", "edge_mode", "mode", "immutable")
        }
        if self._config.graph_manager_enabled:
            # Check if data already has graph structure (nodes/edges) from loading
            # This happens when loading a saved entity that had graph_manager_enabled=True
            if isinstance(native, dict) and "nodes" in native and "edges" in native:
                # Data already has graph structure - check if it's already properly structured
                # If nodes contains the actual data (not another nested nodes structure), use it directly
                nodes_data = native.get("nodes", {})
                if isinstance(nodes_data, dict) and "nodes" not in nodes_data:
                    # This is the correct structure - nodes contains the actual entity data
                    # XWNodeGraph will wrap it, so we pass the nodes data (actual entity data)
                    graph_data = nodes_data
                else:
                    # Already double-wrapped or malformed - use the structure as-is
                    graph_data = native
            else:
                # Plain data - XWNodeGraph will wrap it in graph structure
                graph_data = native if isinstance(native, dict) else {}
            xwnode = XWNodeGraph(data=graph_data, node_mode=mode, edge_mode=edge, immutable=True, **node_opts)
        else:
            xwnode = XWNode.from_native(native, mode=mode.name if hasattr(mode, "name") else str(mode), immutable=True, **node_opts)
        if hasattr(xwdata, "_node") and hasattr(xwdata._node, "_xwnode"):
            xwdata._node._xwnode = xwnode
            xwdata._node._data = xwnode.to_native()
        return xwdata

    def _init_actions(self, actions: dict[str, Any] | list[Any]) -> None:
        """
        Initialize actions from dictionary or list.
        Automatically converts action definitions (dict) to XWAction instances.
        Accepts both dict[str, Any] and list[XWAction] formats.
        Args:
            actions: Can be:
                - dict[str, Any]: Dictionary of action names to either XWAction instances or action definitions (dict)
                - list[XWAction]: List of XWAction instances (api_name used as key)
        """
        from exonware.xwaction import XWAction
        # Handle list format - convert to dict using api_name
        if isinstance(actions, list):
            actions_dict = {}
            for action in actions:
                if isinstance(action, XWAction):
                    # Use api_name or name as key
                    action_name = getattr(action, 'api_name', None) or getattr(action, 'name', None)
                    if action_name:
                        actions_dict[action_name] = action
                    else:
                        logger.warning(f"Action in list has no api_name, skipping: {action}")
                elif callable(action):
                    # Callable without XWAction wrapper - use function name
                    action_name = getattr(action, '__name__', f"action_{len(actions_dict)}")
                    actions_dict[action_name] = action
                else:
                    logger.warning(f"Unsupported action type in list: {type(action)}")
            actions = actions_dict
        # Process actions dictionary
        if not isinstance(actions, dict):
            logger.warning(f"Actions must be dict or list, got: {type(actions)}")
            return
        for action_name, action_def in actions.items():
            if isinstance(action_def, XWAction):
                # Already an XWAction instance - register directly
                self.register_action(action_def)
            elif isinstance(action_def, dict):
                # Action definition dict - convert to XWAction
                try:
                    # Check for query-based action definition
                    if 'query' in action_def and isinstance(action_def['query'], dict):
                        # Query-based action: {"query": {"format": "xwqs", "query": "SELECT ..."}}
                        query_config = action_def['query']
                        query_string = query_config.get('query') or query_config.get('query_string')
                        query_format = query_config.get('format', 'sql')
                        if not query_string:
                            raise ValueError(f"Action '{action_name}' query definition missing 'query' field")
                        # Capture self for closure
                        obj_instance = self
                        # Create handler function that executes the query
                        def query_handler(instance=None, **kwargs):
                            """
                            Execute query using XWAction.query() with context and variables.
                            Merges object data with variables from execution context (kwargs).
                            Variables can be referenced in queries using $variable_name syntax
                            and will be substituted from the execution context.
                            Args:
                                instance: The XWEntity instance (passed by XWAction.execute())
                                **kwargs: Variables from execution context
                            """
                            # Get the object instance (XWEntity) - use instance if provided, otherwise use captured self
                            obj = instance if instance is not None else obj_instance
                            # Get object data in native format (dict/list)
                            if hasattr(obj.data, 'to_native'):
                                obj_data = obj.data.to_native()
                            elif hasattr(obj.data, 'to_dict'):
                                obj_data = obj.data.to_dict()
                            else:
                                obj_data = obj.data
                            # Initialize processed_query early for FROM clause checking
                            processed_query = query_string
                            # For SQL/xwqs queries on single objects, format data correctly
                            if isinstance(obj_data, dict):
                                # For single object dict, merge with variables
                                if kwargs:
                                    merged_dict = {**obj_data, **kwargs}
                                else:
                                    merged_dict = obj_data
                                # For SQL/xwqs queries, wrap single dict in list for table-like structure
                                if query_format in ('sql', 'xwqs', 'xwquery'):
                                    final_query_data = [merged_dict]
                                else:
                                    final_query_data = merged_dict
                                query_data = merged_dict
                            elif isinstance(obj_data, list):
                                final_query_data = obj_data
                                query_data = obj_data
                            else:
                                wrapped = {"_data": obj_data}
                                if kwargs:
                                    wrapped.update(kwargs)
                                final_query_data = [wrapped] if query_format in ('sql', 'xwqs', 'xwquery') else wrapped
                                query_data = wrapped
                            # Support variable substitution in query string: $variable_name
                            var_context = query_data if isinstance(query_data, dict) else (final_query_data[0] if isinstance(final_query_data, list) and final_query_data and isinstance(final_query_data[0], dict) else {})
                            if isinstance(var_context, dict):
                                import re
                                var_pattern = r'\$(\w+)'
                                for var_name in re.findall(var_pattern, processed_query):
                                    if var_name in var_context:
                                        var_value = var_context[var_name]
                                        if isinstance(var_value, str):
                                            processed_query = processed_query.replace(f'${var_name}', f"'{var_value}'")
                                        else:
                                            processed_query = processed_query.replace(f'${var_name}', str(var_value))
                            # For SELECT queries without FROM clause on single objects, add FROM table
                            if query_format in ('sql', 'xwqs', 'xwquery'):
                                has_from = 'FROM' in processed_query.upper() or 'from' in processed_query
                                is_select = processed_query.strip().upper().startswith('SELECT')
                                if not has_from and is_select and isinstance(final_query_data, list) and len(final_query_data) == 1:
                                    processed_query = processed_query.rstrip(';').rstrip() + " FROM table"
                                    final_query_data = {"table": final_query_data}
                                    logger.debug(f"Added FROM clause to query: {processed_query}, restructured data: {final_query_data}")
                                elif not is_select and isinstance(final_query_data, list) and len(final_query_data) == 1:
                                    # INSERT/UPDATE/DELETE: ensure data is {"table": [row]} for target
                                    final_query_data = {"table": final_query_data}
                            # Execute query with properly formatted data
                            try:
                                result = XWAction.query(processed_query, final_query_data, format=query_format, **kwargs)
                            except Exception as e:
                                from .errors import XWEntityActionError
                                error_msg = (
                                    f"Query execution failed for action '{action_name}': {e}. "
                                    f"Ensure exonware-xwquery is installed and query syntax is correct. "
                                    f"Query: {processed_query[:100] if len(processed_query) > 100 else processed_query}"
                                )
                                raise XWEntityActionError(error_msg, action_name=action_name, cause=e) from e
                            # Extract data from result (XWAction.query returns {"results": data})
                            if hasattr(result, 'data'):
                                data = result.data
                            elif hasattr(result, 'result'):
                                data = result.result
                            else:
                                data = result
                            if isinstance(data, dict) and "results" in data and len(data) == 1:
                                data = data["results"]
                            # Unwrap to row(s): [{"key":"table","value":[row]}] -> row; [row] -> row
                            if isinstance(data, list) and data:
                                first = data[0]
                                if isinstance(first, dict) and "value" in first:
                                    data = first["value"]
                                    if isinstance(data, list) and len(data) == 1:
                                        data = data[0]
                                elif isinstance(first, dict) and len(data) == 1:
                                    data = first
                                else:
                                    data = data
                            elif isinstance(data, dict) and "value" in data:
                                v = data["value"]
                                data = v[0] if isinstance(v, list) and len(v) == 1 else v
                            return {"results": data}
                        # Create XWAction from query handler
                        action = XWAction.create(query_handler, api_name=action_name)
                        self.register_action(action)
                    # Script-based action: {"script": {"language": "python|javascript", "code": "..."}}
                    elif 'script' in action_def and isinstance(action_def['script'], dict):
                        script_config = action_def['script']
                        script_language = script_config.get('language', 'python')
                        script_code = script_config.get('code') or script_config.get('script')
                        if not script_code:
                            raise ValueError(f"Action '{action_name}' script definition missing 'code' field")
                        # Create handler function that executes the script
                        obj_instance = self
                        def script_handler(instance=None, **kwargs):
                            """Execute script using the specified language."""
                            obj = instance if instance is not None else obj_instance
                            # Get object data in native format
                            if hasattr(obj.data, 'to_native'):
                                obj_data = obj.data.to_native()
                            elif hasattr(obj.data, 'to_dict'):
                                obj_data = obj.data.to_dict()
                            else:
                                obj_data = obj.data
                            # Merge object data with kwargs for script context
                            script_context = {**obj_data, **kwargs} if isinstance(obj_data, dict) else kwargs
                            if script_language == 'python':
                                # Execute Python script with context
                                exec_globals = {'__builtins__': __builtins__, 'data': script_context, 'obj': obj, 'instance': obj}
                                exec_locals = {}
                                exec(script_code, exec_globals, exec_locals)
                                # Return the result (script should set 'result' variable or return value)
                                return exec_locals.get('result', exec_locals)
                            elif script_language == 'javascript':
                                # JavaScript execution would require a JS engine
                                # For now, raise an error suggesting to use Python
                                raise ValueError(
                                    f"JavaScript script execution not yet implemented. "
                                    f"Use 'python' language or install exonware-xwstorage for JavaScript support."
                                )
                            else:
                                raise ValueError(f"Unsupported script language: {script_language}. Supported: 'python', 'javascript'")
                        # Create XWAction from script handler
                        action = XWAction.create(script_handler, api_name=action_name)
                        self.register_action(action)
                    # Handler-based action: {"handler": callable}
                    elif 'handler' in action_def and callable(action_def['handler']):
                        # Wrap handler in XWAction
                        handler_func = action_def['handler']
                        action = XWAction.create(handler_func, api_name=action_name)
                        self.register_action(action)
                    # Try to create XWAction from dict using from_native
                    elif hasattr(XWAction, 'from_native'):
                        action = XWAction.from_native(action_def)
                        self.register_action(action)
                    else:
                        raise ValueError(f"Action '{action_name}' definition must have 'handler' (callable) or 'query' (dict) field")
                except Exception as e:
                    # If conversion fails, log error
                    logger.error(f"Could not convert action '{action_name}' from dict: {e}")
                    raise XWEntityActionError(
                        f"Failed to initialize action '{action_name}': {e}",
                        action_name=action_name,
                        cause=e
                    ) from e
            elif callable(action_def):
                # Callable function - register directly
                self.register_action(action_def)
            else:
                logger.warning(f"Action '{action_name}' has unsupported type: {type(action_def)}")
    # ==========================================================================
    # PROPERTIES
    # ==========================================================================
    @property

    def data(self) -> Any:  # XWData type
        """Get the entity data."""
        return self._data
    @property

    def schema(self) -> Any | None:  # XWSchema type
        """
        Get the entity schema.
        Supports:
        - Dict-style access: schema["properties"]["name"]
        - Query method: schema.query("xwquery") (delegates to underlying XWData if available)
        """
        return self._schema
    @property

    def type_id(self) -> str | None:
        """
        Entity type identifier, always equal to schema.id when schema is present.
        Returns schema.id (or $id from dict schemas), or schema.name as fallback,
        or None when no schema.
        """
        if not self._schema:
            return None
        if hasattr(self._schema, "id") and self._schema.id:
            return str(self._schema.id)
        if isinstance(self._schema, dict):
            return (
                self._schema.get("$id")
                or self._schema.get("id")
                or self._schema.get("name")
                or None
            )
        return None
    @property

    def schema_file_base(self) -> str:
        """
        File-base name derived from schema.id, in lowercase for JSON filenames.
        Example: schema.id = "bluesmyth.Character" -> "bluesmyth.character"
        so that data and desc can be saved as bluesmyth.character.data.json
        and bluesmyth.character.desc.json.
        """
        tid = self.type_id
        return str(tid).lower() if tid else "entity"
    @property

    def name(self) -> str:
        """Display name from data: name or title (common across entity types)."""
        return self.get("name") or self.get("title") or ""
    @property

    def title(self) -> str | None:
        """Display title from data: title or name."""
        out = self.get("title") or self.get("name")
        return out if out else None
    @property

    def description(self) -> str | None:
        """Description from data: desc or description."""
        out = self.get("desc") or self.get("description")
        return out if out else None
    @property

    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._metadata.created_at
    @property

    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._metadata.updated_at
    @property

    def deleted_at(self) -> datetime | None:
        """Get deletion timestamp (None if not deleted)."""
        return self._metadata.deleted_at
    @property

    def actions(self) -> dict[str, Any]:  # Dict of XWAction instances
        """
        Get actions as dictionary.
        Actions are normalized at registration time to always be XWAction instances.
        Returns:
            Dictionary mapping action names to XWAction instances
        """
        return self._actions

    def _discover_class_actions(self) -> list[XWAction]:
        """
        Discover @XWAction-decorated callables on the entity class.
        Reuses xwaction.extract_actions utility for consistency.
        """
        return extract_actions(self.__class__)
    # ==========================================================================
    # DATA INITIALIZATION
    # ==========================================================================

    def _init_data_from_dict(self, data: EntityData) -> None:
        """Initialize data from dictionary."""
        self._data = self._init_data_with_node(data)
    # ==========================================================================
    # FACTORY METHODS (from XWEntity)
    # ==========================================================================
    # Note: This classmethod overrides the instance method from_dict in parent classes
    # We need to explicitly bind it to ensure it's accessible as a classmethod
    @classmethod

    def from_dict(
        cls,
        data: EntityData,
        schema: Any | None = None,  # XWSchema type
        entity_type: str | None = None,
        config: XWEntityConfig | None = None,
        **kwargs
    ) -> "XWEntity":
        """
        Create entity from dictionary with validation.
        Args:
            data: Entity data dictionary (can be full entity dict with _metadata/_data keys, or plain data dict)
            schema: Optional schema for validation
            entity_type: Optional entity type
            config: Optional configuration
            **kwargs: Additional options (node_mode, edge_mode, etc.)
        Returns:
            XWEntity instance
        Raises:
            XWEntityError: If data is invalid or schema validation fails
        """
        if not isinstance(data, dict):
            raise XWEntityError(
                f"Expected dict for data, got {type(data).__name__}"
            )
        try:
            # Check if this is a full entity dict (from to_native()) with _metadata and _data keys
            if "_metadata" in data or "_data" in data or "_schema" in data or "_actions" in data:
                # This is a full entity dict - create empty entity and use _from_dict
                entity = cls(
                    schema=schema,
                    entity_type=entity_type,
                    config=config,
                    **kwargs
                )
                entity._from_dict(data)
            else:
                # This is plain data dict - pass directly to constructor
                entity = cls(
                    schema=schema,
                    data=data,
                    entity_type=entity_type,
                    config=config,
                    **kwargs
                )
            # Auto-validate if schema is provided and auto_validate is enabled
            if schema and config and config.auto_validate:
                if not entity.validate():
                    raise XWEntityValidationError(
                        "Entity validation failed during creation",
                        cause=None
                    )
            return entity
        except (XWEntityError, XWEntityValidationError):
            raise
        except Exception as e:
            raise XWEntityError(
                f"Failed to create entity from dict: {e}",
                cause=e
            )
    @classmethod

    def from_native(cls, data: EntityData, schema: Any | None = None, entity_type: str | None = None, **kwargs) -> "XWEntity":
        """
        Create entity from native Python dictionary.
        Similar to XWData.from_native(), this creates an XWEntity from a dictionary
        that contains the merged representation (schema + actions + data).
        This allows XWEntity to work seamlessly with XWData serialization.
        Args:
            data: Dictionary containing _metadata, _schema, _actions, and _data
            schema: Optional schema override (if not in data)
            entity_type: Optional entity type override (if not in data)
            **kwargs: Additional options
        Returns:
            XWEntity instance
        """
        resolved_entity_type = kwargs.pop("entity_type", kwargs.pop("object_type", entity_type))
        return cls.from_dict(data, schema=schema, entity_type=resolved_entity_type, **kwargs)
    # ==========================================================================
    # PUBLIC API METHODS (from XWEntity)
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
        Uses XWSchema.validate_sync() for validation.
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

    def validate_issues(self) -> list[dict[str, str]]:
        """
        Get detailed validation issues from schema (public API).
        Uses XWSchema.validate_issues_sync() for detailed validation.
        Returns:
            List of validation issue dictionaries with 'path' and 'message' keys
        """
        if not self._schema:
            return []  # No schema means no validation issues
        if self._data is None:
            return [{"path": "", "message": "Entity data is None"}]
        # Use XWSchema.validate_issues_sync() for detailed validation
        if hasattr(self._schema, "validate_issues_sync"):
            return self._schema.validate_issues_sync(self._data)
        elif hasattr(self._schema, "validate_sync"):
            # Fallback: use validate_sync and extract errors
            is_valid, errors = self._schema.validate_sync(self._data)
            if is_valid:
                return []
            # Convert error strings to issue dicts
            return [{"path": "", "message": err} for err in errors]
        else:
            logger.warning("Schema does not support validation_issues")
            return []

    def execute_action(self, action_name: str, *args, **kwargs) -> Any:
        """
        Execute a registered action with parameter validation (public API).
        Args:
            action_name: Name of the action to execute
            *args: Positional arguments (converted to kwargs based on function signature)
            **kwargs: Keyword arguments
        Returns:
            Action result (may be ActionResult or direct result)
        Raises:
            XWEntityActionError: If action not found or execution fails
            XWEntityValidationError: If parameter validation fails
        """
        return self._execute_action(action_name, *args, **kwargs)

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

    def to_dict(self, include_schema: bool = True) -> dict[str, Any]:
        """
        Export entity as dictionary (public API).
        Set include_schema=False when schema lives elsewhere (e.g. .desc file or registry).
        Returns:
            Entity data dictionary
        """
        return super().to_dict(include_schema=include_schema)
    # NOTE:
    # - Factory construction from dict is done via the classmethod `from_dict(...)`
    # - In‑place restoration of an existing instance is done via the internal helper
    #   `_from_dict(...)` inherited from the base class. We do not add extra public
    #   aliases here to keep the API surface minimal and avoid name conflicts.
    # ==========================================================================
    # STORAGE OPERATIONS
    # ==========================================================================

    def save(
        self,
        path: str | Path,
        format: str | None = None,
        *,
        include_schema: bool = True,
        **options: Any,
    ) -> None:
        """
        Save entity to storage in any supported format (format-agnostic; uses xwdata/xwsystem).
        XWEntity is storage-agnostic: this writes to the given path using whatever format
        xwdata supports (json, xwjson, yaml, etc.). "Where" and "in what shape" (e.g. file-tree
        vs single file vs future xwstorage) are the responsibility of the caller or a
        persistence layer. Storage backends like xwstorage work with IData/XWData; they can
        accept entity content via entity.data or entity.to_dict() and do not require XWEntity
        to implement a storage provider or auth provider.
        Args:
            path: File path to save to
            format: Optional format name (auto-detected from extension if not provided)
            include_schema: If False, omit schema from the saved payload (use when schema
                lives elsewhere, e.g. .desc file or shared registry)
            **options: Additional format-specific options
        """
        import asyncio
        from exonware.xwdata import XWData
        object_dict = self.to_dict(include_schema=include_schema)
        # Create XWData instance containing the merged object (schema + actions + data)
        merged_data = XWData.from_native(object_dict)
        # Use XWData.save() to save - fully reuses xwdata format capabilities
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, merged_data.save(path, format=format, **options))
                    future.result()
            else:
                loop.run_until_complete(merged_data.save(path, format=format, **options))
        except RuntimeError:
            asyncio.run(merged_data.save(path, format=format, **options))

    def save_to_directory(
        self,
        output_dir: str | Path,
        *,
        save_desc: bool = False,
        format: str | None = None,
        **options: Any,
    ) -> list[Path]:
        """
        Convenience: save entity data (and optionally desc) under a directory using schema.id in lowercase.
        Does not save schema when save_desc is False (default); schema is assumed to live elsewhere.
        "Where" and naming (e.g. collection-based names like .data.collection_1.json) are the
        responsibility of the caller or a persistence layer; this is a simple file-based option.
        Writes:
        - <output_dir> / <schema_file_base>.data.json  (entity data payload only)
        - If save_desc: <output_dir> / <schema_file_base>.desc.json  (meta + schema + actions)
        Example: schema.id = "bluesmyth.Character" -> bluesmyth.character.data.json.
        Args:
            output_dir: Directory to write files into
            save_desc: If True, also write the desc file (meta, schema, actions); default False so schema is not saved again
            format: Override format (default json for this helper)
            **options: Passed to the underlying save
        Returns:
            List of paths written
        """
        from exonware.xwsystem import JsonSerializer
        _json = JsonSerializer()
        _write_opts = {"indent": 2, "ensure_ascii": False}
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        base = self.schema_file_base
        written: list[Path] = []
        # Data file: lowercase name from schema.id; content = entity data payload (one object)
        data_path = out / f"{base}.data.json"
        if hasattr(self._data, "to_native"):
            data_payload = self._data.to_native()
        else:
            data_payload = getattr(self._data, "_data", None) or {}
        _json.save_file(data_payload, data_path, **_write_opts)
        written.append(data_path)
        if save_desc:
            desc_path = out / f"{base}.desc.json"
            meta = {
                "schema_name": base,
                "entity_type": getattr(self._metadata, "type", None) or "Entity",
                "description": getattr(self.schema, "title", None) or "",
            }
            schema_native = (
                self._schema.to_native()
                if hasattr(self._schema, "to_native")
                else (self._schema if isinstance(self._schema, dict) else {})
            )
            actions_export: dict[str, Any] = {}
            for name, action in (self._actions or {}).items():
                if hasattr(action, "to_dict"):
                    actions_export[name] = action.to_dict()
                elif hasattr(action, "to_native"):
                    actions_export[name] = action.to_native()
                else:
                    actions_export[name] = {"api_name": getattr(action, "api_name", name)}
            desc_dict = {"meta": meta, "schema": schema_native, "actions": actions_export}
            _json.save_file(desc_dict, desc_path, **_write_opts)
            written.append(desc_path)
        return written

    def load(self, path: str | Path, format: str | None = None, **options) -> None:
        """
        Load entity from storage in any supported format (from XWObject).
        Fully reuses XWData capabilities by loading a single XWData instance
        that contains merged schema, actions, and data, then extracting and restoring them.
        This provides all format support that XWData offers.
        Args:
            path: File path to load from
            format: Optional format name (auto-detected from extension if not provided)
            **options: Additional format-specific options
        """
        import asyncio
        from exonware.xwdata import XWData
        # Use XWData.load() to load - fully reuses xwdata format capabilities
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, XWData.load(path, format_hint=format, **options))
                    loaded_data = future.result()
            else:
                loaded_data = loop.run_until_complete(XWData.load(path, format_hint=format, **options))
        except RuntimeError:
            loaded_data = asyncio.run(XWData.load(path, format_hint=format, **options))
        # Extract dict from loaded XWData and restore object
        if isinstance(loaded_data, XWData):
            object_dict = loaded_data.to_native()
        else:
            object_dict = loaded_data
        # Restore object from dict
        if isinstance(object_dict, dict):
            self._from_dict(object_dict)
        else:
            raise XWEntityError(f"Invalid data format loaded from {path}: expected dict, got {type(object_dict).__name__}")
    # ==========================================================================
    # FORMAT-SPECIFIC EXPORT METHODS
    # ==========================================================================

    def to_json(self, path: (str | Path) | None = None, **options) -> str:
        """Export entity as JSON string or save to file. Reuses xwdata's serialization approach."""
        if path:
            self.save(path, format='json', **options)
            return str(path)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            data = self.to_dict()
            result = auto_serializer.detect_and_serialize(data, format_hint='JSON', **options)
            return result if isinstance(result, str) else result.decode('utf-8')

    def to_yaml(self, path: (str | Path) | None = None, **options) -> str:
        """Export entity as YAML string or save to file. Reuses xwdata's serialization approach."""
        if path:
            self.save(path, format='yaml', **options)
            return str(path)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            data = self.to_dict()
            result = auto_serializer.detect_and_serialize(data, format_hint='YAML', **options)
            return result if isinstance(result, str) else result.decode('utf-8')

    def to_toml(self, path: (str | Path) | None = None, **options) -> str:
        """Export entity as TOML string or save to file. Reuses xwdata's serialization approach."""
        if path:
            self.save(path, format='toml', **options)
            return str(path)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            data = self.to_dict()
            result = auto_serializer.detect_and_serialize(data, format_hint='TOML', **options)
            return result if isinstance(result, str) else result.decode('utf-8')

    def to_xml(self, path: (str | Path) | None = None, **options) -> str:
        """Export entity as XML string or save to file. Reuses xwdata's serialization approach."""
        if path:
            self.save(path, format='xml', **options)
            return str(path)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            data = self.to_dict()
            result = auto_serializer.detect_and_serialize(data, format_hint='XML', **options)
            return result if isinstance(result, str) else result.decode('utf-8')

    def to_format(self, format: str, path: (str | Path) | None = None, **options) -> str:
        """
        Export entity in any supported format.
        Fully reuses xwdata capabilities by using the same serialization registry
        that xwdata uses internally (xwsystem serialization registry).
        Args:
            format: Format name (json, yaml, toml, xml, msgpack, etc.)
            path: Optional file path (if not provided, returns string)
            **options: Format-specific options
        Returns:
            Serialized string if path not provided, file path string if path provided
        """
        if path:
            self.save(path, format=format, **options)
            return str(path)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            data = self.to_dict()
            result = auto_serializer.detect_and_serialize(data, format_hint=format.upper(), **options)
            return result if isinstance(result, str) else result.decode('utf-8')
    # ==========================================================================
    # FORMAT-SPECIFIC IMPORT METHODS
    # ==========================================================================

    def from_json(self, data: str | Path, **options) -> None:
        """Import entity from JSON string or file. Reuses xwdata's serialization approach."""
        import json as _stdlib_json
        from pathlib import Path
        if isinstance(data, (str, Path)) and Path(data).exists():
            self.load(data, format='json', **options)
        else:
            from exonware.xwsystem.io.serialization import get_serialization_registry
            registry = get_serialization_registry()
            serializer = registry.get_by_format('json')
            if serializer:
                loaded = serializer.decode(str(data), **options)
                if hasattr(loaded, "to_native") and callable(getattr(loaded, "to_native")):
                    loaded = loaded.to_native()
                elif hasattr(loaded, "to_dict") and callable(getattr(loaded, "to_dict")):
                    loaded = loaded.to_dict()
                # Root cause: some registry codecs (e.g. Lark-based) return parse trees
                # instead of dicts. Detect parse-tree shape and fallback to stdlib.
                if isinstance(loaded, dict) and {"children", "metadata", "type"}.issubset(loaded.keys()):
                    loaded = _stdlib_json.loads(str(data))
                if isinstance(loaded, dict):
                    self._from_dict(loaded)
                else:
                    raise XWEntityError(f"Invalid JSON data: expected dict, got {type(loaded).__name__}")
            else:
                raise XWEntityError("JSON serializer not available")

    def from_yaml(self, data: str | Path, **options) -> None:
        """Import entity from YAML string or file. Reuses xwdata's serialization approach."""
        from pathlib import Path
        if isinstance(data, (str, Path)) and Path(data).exists():
            self.load(data, format='yaml', **options)
        else:
            from exonware.xwsystem.io.serialization import get_serialization_registry
            registry = get_serialization_registry()
            serializer = registry.get_by_format('yaml')
            if serializer:
                loaded = serializer.decode(str(data), **options)
                if isinstance(loaded, dict):
                    self._from_dict(loaded)
                else:
                    raise XWEntityError(f"Invalid YAML data: expected dict, got {type(loaded).__name__}")
            else:
                raise XWEntityError("YAML serializer not available")

    def from_toml(self, data: str | Path, **options) -> None:
        """Import entity from TOML string or file. Reuses xwdata's serialization approach."""
        from pathlib import Path
        if isinstance(data, (str, Path)) and Path(data).exists():
            self.load(data, format='toml', **options)
        else:
            from exonware.xwsystem.io.serialization import get_serialization_registry
            registry = get_serialization_registry()
            serializer = registry.get_by_format('toml')
            if serializer:
                loaded = serializer.decode(str(data), **options)
                if isinstance(loaded, dict):
                    self._from_dict(loaded)
                else:
                    raise XWEntityError(f"Invalid TOML data: expected dict, got {type(loaded).__name__}")
            else:
                raise XWEntityError("TOML serializer not available")

    def from_xml(self, data: str | Path, **options) -> None:
        """Import entity from XML string or file. Reuses xwdata's serialization approach."""
        from pathlib import Path
        if isinstance(data, (str, Path)) and Path(data).exists():
            self.load(data, format='xml', **options)
        else:
            from exonware.xwsystem.io.serialization import get_serialization_registry
            registry = get_serialization_registry()
            serializer = registry.get_by_format('xml')
            if serializer:
                loaded = serializer.decode(str(data), **options)
                if isinstance(loaded, dict):
                    self._from_dict(loaded)
                else:
                    raise XWEntityError(f"Invalid XML data: expected dict, got {type(loaded).__name__}")
            else:
                raise XWEntityError("XML serializer not available")

    def from_format(self, format: str, data: str | Path, **options) -> None:
        """
        Import entity from any supported format.
        Fully reuses xwdata capabilities by using the same serialization registry
        that xwdata uses internally (xwsystem serialization registry).
        Args:
            format: Format name (json, yaml, toml, xml, msgpack, etc.)
            data: Data string or file path
            **options: Format-specific options
        """
        from pathlib import Path
        if isinstance(data, (str, Path)) and Path(data).exists():
            self.load(data, format=format, **options)
        else:
            from exonware.xwsystem.io.serialization.auto_serializer import AutoSerializer
            auto_serializer = AutoSerializer()
            loaded = auto_serializer.detect_and_deserialize(str(data), format_hint=format.upper(), **options)
            if isinstance(loaded, dict):
                self._from_dict(loaded)
            else:
                raise XWEntityError(f"Invalid {format} data: expected dict, got {type(loaded).__name__}")

    def to_native(self) -> EntityData:
        """
        Get entity as native dictionary (public API).
        Returns:
            Entity data dictionary
        """
        return self._to_native()
    # ==========================================================================
    # PERFORMANCE OPTIMIZATION (public API from XWEntity)
    # ==========================================================================

    def optimize_for_access(self) -> "XWEntity":
        """
        Optimize the entity for fast access operations (public API).
        Returns:
            Self for chaining
        """
        self._optimize_for_access()
        return self

    def optimize_for_validation(self) -> "XWEntity":
        """
        Optimize the entity for fast validation operations (public API).
        Returns:
            Self for chaining
        """
        self._optimize_for_validation()
        return self

    def optimize_memory(self) -> "XWEntity":
        """
        Optimize memory usage (public API).
        Returns:
            Self for chaining
        """
        self._optimize_memory()
        return self

    def get_memory_usage(self) -> int:
        """
        Get the memory usage in bytes (public API).
        Returns:
            Estimated memory usage in bytes
        """
        return self._get_memory_usage()

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get performance statistics (public API).
        Returns:
            Dictionary with performance statistics
        """
        return super().get_performance_stats()
    # ==========================================================================
    # EXTENSIBILITY (public API from XWEntity)
    # ==========================================================================

    def register_extension(self, name: str, extension: Any) -> "XWEntity":
        """
        Register an extension with the entity (public API).
        Args:
            name: Extension name
            extension: Extension object
        Returns:
            Self for chaining
        """
        super().register_extension(name, extension)
        return self

    def get_extension(self, name: str) -> Any | None:
        """
        Get an extension by name (public API).
        Args:
            name: Extension name
        Returns:
            Extension object or None if not found
        """
        return super().get_extension(name)

    def has_extension(self, name: str) -> bool:
        """
        Check if an extension exists (public API).
        Args:
            name: Extension name
        Returns:
            True if extension exists
        """
        return super().has_extension(name)

    def list_extensions(self) -> list[str]:
        """
        List all registered extensions (public API).
        Returns:
            List of extension names
        """
        return super().list_extensions()

    def remove_extension(self, name: str) -> bool:
        """
        Remove an extension by name (public API).
        Args:
            name: Extension name
        Returns:
            True if extension was removed, False if not found
        """
        return super().remove_extension(name)

    def has_extension_type(self, extension_type: str) -> bool:
        """
        Check if an extension of a specific type exists (public API).
        Args:
            extension_type: Extension type name to search for
        Returns:
            True if extension of type exists
        """
        return super().has_extension_type(extension_type)
    # ==========================================================================
    # ATTRIBUTE DELEGATION (__getattr__ from XWEntity)
    # ==========================================================================

    def __getattr__(self, name: str) -> Any:
        """
        Delegate attribute access to data properties and actions.
        Priority:
        1. Check if it's a registered action -> execute it
        2. Check if it's in entity data -> return data value
        3. Raise AttributeError
        Examples:
            >>> entity.uid  # Returns entity.data.get("uid")
            >>> entity.add_user(a, b)  # Executes entity.execute_action("add_user", a, b)
        """
        # First, check if it's a registered action
        if name in self._actions:
            action = self._actions[name]
            # Return a callable that executes the action
            def action_executor(*args, **kwargs):
                # execute_action handles parameter validation automatically
                return self.execute_action(name, *args, **kwargs)
            # Preserve action metadata for introspection
            action_executor._is_action = True
            action_executor._action_name = name
            action_executor._action_obj = action
            return action_executor
        # Second, check if it's in entity data
        if self._data is not None:
            # Try to get from data
            try:
                value = self.get(name)
                if value is not None:
                    return value
            except Exception:
                pass
        # Not found - raise AttributeError
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'. "
            f"Available actions: {list(self._actions.keys())}. "
            f"Use entity.data.get('{name}') to access data properties."
        )
# ==============================================================================
# EXPORTS
# ==============================================================================
__all__ = [
    "XWEntity",
]
