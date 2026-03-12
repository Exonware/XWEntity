#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/base.py
XWEntity Abstract Base Classes
This module defines abstract base classes that extend interfaces from contracts.py.
Following GUIDE_DEV.md: All abstract classes start with 'A' and extend 'I' interfaces.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 08-Nov-2025
"""

from abc import ABC, abstractmethod
from typing import Any, Callable
from datetime import datetime
from pathlib import Path
import asyncio
import threading
import uuid
from collections.abc import MutableMapping
from exonware.xwsystem import get_logger
from exonware.xwdata import XWData
# Import XWAction for type checking and validation
from exonware.xwaction import XWAction
from exonware.xwsystem.shared import XWObject
from .contracts import (
    # Entity contracts
    IEntity,
    IEntityState,
    IEntitySerialization,
)
from .defs import (
    ObjectState,
    ObjectID,
    ObjectType,
    ObjectData,
    DEFAULT_OBJECT_TYPE,
    DEFAULT_STATE,
    DEFAULT_VERSION,
    STATE_TRANSITIONS,
    # Entity types (merged)
    EntityState,
    EntityID,
    EntityType,
    EntityData,
    DEFAULT_ENTITY_TYPE,
    DEFAULT_CACHE_SIZE,
    DEFAULT_THREAD_SAFETY,
    DEFAULT_PERFORMANCE_MODE,
    PerformanceMode,
)
from .errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityDataError,
)
from .config import get_config
from exonware.xwsystem import LRUCache
logger = get_logger(__name__)
# Sentinel values for correct caching semantics.
# - `_MISSING` is used to detect "path not found" without conflating it with a real `None` value.
# - `_CACHED_NONE` is stored in caches to represent a real `None` value (since cache.get() uses None as "miss").
_MISSING = object()
_CACHED_NONE = object()
# Global entity-level cache using shared xwsystem LRUCache
_entity_cache: LRUCache | None = None


def get_entity_cache() -> LRUCache:
    """
    Get global cache used by XWEntity/AEntity for data/path lookups.
    Reuses exonware.xwsystem.caching.lru_cache.LRUCache as the backing store.
    Capacity is driven by XWEntityConfig.cache_size.
    """
    global _entity_cache
    if _entity_cache is None:
        cfg = get_config()
        capacity = getattr(cfg, "cache_size", 1024)
        _entity_cache = LRUCache(capacity=capacity, name="xwentity-global-cache")
    return _entity_cache


def clear_entity_cache() -> None:
    """Clear the global entity cache."""
    global _entity_cache
    if _entity_cache is not None:
        _entity_cache.clear()
    # ==========================================================================
    # SCHEMA OPERATIONS
    # ==========================================================================
    def validate(self) -> bool:
        """
        Validate data against schema using XWSchema.
        Uses XWSchema.validate_sync() which supports XWData directly.
        This ensures full reuse of xwschema validation capabilities.
        """
        if not self._schema:
            return True  # No schema means no validation
        if self._data is None:
            return False
        # Use XWSchema.validate_sync() - fully reuses xwschema validation
        if hasattr(self._schema, "validate_sync"):
            is_valid, _errors = self._schema.validate_sync(self._data)
            return bool(is_valid)
        if hasattr(self._schema, "validate"):
            # Async validate() is not supported from sync object API.
            raise XWEntityValidationError(
                "Schema validation requires async context. Use XWSchema.validate_sync()."
            )
        logger.warning("Schema does not support validation")
        return True
    # ==========================================================================
    # ACTIONS
    # ==========================================================================
    def execute_action(self, action_name: str, **kwargs) -> Any:
        """
        Execute a registered action with full XWAction validation and features.
        This method uses XWAction.execute() which provides:
        - Input validation: Validates inputs against XWAction.in_types schemas using XWSchema
        - Output validation: Validates outputs against XWAction.out_types schemas using XWSchema
        - Permission checking: Validates user roles and permissions
        - Handler pipeline: BEFORE, AFTER, ERROR, FINALLY handlers
        - XWQuery support: Actions can use XWAction.query() internally for data querying
        Args:
            action_name: Name of the action to execute
            **kwargs: Keyword arguments (will be validated against action's in_types schemas)
        Returns:
            Action result (validated against action's out_types schemas if defined)
        Raises:
            XWEntityActionError: If action not found or execution fails
            XWEntityValidationError: If input/output validation fails
        """
        if action_name not in self._actions:
            raise XWEntityActionError(
                f"Action '{action_name}' not found",
                action_name=action_name
            )
        action = self._actions[action_name]
        # Extract XWAction object if action is a decorated method
        from exonware.xwaction import XWAction
        xwaction_obj = None
        if callable(action) and hasattr(action, 'xwaction'):
            xwaction_obj = getattr(action, 'xwaction', None)
        elif XWAction and isinstance(action, XWAction):
            xwaction_obj = action
        # Handle different action types
        from exonware.xwaction import ActionContext
        ctx = ActionContext(
            actor="object",
            source="xwobject",
            metadata={"action_name": action_name}
        )
        # PRIORITY 1: Use XWAction.execute() - fully reuses xwaction execution pipeline
        if xwaction_obj and hasattr(xwaction_obj, 'execute'):
            result = xwaction_obj.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 2: Action itself is XWAction (has execute method)
        elif XWAction and isinstance(action, XWAction) and hasattr(action, 'execute'):
            result = action.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 3: Action has execute method
        elif hasattr(action, 'execute') and callable(getattr(action, 'execute', None)):
            result = action.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 4: Regular callable
        elif callable(action):
            return action(self, **kwargs)
        else:
            raise XWEntityActionError(
                f"Action '{action_name}' is not callable",
                action_name=action_name
            )
    def list_actions(self) -> list[str]:
        """List available action names."""
        return list(self._actions.keys())
    def register_action(self, action: Any) -> None:  # XWAction type
        """
        Register an action for this object.
        Normalizes actions at registration time:
        - Decorated methods (wrapper.xwaction) -> extracts XWAction instance
        - XWAction instances -> stores directly
        - Other callables -> stores as-is
        """
        from exonware.xwaction import XWAction
        # Normalize: Extract XWAction object if it's a decorated method
        if callable(action) and hasattr(action, 'xwaction') and XWAction is not None:
            xwaction_obj = getattr(action, 'xwaction', None)
            if isinstance(xwaction_obj, XWAction):
                action = xwaction_obj  # Store XWAction instance directly
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
    # SERIALIZATION (IObject)
    # ==========================================================================
    def to_dict(self, include_schema: bool = True) -> ObjectData:
        """Export object as dictionary. Set include_schema=False when schema lives elsewhere (e.g. .desc file)."""
        result: ObjectData = {
            "_metadata": self._metadata.to_dict(),
        }
        if self._data and hasattr(self._data, 'to_native'):
            result["_data"] = self._data.to_native()
        else:
            result["_data"] = {}
        if include_schema and self._schema:
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
    def from_dict(self, data: ObjectData) -> None:
        """
        Import object from dictionary.
        Handles both:
        1. Full object structure: {"_metadata": {...}, "_data": {...}, "_schema": {...}}
        2. Plain data structure: {"name": "Alice", "age": 30} (treats as data)
        """
        # Check if this is a full object structure (has _metadata or _data keys)
        if "_metadata" in data or "_data" in data:
            # Full object structure
            if "_metadata" in data:
                self._metadata.from_dict(data["_metadata"])
                # Sync object uid from metadata so both id and uid are restored (XWObject subclasses)
                if hasattr(self, "_uid"):
                    self._uid = self._metadata.uid
            if "_data" in data:
                # Data initialization depends on subclass
                self._init_data_from_dict(data["_data"])
        else:
            # Plain data structure - treat entire dict as data
            self._init_data_from_dict(data)
        # Optional schema restore
        if "_schema" in data and data["_schema"] is not None:
            from exonware.xwschema import XWSchema
            try:
                if isinstance(data["_schema"], dict):
                    self._schema = XWSchema(data["_schema"])
            except Exception as e:
                raise XWEntityError(f"Failed to restore schema from dict: {e}", cause=e)
        # Optional actions restore
        if "_actions" in data and isinstance(data["_actions"], dict):
            from exonware.xwaction import XWAction
            try:
                for _name, action_payload in data["_actions"].items():
                    if isinstance(action_payload, dict):
                        try:
                            action = XWAction.from_native(action_payload)
                            self.register_action(action)
                        except (ValueError, AttributeError) as action_error:
                            # Actions with local/closure function references may not be restorable
                            logger.warning(
                                f"Failed to restore action '{_name}' from dict: {action_error}. "
                                f"This is expected for actions with local function references."
                            )
            except Exception as e:
                if "Cannot resolve function" not in str(e):
                    raise XWEntityError(f"Failed to restore actions from dict: {e}", cause=e)
                else:
                    logger.warning(f"Some actions could not be restored due to function resolution: {e}")
    @abstractmethod
    def _init_data_from_dict(self, data: ObjectData) -> None:
        """Initialize data from dictionary. Must be implemented by subclass."""
        pass
# ==============================================================================
# ENTITY METADATA
# ==============================================================================


class XWEntityMetadata:
    """
    Internal metadata management for entities.
    Manages entity identity (id + uid), state, versioning, and timestamps.
    Both id and uid are always present and used: id = user/programmer-set for
    finding/storing; uid = system auto-generated so id is never duplicated.
    """

    def __init__(self, entity_type: str | None = None):
        """Initialize entity metadata. uid is auto-generated; id is unset until user sets it."""
        self._id: EntityID = ""  # user/programmer-set for finding/storing
        self._uid: str = str(uuid.uuid4())  # system auto-generated, ensures uniqueness
        self._type: EntityType = entity_type or DEFAULT_ENTITY_TYPE
        self._state: EntityState = DEFAULT_STATE
        self._version: int = DEFAULT_VERSION
        self._created_at: datetime = datetime.now()
        self._updated_at: datetime = self._created_at
        self._deleted_at: datetime | None = None
    @property

    def id(self) -> EntityID:
        """User/programmer-set identifier for finding and storing."""
        return self._id
    @property

    def uid(self) -> str:
        """System auto-generated unique identifier. Never the same as id."""
        return self._uid
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
    @property

    def deleted_at(self) -> datetime | None:
        """Get deletion timestamp (None if not deleted)."""
        return self._deleted_at
    @deleted_at.setter

    def deleted_at(self, value: datetime | None) -> None:
        """Set deletion timestamp."""
        self._deleted_at = value
        if value is not None:
            self._updated_at = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Convert metadata to dictionary. Always includes both id and uid."""
        result = {
            "id": self._id,
            "uid": self._uid,
            "type": self._type,
            "state": str(self._state),
            "version": self._version,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
        }
        if self._deleted_at is not None:
            result["deleted_at"] = self._deleted_at.isoformat()
        return result

    def from_dict(self, data: dict[str, Any]) -> None:
        """Load metadata from dictionary. Restores both id and uid."""
        self._id = data.get("id", "")
        self._uid = data.get("uid", str(uuid.uuid4()))
        self._type = data.get("type", DEFAULT_ENTITY_TYPE)
        self._state = EntityState(data.get("state", DEFAULT_STATE.value))
        self._version = data.get("version", DEFAULT_VERSION)
        if "created_at" in data:
            raw = data["created_at"]
            if isinstance(raw, str):
                self._created_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if "updated_at" in data:
            raw = data["updated_at"]
            if isinstance(raw, str):
                self._updated_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if "deleted_at" in data:
            raw = data["deleted_at"]
            if isinstance(raw, str):
                self._deleted_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
# ==============================================================================
# DATA ENGINE (Option G: shared base for entity, collection, group)
# ==============================================================================


class ADataBackedObject(ABC):
    """
    Shared data engine: one place for XWData-backed serialization.

    AEntity, ACollection, and AGroup use this to hold serializable state in
    _data_backed (XWData). to_dict() = _data_backed.to_native(); from_dict()
    restores _data_backed and calls _apply_data_from_dict(). Subclasses
    implement _build_data_payload() and optionally _apply_data_from_dict().
    """

    _data_backed: Any  # XWData

    @abstractmethod
    def _build_data_payload(self, **kwargs: Any) -> dict[str, Any]:
        """Return current state as dict. Subclass implements. kwargs (e.g. include_schema) passed through."""
        ...

    def _apply_data_from_dict(self, data: dict[str, Any]) -> None:
        """Restore scalar state from dict. Subclass overrides as needed."""
        pass

    def _init_data_backed(self) -> None:
        """Call from subclass __init__. Sets _data_backed from _build_data_payload()."""
        self._data_backed = XWData.from_native(self._build_data_payload())

    def _sync_data(self, **kwargs: Any) -> None:
        """Sync _data_backed from current state. kwargs passed to _build_data_payload."""
        self._data_backed = XWData.from_native(self._build_data_payload(**kwargs))

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Export as dict (Option G: single source = _data_backed.to_native()). kwargs passed to _sync_data/_build_data_payload."""
        self._sync_data(**kwargs)
        out = self._data_backed.to_native()
        return out if isinstance(out, dict) else {}

    def from_dict(self, data: dict[str, Any]) -> None:
        """Restore from dict; _data_backed set, then _apply_data_from_dict."""
        self._data_backed = XWData.from_native(dict(data))
        native = self._data_backed.to_native()
        if isinstance(native, dict):
            self._apply_data_from_dict(native)


# ==============================================================================
# ABSTRACT COLLECTION / GROUP
# ==============================================================================


class ACollection(ADataBackedObject):
    """
    Abstract base for lightweight logical collections.
    Type parameter is for static typing only; concrete classes (e.g. XWCollection[T])
    use this non-generic base to avoid MRO conflict with XWObject (ABC vs Generic).
    """

    def __init__(self, entity_type: type[Any] | str) -> None:
        self._entity_type: type[Any] | str = entity_type

    @property
    def entity_type(self) -> type[Any] | str:
        """Get the entity type managed by this collection."""
        return self._entity_type


class AGroup(ADataBackedObject):
    """
    Abstract base for lightweight logical groups.

    This base does not impose storage semantics; it exists to provide a
    common type for group implementations (like XWGroup).
    """

    pass


# ==============================================================================
# ABSTRACT ENTITY
# ==============================================================================


class AEntity(ADataBackedObject, XWObject, IEntity, IEntityState, IEntitySerialization):
    """
    Abstract base class for all entity implementations.
    Provides default implementations for common functionality while requiring
    subclasses to implement core data operations. Manages metadata, caching,
    performance stats, and state transitions.
    """

    def __init__(
        self,
        schema: Any | None = None,  # XWSchema type
        data: Any | None = None,  # XWData type or dict
        entity_type: str | None = None,
        config: Any | None = None,  # XWEntityConfig type
        object_id: str | None = None,
        **kwargs,
    ):
        """
        Initialize abstract entity.
        Args:
            schema: Optional entity schema
            data: Optional initial data (dict or XWData)
            entity_type: Optional entity type name
            config: Optional entity configuration
            object_id: Optional id for XWObject (passed to super); subclasses may pass from data.
        """
        super().__init__(object_id=object_id or "")
        # Core components
        self._metadata = XWEntityMetadata(entity_type)
        self._metadata._uid = self._uid
        self._created_at = self._metadata._created_at
        self._updated_at = self._metadata._updated_at
        self._schema = schema
        self._config = config or get_config()
        # Data will be initialized by subclass
        self._data: Any | None = None  # XWData type
        # Actions storage (override XWObject base)
        self._actions: dict[str, Any] = {}
        # Performance optimizations
        self._cache: dict[str, Any] = {}
        self._cache_size = self._config.cache_size if hasattr(self._config, 'cache_size') else DEFAULT_CACHE_SIZE
        self._global_cache = get_entity_cache()
        self._schema_cache: dict[str, Any] | None = None
        self._performance_stats: dict[str, Any] = {
            "access_count": 0,
            "validation_count": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }
        # Extensibility
        self._extensions: dict[str, Any] = {}
        # Thread safety
        enable_thread_safety = (
            self._config.enable_thread_safety
            if hasattr(self._config, 'enable_thread_safety')
            else False
        )
        self._lock = threading.RLock() if enable_thread_safety else None
        self._init_data_backed()
    # ==========================================================================
    # CORE PROPERTIES (IEntity) – id/uid from XWObject; timestamps mirrored in __init__
    # ==========================================================================
    @property
    def id(self) -> EntityID:
        """Entity identifier. Returns user-set id when present, else uid for uniqueness."""
        user_id = self._metadata._id if self._metadata else (getattr(self, "_id", None) or "")
        return user_id if user_id else (self._metadata.uid if self._metadata else getattr(self, "_uid", "") or "")

    @property

    def type(self) -> EntityType:
        """Get the entity type name."""
        return self._metadata.type
    @property

    def schema(self) -> Any | None:  # XWSchema type
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
        """Get the creation timestamp (mirrored from _metadata in __init__)."""
        return self._created_at
    @property

    def updated_at(self) -> datetime:
        """Get the last update timestamp (mirrored from _metadata in __init__)."""
        return self._updated_at
    # ==========================================================================
    # DATA OPERATIONS (IEntity)
    # ==========================================================================

    def _get(self, path: str, default: Any = None) -> Any:
        """Get value at path."""
        self._performance_stats["access_count"] += 1
        # Use unique cache namespace per entity (avoid cross-entity pollution when id is empty)
        _entity_cache_key = self.id or getattr(self, "_uid", None) or id(self)
        cache_key = f"get:{_entity_cache_key}:{path}"
        cached = self._global_cache.get(cache_key)
        if cached is not None:
            self._performance_stats["cache_hits"] += 1
            return None if cached is _CACHED_NONE else cached
        # Also check local cache
        if cache_key in self._cache:
            self._performance_stats["cache_hits"] += 1
            local_cached = self._cache[cache_key]
            return None if local_cached is _CACHED_NONE else local_cached
        self._performance_stats["cache_misses"] += 1
        # Delegate to data
        if self._data is None:
            return default
        # IMPORTANT: preserve `default` semantics.
        # We must not cache "default" results for missing paths, because different callers
        # may pass different defaults (including None).
        value = self._data_get_sync(path, _MISSING)
        if value is _MISSING:
            return default
        # Cache found value (both local and global). Represent real None with sentinel.
        to_cache = _CACHED_NONE if value is None else value
        if len(self._cache) < self._cache_size:
            self._cache[cache_key] = to_cache
        self._global_cache.put(cache_key, to_cache)
        return value

    def _data_get_sync(self, path: str, default: Any = None) -> Any:
        """
        Synchronous get over XWData - FULLY DELEGATES to XWData.
        Uses XWData.get() which provides:
        - Path-based access (e.g., "user.profile.name")
        - Query support via xwquery
        - Format-agnostic data access
        - Caching and performance optimizations
        Uses XWDataNode's sync methods first, then falls back to XWData's async methods.
        NO manual dict navigation - always uses XWData capabilities.
        """
        # Prefer XWDataNode sync navigation (fast path) - DELEGATE to XWData
        node = getattr(self._data, "_node", None)
        if node is not None and hasattr(node, "get_value_at_path"):
            return node.get_value_at_path(path, default)
        # Fallback: Use XWData's async get() method via sync bridge
        if isinstance(self._data, XWData) and hasattr(self._data, "get"):
            try:
                loop = asyncio.get_running_loop()
                logger.debug("Cannot use async get() in sync context with running loop")
                return default
            except RuntimeError:
                return asyncio.run(self._data.get(path, default))
        # Last resort: if data is a plain dict, use simple access
        if isinstance(self._data, dict):
            # Use XWDataNode's navigation logic (reuse, don't duplicate)
            from exonware.xwdata.data.node import XWDataNode
            temp_node = XWDataNode(data=self._data)
            return temp_node.get_value_at_path(path, default)
        return default

    def _set(self, path: str, value: Any) -> None:
        """Set value at path."""
        if self._lock:
            with self._lock:
                self._set_impl(path, value)
        else:
            self._set_impl(path, value)

    def _set_impl(self, path: str, value: Any) -> None:
        """
        Internal set implementation - FULLY DELEGATES to XWData.
        Uses XWData.set() which provides:
        - Path-based updates (e.g., "user.profile.name")
        - Immutability support via XWNode
        - Automatic cache invalidation
        - Format-agnostic data updates
        Uses XWDataNode's sync methods first, then falls back to XWData's async methods.
        NO manual dict updates - always uses XWData capabilities.
        """
        if self._data is None:
            raise XWEntityError("Data not initialized")
        # Prefer XWDataNode sync mutation (COW) - DELEGATE to XWData
        node = getattr(self._data, "_node", None)
        if node is not None and hasattr(node, "set_value_at_path"):
            new_node = node.set_value_at_path(path, value)
            self._data = self._rebuild_xwdata_from_node(new_node)
        elif isinstance(self._data, XWData) and hasattr(self._data, "set"):
            # Fallback: Use XWData's async set() method via sync bridge
            try:
                loop = asyncio.get_running_loop()
                logger.debug("Cannot use async set() in sync context with running loop")
                raise XWEntityError("Cannot set value: async context required. Use async API.")
            except RuntimeError:
                asyncio.run(self._data.set(path, value))
                node = getattr(self._data, "_node", None)
                if node:
                    self._data = self._rebuild_xwdata_from_node(node)
        elif isinstance(self._data, dict):
            # Last resort: if data is a plain dict, use XWDataNode's logic (reuse, don't duplicate)
            from exonware.xwdata.data.node import XWDataNode
            temp_node = XWDataNode(data=self._data)
            new_node = temp_node.set_value_at_path(path, value)
            self._data = new_node.to_native()
        else:
            raise XWEntityError("Cannot set value: data does not support mutation")
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change

    def _rebuild_xwdata_from_node(self, new_node: Any) -> Any:
        """
        Rebuild an XWData instance from a new XWDataNode without using async APIs.
        This keeps XWEntity's sync API usable while preserving XWData's COW behavior.
        """
        old = self._data
        if old is None or not isinstance(old, XWData):
            return XWData(new_node)  # type: ignore[arg-type]
        instance = XWData.__new__(XWData)
        instance._config = old._config
        instance._engine = old._engine
        instance._node = new_node
        instance._metadata = getattr(new_node, "metadata", {})
        return instance

    def _delete(self, path: str) -> None:
        """Delete value at path."""
        if self._lock:
            with self._lock:
                self._delete_impl(path)
        else:
            self._delete_impl(path)

    def _delete_impl(self, path: str) -> None:
        """
        Internal delete implementation - FULLY DELEGATES to XWData.
        Uses XWData.delete() which provides:
        - Path-based deletion (e.g., "user.profile.name")
        - Immutability support via XWNode
        - Automatic cache invalidation
        - Format-agnostic data deletion
        Uses XWDataNode's sync methods first, then falls back to XWData's async methods.
        NO manual dict deletion - always uses XWData capabilities.
        """
        if self._data is None:
            raise XWEntityError("Data not initialized")
        # Prefer XWDataNode sync deletion - DELEGATE to XWData
        node = getattr(self._data, "_node", None)
        if node is not None and hasattr(node, "delete_at_path"):
            new_node = node.delete_at_path(path)
            self._data = self._rebuild_xwdata_from_node(new_node)
        elif isinstance(self._data, XWData) and hasattr(self._data, "delete"):
            # Fallback: Use XWData's async delete() method via sync bridge
            try:
                loop = asyncio.get_running_loop()
                logger.debug("Cannot use async delete() in sync context with running loop")
                raise XWEntityError("Cannot delete value: async context required. Use async API.")
            except RuntimeError:
                asyncio.run(self._data.delete(path))
                node = getattr(self._data, "_node", None)
                if node:
                    self._data = self._rebuild_xwdata_from_node(node)
        elif isinstance(self._data, dict):
            # Last resort: if data is a plain dict, use XWDataNode's logic (reuse, don't duplicate)
            from exonware.xwdata.data.node import XWDataNode
            temp_node = XWDataNode(data=self._data)
            new_node = temp_node.delete_at_path(path)
            self._data = new_node.to_native()
        else:
            raise XWEntityError("Cannot delete value: data does not support mutation")
        self._metadata.update_version()
        self._clear_cache()  # Invalidate cache on data change

    def _update(self, updates: EntityData) -> None:
        """Update multiple values."""
        for path, value in updates.items():
            self._set(path, value)

    def _validate(self) -> bool:
        """
        Validate data against schema using XWSchema.
        Uses XWSchema.validate_sync() which supports XWData directly.
        This ensures full reuse of xwschema validation capabilities.
        """
        self._performance_stats["validation_count"] += 1
        if not self._schema:
            return True  # No schema means no validation
        if self._data is None:
            return False
        # Use XWSchema.validate_sync() - fully reuses xwschema validation
        # This method supports XWData directly, so no conversion needed
        if hasattr(self._schema, "validate_sync"):
            is_valid, _errors = self._schema.validate_sync(self._data)
            return bool(is_valid)
        if hasattr(self._schema, "validate"):
            # Async validate() is not supported from sync entity API.
            raise XWEntityValidationError(
                "Schema validation requires async context. Use XWSchema.validate_sync() or validate via XWEntity.validate_issues()."
            )
        logger.warning("Schema does not support validation")
        return True

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
    @abstractmethod

    def _init_data_from_dict(self, data: EntityData) -> None:
        """Initialize data from dictionary. Must be implemented by subclass."""
        pass
    # ==========================================================================
    # ACTIONS (dict with action name as key, IAction as value)
    # ==========================================================================

    def _execute_action(self, action_name: str, *args, **kwargs) -> Any:
        """
        Execute a registered action with parameter validation.
        Args:
            action_name: Name of the action to execute
            *args: Positional arguments (will be converted to kwargs based on function signature)
            **kwargs: Keyword arguments
        Returns:
            Action result
        Raises:
            XWEntityActionError: If action not found or execution fails
            XWEntityValidationError: If parameter validation fails
        """
        if action_name not in self._actions:
            raise XWEntityActionError(
                f"Action '{action_name}' not found",
                action_name=action_name
            )
        action = self._actions[action_name]
        # Extract XWAction object if action is a decorated method
        xwaction_obj = None
        if callable(action) and hasattr(action, 'xwaction'):
            xwaction_obj = getattr(action, 'xwaction', None)
        elif XWAction and isinstance(action, XWAction):
            xwaction_obj = action
        # Convert *args to **kwargs if we have positional arguments
        # This is needed because XWAction.execute() only accepts **kwargs
        # The instance (self/obj) is passed separately, so *args should map to parameters after instance
        if args and (xwaction_obj or callable(action)):
            import inspect
            # Get the function signature (either from XWAction.func or the action itself)
            func = None
            if xwaction_obj and hasattr(xwaction_obj, 'func'):
                func = xwaction_obj.func
            elif callable(action):
                func = action
            if func:
                try:
                    sig = inspect.signature(func)
                    # Get parameter names, excluding 'self'/'obj' (which is passed as instance)
                    param_names = list(sig.parameters.keys())
                    # Remove 'self' or 'obj' from parameter names (they're passed as instance)
                    if param_names and param_names[0] in ('self', 'obj'):
                        param_names = param_names[1:]
                    # Map positional args to parameter names (after instance)
                    for i, arg_value in enumerate(args):
                        if i < len(param_names):
                            param_name = param_names[i]
                            if param_name not in kwargs:  # Don't override explicit kwargs
                                kwargs[param_name] = arg_value
                except Exception:
                    # Conversion can fail - fall through to regular callable path
                    pass
        # Handle different action types
        # CRITICAL: Always use XWAction.execute() if available (has validation built-in)
        from exonware.xwaction import ActionContext
        ctx = ActionContext(
            actor="entity",
            source="xwentity",
            metadata={"action_name": action_name}
        )
        # PRIORITY 1: Use XWAction.execute() - fully reuses xwaction execution pipeline
        if xwaction_obj and hasattr(xwaction_obj, 'execute'):
            result = xwaction_obj.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 2: Action itself is XWAction (has execute method)
        elif XWAction and isinstance(action, XWAction) and hasattr(action, 'execute'):
            result = action.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 3: Action has execute method
        elif hasattr(action, 'execute') and callable(getattr(action, 'execute', None)):
            result = action.execute(context=ctx, instance=self, **kwargs)
            # Extract data from ActionResult if it's an ActionResult object
            if hasattr(result, 'data'):
                return result.data
            return result
        # PRIORITY 4: Regular callable - validate manually if we have XWAction object
        elif callable(action):
            # If we have XWAction object with validation schemas, validate before calling
            if xwaction_obj and hasattr(xwaction_obj, 'in_types') and xwaction_obj.in_types:
                # Validate inputs before calling
                from exonware.xwaction.core.validation import action_validator
                validation_result = action_validator.validate_inputs(xwaction_obj, kwargs)
                if not validation_result.valid:
                    raise XWEntityValidationError(
                        f"Action parameter validation failed: {', '.join(validation_result.errors)}",
                        cause=None
                    )
            # Execute the callable
            return action(self, *args, **kwargs)
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
        """
        Register an action for this entity.
        Normalizes actions at registration time:
        - Decorated methods (wrapper.xwaction) -> extracts XWAction instance
        - XWAction instances -> stores directly
        - Other callables -> stores as-is
        """
        # Normalize: Extract XWAction object if it's a decorated method
        if callable(action) and hasattr(action, 'xwaction') and XWAction is not None:
            xwaction_obj = getattr(action, 'xwaction', None)
            if isinstance(xwaction_obj, XWAction):
                action = xwaction_obj  # Store XWAction instance directly
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
        logger.debug(f"Entity {self.id} transitioned to {target_state}")

    def _can_transition_to(self, target_state: EntityState) -> bool:
        """Check if state transition is allowed."""
        current_state = self._metadata.state
        allowed_transitions = STATE_TRANSITIONS.get(current_state, [])
        return target_state in allowed_transitions

    def _update_version(self) -> None:
        """Update the entity version."""
        self._metadata.update_version()
    # ==========================================================================
    # SERIALIZATION (IEntitySerialization) – Option G: ADataBackedObject
    # ==========================================================================

    def _build_data_payload(self, **kwargs: Any) -> dict[str, Any]:
        """Build entity dict for _data_backed (metadata, data, optional schema, actions)."""
        include_schema = kwargs.get("include_schema", True)
        result: dict[str, Any] = {
            "_metadata": self._metadata.to_dict(),
            "_data": self._data.to_native() if self._data and hasattr(self._data, "to_native") else {},
        }
        if include_schema and self._schema:
            if hasattr(self._schema, "to_dict"):
                result["_schema"] = self._schema.to_dict()
            elif hasattr(self._schema, "to_native"):
                result["_schema"] = self._schema.to_native()
        if self._actions:
            result["_actions"] = {
                name: self._export_action(action)
                for name, action in self._actions.items()
            }
        return result

    def _apply_data_from_dict(self, data: dict[str, Any]) -> None:
        """Restore entity state from dict (metadata, data, schema, actions)."""
        if "_metadata" in data:
            self._metadata.from_dict(data["_metadata"])
            if hasattr(self, "_uid"):
                self._uid = self._metadata.uid
        if "_data" in data:
            self._init_data_from_dict(data["_data"])
        if "_schema" in data and data["_schema"] is not None:
            from exonware.xwschema import XWSchema
            try:
                if isinstance(data["_schema"], dict):
                    self._schema = XWSchema(data["_schema"])
            except Exception as e:
                raise XWEntityError(f"Failed to restore schema from dict: {e}", cause=e)
        if "_actions" in data and isinstance(data["_actions"], dict):
            for _name, action_payload in data["_actions"].items():
                if isinstance(action_payload, dict):
                    try:
                        action = XWAction.from_native(action_payload)
                        self.register_action(action)
                    except (ValueError, AttributeError):
                        logger.warning(
                            "Failed to restore action %r from dict (expected for local refs).",
                            _name,
                        )

    def to_dict(self, include_schema: bool = True) -> dict[str, Any]:
        """Export entity as dictionary. Pass include_schema to _data_backed payload."""
        return super().to_dict(include_schema=include_schema)

    def _to_native(self) -> EntityData:
        """Export entity as native dict (for to_native() and IEntity-style roundtrip)."""
        return self.to_dict()

    def _from_dict(self, data: dict[str, Any]) -> None:
        """In-place restore from full entity dict. Used by XWEntity.from_dict and load."""
        if "_metadata" in data or "_data" in data or "_schema" in data or "_actions" in data:
            self._apply_data_from_dict(data)
            self._sync_data()
        else:
            # Plain data dict: set data and sync _data_backed
            self._init_data_from_dict(data)
            self._sync_data()
        # Clear cache after data change to avoid stale get() results (root cause: cache collision when id() reused)
        self._clear_cache()
    @abstractmethod

    def save(self, *args, **kwargs) -> None:
        """
        Save entity to storage.
        Must be implemented by subclass.
        """
        pass
    @abstractmethod

    def load(self, *args, **kwargs) -> None:
        """
        Load entity from storage.
        Must be implemented by subclass.
        """
        pass
    # ==========================================================================
    # PERFORMANCE OPTIMIZATION
    # ==========================================================================

    def _optimize_for_access(self) -> None:
        """Optimize the entity for fast access operations."""
        # Pre-cache frequently accessed paths
        self._cache_schema()

    def _optimize_for_validation(self) -> None:
        """Optimize the entity for fast validation operations."""
        self._cache_schema()

    def _cache_schema(self) -> None:
        """Cache the schema for faster validation."""
        if self._schema and not self._schema_cache:
            if hasattr(self._schema, 'to_native'):
                self._schema_cache = self._schema.to_native()
            elif hasattr(self._schema, 'to_dict'):
                self._schema_cache = self._schema.to_dict()

    def _clear_cache(self) -> None:
        """Clear performance cache (both local and global entries for this entity)."""
        self._cache.clear()
        self._schema_cache = None
        # Clear global cache entries for this entity only (same key as _get uses)
        _entity_cache_key = self.id or getattr(self, "_uid", None) or id(self)
        entity_prefix = f"get:{_entity_cache_key}:"
        if self._global_cache:
            if hasattr(self._global_cache, "clear_by_prefix"):
                self._global_cache.clear_by_prefix(entity_prefix)
            elif hasattr(self._global_cache, "keys"):
                for k in list(self._global_cache.keys()):
                    if isinstance(k, str) and k.startswith(entity_prefix) and hasattr(self._global_cache, "delete"):
                        self._global_cache.delete(k)

    def _get_memory_usage(self) -> int:
        """
        Get the memory usage in bytes.
        Returns:
            Estimated memory usage in bytes
        """
        import sys
        size = 0
        size += sys.getsizeof(self._metadata)
        if self._data:
            size += sys.getsizeof(self._data)
        size += sys.getsizeof(self._actions)
        size += sys.getsizeof(self._cache)
        size += sys.getsizeof(self._extensions)
        return size

    def _optimize_memory(self) -> None:
        """Optimize memory usage."""
        # Clear unnecessary caches
        self._clear_cache()
        # Compact data if possible
        if self._data and hasattr(self._data, 'compact'):
            self._data.compact()

    def get_performance_stats(self) -> dict[str, Any]:
        """
        Get performance statistics.
        Returns:
            Dictionary with performance statistics
        """
        stats = self._performance_stats.copy()
        if hasattr(self._global_cache, 'get_stats'):
            stats['cache_stats'] = self._global_cache.get_stats()
        elif hasattr(self._global_cache, 'stats'):
            stats['cache_stats'] = self._global_cache.stats()
        else:
            stats['cache_stats'] = {}
        return stats
    # ==========================================================================
    # EXTENSIBILITY
    # ==========================================================================

    def register_extension(self, name: str, extension: Any) -> None:
        """
        Register an extension with the entity.
        Args:
            name: Extension name
            extension: Extension object
        """
        self._extensions[name] = extension
        logger.debug(f"Registered extension: {name}")

    def get_extension(self, name: str) -> Any | None:
        """
        Get an extension by name.
        Args:
            name: Extension name
        Returns:
            Extension object or None if not found
        """
        return self._extensions.get(name)

    def has_extension(self, name: str) -> bool:
        """
        Check if an extension exists.
        Args:
            name: Extension name
        Returns:
            True if extension exists
        """
        return name in self._extensions

    def list_extensions(self) -> list[str]:
        """
        List all registered extensions.
        Returns:
            List of extension names
        """
        return list(self._extensions.keys())

    def remove_extension(self, name: str) -> bool:
        """
        Remove an extension by name.
        Args:
            name: Extension name
        Returns:
            True if extension was removed, False if not found
        """
        if name in self._extensions:
            del self._extensions[name]
            logger.debug(f"Removed extension: {name}")
            return True
        return False

    def has_extension_type(self, extension_type: str) -> bool:
        """
        Check if an extension of a specific type exists.
        Args:
            extension_type: Extension type name to search for
        Returns:
            True if extension of type exists
        """
        return any(
            hasattr(ext, '__class__') and extension_type.lower() in ext.__class__.__name__.lower()
            for ext in self._extensions.values()
        )
# ==============================================================================
# EXPORTS
# ==============================================================================
__all__ = [
    # Entity classes
    "XWEntityMetadata",
    "AEntity",
    "ADataBackedObject",
    "ACollection",
    "AGroup",
]

