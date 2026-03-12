#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/group.py
XWGroup - Logical Group Scope

This module defines a lightweight group type for XWEntity collections.
It is intentionally storage-agnostic and focuses on:
- Identity (id/uid via XWObject)
- Logical grouping of collections
- Group-level actions (e.g. multi-collection operations)

Actual persistence, indexing, and concrete storage strategies are implemented
by higher-level libraries (e.g. xwmodels) that may wrap or extend this class.

Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 05-Mar-2026
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, TYPE_CHECKING
from collections.abc import Iterable

from exonware.xwsystem import get_logger
from exonware.xwsystem.shared import XWObject
from exonware.xwaction import XWAction, ActionContext
from exonware.xwaction.core.validation import action_validator
from .base import AGroup
from .errors import XWEntityActionError, XWEntityValidationError
from .defs import EntityData

if TYPE_CHECKING:
    from .collection import XWCollection

logger = get_logger(__name__)


class XWGroup(XWObject, AGroup):
    """
    Lightweight logical group of collections.

    This class models the *scope* for a set of collections, without assuming
    any particular storage layout. Higher-level libraries (like xwmodels) can
    build persistence-aware groups on top of this.
    """

    def __init__(
        self,
        object_id: str,
        title: "str | None" = None,
        description: "str | None" = None,
        parent: "XWGroup | None" = None,
    ) -> None:
        """
        Initialize a group scope.

        Args:
            object_id: Identifier for this group (XWObject id/uid source).
            title: Optional human-friendly title.
            description: Optional description.
            parent: Optional parent group (for nested groups).
        """
        super().__init__(object_id=object_id)
        # Ensure identity is set (in case MRO or package resolution differs)
        self._id = object_id if object_id else None
        if title:
            self._title = title
        if description:
            self._description = description
        self._created_at = datetime.now()
        self._updated_at = self._created_at
        self._parent: "XWGroup | None" = parent
        self._subgroups: dict[str, "XWGroup"] = {}
        self._collections: dict[str, XWCollection[Any]] = {}
        # Group-level actions (multi-collection operations, maintenance, etc.)
        self._actions: dict[str, Any] = {}
        # Register with parent if provided
        if parent is not None:
            parent._subgroups[object_id] = self
        # Option G: init shared data engine (ADataBackedObject)
        self._init_data_backed()
        if parent is not None:
            parent._sync_data()

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Satisfy AObject abstract method; delegate to ADataBackedObject."""
        return AGroup.to_dict(self, **kwargs)

    # -------------------------------------------------------------------------
    # Hierarchy
    # -------------------------------------------------------------------------
    @property
    def parent(self) -> "XWGroup | None":
        """Get parent group, if any."""
        return self._parent

    @property
    def subgroups(self) -> dict[str, "XWGroup"]:
        """Get subgroups by id."""
        return dict(self._subgroups)

    @property
    def collections(self) -> dict[str, XWCollection[Any]]:
        """Get collections by id."""
        return dict(self._collections)

    def add_collection(self, collection: XWCollection[Any]) -> None:
        """
        Register a collection with this group.

        Does not create any storage; just establishes logical ownership.
        """
        self._collections[collection.id] = collection
        # Back-link collection to this group if it doesn't already point here
        if getattr(collection, "group", None) is not self:
            try:
                collection.group = self  # type: ignore[assignment]
            except Exception:
                # Collection may not expose a writable group attribute; ignore.
                pass
        self._touch()
        self._sync_data()

    def remove_collection(self, collection_id: str) -> bool:
        """Remove a collection by id from this group."""
        if collection_id in self._collections:
            del self._collections[collection_id]
            self._touch()
            self._sync_data()
            return True
        return False

    def get_collection(self, collection_id: str) -> "XWCollection[Any] | None":
        """Get a collection by id, if present."""
        return self._collections.get(collection_id)

    def _to_native(self) -> EntityData:
        """Export group as native dict (IGroup protocol)."""
        return self.to_dict()

    def _from_native(self, data: EntityData) -> None:
        """Restore group from native dict (IGroup protocol)."""
        self.from_dict(dict(data))

    def iter_collections(self) -> Iterable[XWCollection[Any]]:
        """Iterate over all collections in this group."""
        return self._collections.values()

    def iter_subgroups(self) -> Iterable["XWGroup"]:
        """Iterate over all direct subgroups."""
        return self._subgroups.values()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def _touch(self) -> None:
        """Update internal timestamp when group-level changes occur."""
        self._updated_at = datetime.now()

    # -------------------------------------------------------------------------
    # ADataBackedObject (Option G)
    # -------------------------------------------------------------------------
    def _build_data_payload(self, **kwargs: Any) -> dict[str, Any]:
        """Build serializable payload for _data_backed."""
        return {
            "id": self.id,
            "uid": self.uid,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "title": getattr(self, "_title", None),
            "description": getattr(self, "_description", None),
            "collection_ids": list(self._collections.keys()),
            "subgroup_ids": list(self._subgroups.keys()),
        }

    def _apply_data_from_dict(self, data: dict[str, Any]) -> None:
        """Restore scalar state from dict; live caches stay empty (caller adds children)."""
        self._id = data.get("id") or self._id
        if "uid" in data:
            self._uid = data["uid"]
        self._title = data.get("title")
        self._description = data.get("description")
        for key in ("created_at", "updated_at"):
            if key in data and isinstance(data[key], str):
                try:
                    dt = datetime.fromisoformat(data[key].replace("Z", "+00:00"))
                    setattr(self, f"_{key}", dt)
                except Exception:
                    pass

    # -------------------------------------------------------------------------
    # XWObject / AObject abstract methods (storage-agnostic: no-op save/load)
    # -------------------------------------------------------------------------
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Storage-agnostic: no-op. Persistence is implemented by xwmodels (XWModelGroup)."""
        pass

    def load(self, *args: Any, **kwargs: Any) -> None:
        """Storage-agnostic: no-op. Persistence is implemented by xwmodels (XWModelGroup)."""
        pass

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def register_action(self, action: Any) -> None:
        """
        Register a group-level action.

        Supports:
        - XWAction instances
        - Callables decorated with XWAction (wrapper.xwaction)
        - Plain callables (stored as-is)
        """
        # Normalize: Extract XWAction object if it's a decorated method
        if callable(action) and hasattr(action, "xwaction"):
            xwaction_obj = getattr(action, "xwaction", None)
            if isinstance(xwaction_obj, XWAction):
                action = xwaction_obj  # Store XWAction instance directly

        # Determine action name
        if hasattr(action, "api_name"):
            name = action.api_name  # type: ignore[assignment]
        elif hasattr(action, "name"):
            name = action.name  # type: ignore[assignment]
        elif hasattr(action, "__name__"):
            name = action.__name__  # type: ignore[assignment]
        else:
            name = f"action_{len(self._actions)}"

        self._actions[name] = action
        logger.debug(f"Registered group action: {name}")

    def list_actions(self) -> list[str]:
        """List available group-level action names."""
        return list(self._actions.keys())

    def execute_action(self, action_name: str, **kwargs: Any) -> Any:
        """
        Execute a registered group-level action.

        If the action is an XWAction, this delegates to its execute() method
        with a group-specific ActionContext; otherwise, it calls the callable
        directly.
        """
        if action_name not in self._actions:
            raise XWEntityActionError(
                f"Action '{action_name}' not found on group '{self.id}'",
                action_name=action_name,
            )

        action = self._actions[action_name]

        xwaction_obj = None
        if callable(action) and hasattr(action, "xwaction"):
            xwaction_obj = getattr(action, "xwaction", None)
        elif isinstance(action, XWAction):
            xwaction_obj = action

        ctx = ActionContext(
            actor="group",
            source="xwentity.group",
            metadata={"action_name": action_name, "group_id": self.id},
        )

        # PRIORITY 1: Use XWAction.execute() when available
        if xwaction_obj is not None and hasattr(xwaction_obj, "execute"):
            result = xwaction_obj.execute(context=ctx, instance=self, **kwargs)
            if hasattr(result, "data"):
                return result.data  # type: ignore[no-any-return]
            return result

        # PRIORITY 2: Action itself is XWAction with execute()
        if isinstance(action, XWAction) and hasattr(action, "execute"):
            result = action.execute(context=ctx, instance=self, **kwargs)
            if hasattr(result, "data"):
                return result.data  # type: ignore[no-any-return]
            return result

        # PRIORITY 3: Action has execute() method
        if hasattr(action, "execute") and callable(getattr(action, "execute", None)):
            result = action.execute(context=ctx, instance=self, **kwargs)  # type: ignore[call-arg]
            if hasattr(result, "data"):
                return result.data  # type: ignore[no-any-return]
            return result

        # PRIORITY 4: Regular callable, optionally validate via XWAction schema
        if callable(action):
            if xwaction_obj is not None and hasattr(xwaction_obj, "in_types") and xwaction_obj.in_types:
                validation_result = action_validator.validate_inputs(xwaction_obj, kwargs)
                if not validation_result.valid:
                    raise XWEntityValidationError(
                        f"Action parameter validation failed: "
                        f"{', '.join(validation_result.errors)}",
                        cause=None,
                    )
            return action(self, **kwargs)  # type: ignore[misc]

        raise XWEntityActionError(
            f"Action '{action_name}' is not callable on group '{self.id}'",
            action_name=action_name,
        )

    def execute_action_on_collections(self, action_name: str, **kwargs: Any) -> list[Any]:
        """
        Execute a collection-level action on all collections in this group.

        Applies the given action to each collection; useful for mass operations
        (e.g. sync_all, validate_all). Returns list of results in collection order.

        Args:
            action_name: Name of the action to execute on each collection
            **kwargs: Arguments passed to each collection's execute_action

        Returns:
            List of results, one per collection

        Raises:
            XWEntityActionError: If action not found on any collection
        """
        results: list[Any] = []
        for coll in self.iter_collections():
            if action_name in coll.list_actions():
                results.append(coll.execute_action(action_name, **kwargs))
            else:
                raise XWEntityActionError(
                    f"Action '{action_name}' not found on collection '{coll.id}'",
                    action_name=action_name,
                )
        return results


__all__ = [
    "XWGroup",
]

