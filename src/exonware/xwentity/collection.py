#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/collection.py
XWCollection - Logical Entity Collection Scope

This module defines a lightweight collection type for XWEntity.
It is intentionally storage-agnostic and focuses on:
- Identity (id/uid via XWObject)
- The entity type managed by this collection
- Collection-level actions (e.g. search, bulk operations)

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
from typing import Any
from collections.abc import Iterable

from exonware.xwsystem import get_logger
from exonware.xwsystem.shared import XWObject
from exonware.xwaction import XWAction, ActionContext
from exonware.xwaction.core.validation import action_validator

from .base import ACollection
from .entity import XWEntity
from .group import XWGroup
from .errors import XWEntityActionError, XWEntityValidationError

logger = get_logger(__name__)


class XWCollection[TEntity: XWEntity](XWObject, ACollection):
    """
    Lightweight logical collection of entities of a single type.

    This class models the *scope* for a set of entities (their type and
    collection-level actions), without assuming any particular storage layout.
    Higher-level libraries (like xwmodels) can build persistence-aware
    collections on top of this.
    """

    def __init__(
        self,
        object_id: str,
        entity_type: type[TEntity] | str,
        group: "XWGroup | None" = None,
        title: "str | None" = None,
        description: "str | None" = None,
    ) -> None:
        """
        Initialize a collection scope.

        Args:
            object_id: Identifier for this collection (XWObject id/uid source).
            entity_type: Entity class or type name this collection manages.
            group: Optional owning group scope.
            title: Optional human-friendly title.
            description: Optional description.
        """
        super().__init__(object_id=object_id)
        ACollection.__init__(self, entity_type=entity_type)
        # Ensure identity is set (in case MRO or package resolution differs)
        self._id = object_id if object_id else None
        self._group: "XWGroup | None" = group
        if title:
            self._title = title
        if description:
            self._description = description
        self._created_at = datetime.now()
        self._updated_at = self._created_at
        # Collection-level actions (search, bulk ops, etc.)
        self._actions: dict[str, Any] = {}
        # Option G: init shared data engine (ADataBackedObject)
        self._init_data_backed()

    def to_dict(self, **kwargs: Any) -> dict[str, Any]:
        """Satisfy AObject abstract method; delegate to ADataBackedObject."""
        return ACollection.to_dict(self, **kwargs)

    # -------------------------------------------------------------------------
    # Basic metadata
    # -------------------------------------------------------------------------
    @property
    def entity_type(self) -> type[TEntity] | str:
        """Get the entity type managed by this collection."""
        return self._entity_type

    @property
    def group(self) -> "XWGroup | None":
        """Get the owning group scope, if any."""
        return self._group

    @group.setter
    def group(self, value: "XWGroup | None") -> None:
        """Set or change the owning group scope."""
        self._group = value
        self._updated_at = datetime.now()
        self._sync_data()

    @property
    def created_at(self) -> datetime:
        """Get creation timestamp."""
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        """Get last update timestamp."""
        return self._updated_at

    def _touch(self) -> None:
        """Update internal timestamp when collection-level changes occur."""
        self._updated_at = datetime.now()

    # -------------------------------------------------------------------------
    # ADataBackedObject (Option G)
    # -------------------------------------------------------------------------
    def _build_data_payload(self, **kwargs: Any) -> dict[str, Any]:
        """Build serializable payload for _data_backed."""
        entity_type_val = (
            self._entity_type.__name__
            if isinstance(self._entity_type, type)
            else self._entity_type
        )
        return {
            "id": self.id,
            "uid": self.uid,
            "entity_type": entity_type_val,
            "created_at": self._created_at.isoformat(),
            "updated_at": self._updated_at.isoformat(),
            "title": getattr(self, "_title", None),
            "description": getattr(self, "_description", None),
            "group_id": self._group.id if self._group else None,
        }

    def _apply_data_from_dict(self, data: dict[str, Any]) -> None:
        """Restore scalar state from dict."""
        self._id = data.get("id") or self._id
        if "uid" in data:
            self._uid = data["uid"]
        self._title = data.get("title")
        self._description = data.get("description")
        if "entity_type" in data and isinstance(data["entity_type"], str):
            self._entity_type = data["entity_type"]
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
        """Storage-agnostic: no-op. Persistence is implemented by xwmodels (XWModelCollection)."""
        pass

    def load(self, *args: Any, **kwargs: Any) -> None:
        """Storage-agnostic: no-op. Persistence is implemented by xwmodels (XWModelCollection)."""
        pass

    # -------------------------------------------------------------------------
    # Actions
    # -------------------------------------------------------------------------
    def register_action(self, action: Any) -> None:
        """
        Register a collection-level action.

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
        logger.debug(f"Registered collection action: {name}")

    def list_actions(self) -> list[str]:
        """List available collection-level action names."""
        return list(self._actions.keys())

    def execute_action(self, action_name: str, **kwargs: Any) -> Any:
        """
        Execute a registered collection-level action.

        If the action is an XWAction, this delegates to its execute() method
        with a collection-specific ActionContext; otherwise, it calls the
        callable directly.
        """
        if action_name not in self._actions:
            raise XWEntityActionError(
                f"Action '{action_name}' not found on collection '{self.id}'",
                action_name=action_name,
            )

        action = self._actions[action_name]

        xwaction_obj = None
        if callable(action) and hasattr(action, "xwaction"):
            xwaction_obj = getattr(action, "xwaction", None)
        elif isinstance(action, XWAction):
            xwaction_obj = action

        ctx = ActionContext(
            actor="collection",
            source="xwentity.collection",
            metadata={"action_name": action_name, "collection_id": self.id},
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
            f"Action '{action_name}' is not callable on collection '{self.id}'",
            action_name=action_name,
        )

    def execute_action_on_entities(
        self,
        action_name: str,
        entities: Iterable[XWEntity],
        **kwargs: Any,
    ) -> list[Any]:
        """
        Execute an entity-level action on all given entities.

        Applies the given action to each entity; useful for mass transactions
        (e.g. bulk_update, bulk_validate). Collection is storage-agnostic,
        so entities must be provided by the caller (e.g. from xwmodels).

        Args:
            action_name: Name of the action to execute on each entity
            entities: Iterable of XWEntity instances
            **kwargs: Arguments passed to each entity's execute_action

        Returns:
            List of results, one per entity

        Raises:
            XWEntityActionError: If action not found on any entity
        """
        results: list[Any] = []
        for entity in entities:
            if action_name in entity.list_actions():
                results.append(entity.execute_action(action_name, **kwargs))
            else:
                raise XWEntityActionError(
                    f"Action '{action_name}' not found on entity '{entity.id}'",
                    action_name=action_name,
                )
        return results


__all__ = [
    "XWCollection",
]

