#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/collection_tests/test_collection.py
Unit tests for XWCollection.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 05-Mar-2026
"""

from __future__ import annotations

import pytest
from typing import Any
from datetime import datetime
from exonware.xwentity import (
    XWEntity,
    XWCollection,
    XWGroup,
    XWEntityActionError,
    XWEntityValidationError,
)
from exonware.xwentity.contracts import ICollection
from exonware.xwentity.base import ACollection
from exonware.xwsystem.shared import XWObject


@pytest.mark.xwentity_unit
class TestXWCollectionIdentity:
    """XWCollection identity and XWObject integration."""

    def test_id_from_object_id(self):
        """id property returns object_id passed to constructor."""
        coll = XWCollection("my_collection", "user")
        assert coll.id == "my_collection"

    def test_uid_present(self):
        """XWObject provides uid."""
        coll = XWCollection("c", "entity")
        assert hasattr(coll, "uid")
        assert coll.uid is not None
        assert isinstance(coll.uid, str)

    def test_extends_acollection_and_xwobject(self):
        """XWCollection extends ACollection and XWObject."""
        coll = XWCollection("c", "e")
        assert isinstance(coll, ACollection)
        assert isinstance(coll, XWObject)

    def test_implements_icollection(self):
        """XWCollection implements ICollection protocol."""
        coll = XWCollection("c", "e")
        assert isinstance(coll, ICollection)


@pytest.mark.xwentity_unit
class TestXWCollectionEntityType:
    """entity_type storage and retrieval."""

    def test_entity_type_str(self):
        """entity_type can be string."""
        coll = XWCollection("c", "user")
        assert coll.entity_type == "user"

    def test_entity_type_class(self):
        """entity_type can be entity class."""
        coll = XWCollection("c", XWEntity)
        assert coll.entity_type is XWEntity


@pytest.mark.xwentity_unit
class TestXWCollectionGroup:
    """Group association."""

    def test_group_none_by_default(self):
        """group is None when not provided."""
        coll = XWCollection("c", "e")
        assert coll.group is None

    def test_group_setter(self):
        """group setter updates and touch updated_at."""
        coll = XWCollection("c", "e")
        g = XWGroup("g1")
        coll.group = g
        assert coll.group is g
        assert coll.updated_at is not None

    def test_group_constructor(self):
        """group can be set via constructor."""
        g = XWGroup("g1")
        coll = XWCollection("c", "e", group=g)
        assert coll.group is g


@pytest.mark.xwentity_unit
class TestXWCollectionTimestamps:
    """created_at and updated_at."""

    def test_created_at_set(self):
        """created_at is set on creation."""
        coll = XWCollection("c", "e")
        assert isinstance(coll.created_at, datetime)

    def test_updated_at_initial(self):
        """updated_at equals created_at initially."""
        coll = XWCollection("c", "e")
        assert coll.updated_at == coll.created_at


@pytest.mark.xwentity_unit
class TestXWCollectionActions:
    """register_action, list_actions, execute_action."""

    def test_register_callable_uses_name(self):
        """Registering a callable uses __name__ as action name."""
        coll = XWCollection("c", "e")

        def my_action(c: XWCollection[Any]) -> None:
            pass

        coll.register_action(my_action)
        assert "my_action" in coll.list_actions()

    def test_register_multiple_actions(self):
        """Multiple actions can be registered."""
        coll = XWCollection("c", "e")

        def a1(c: XWCollection[Any]) -> str:
            return "1"

        def a2(c: XWCollection[Any]) -> str:
            return "2"

        coll.register_action(a1)
        coll.register_action(a2)
        names = coll.list_actions()
        assert "a1" in names and "a2" in names

    def test_execute_returns_value(self):
        """execute_action returns callable result."""
        coll = XWCollection("c", "e")

        def add(c: XWCollection[Any], x: int, y: int) -> int:
            return x + y

        coll.register_action(add)
        result = coll.execute_action("add", x=2, y=3)
        assert result == 5

    def test_execute_nonexistent_raises(self):
        """execute_action with unknown name raises XWEntityActionError."""
        coll = XWCollection("c", "e")
        with pytest.raises(XWEntityActionError) as exc:
            coll.execute_action("missing")
        assert "missing" in str(exc.value) or "not found" in str(exc.value).lower()

    def test_action_receives_collection_as_first_arg(self):
        """Plain callable receives (self, **kwargs) with self being collection."""
        coll = XWCollection("c", "e")
        seen = []

        def record(c: XWCollection[Any]) -> str:
            seen.append(c)
            return c.id

        coll.register_action(record)
        out = coll.execute_action("record")
        assert out == "c"
        assert len(seen) == 1 and seen[0] is coll


@pytest.mark.xwentity_unit
class TestXWCollectionEdgeCases:
    """Edge cases and robustness."""

    def test_empty_object_id_not_forbidden(self):
        """Empty string object_id is allowed (XWObject may allow it)."""
        coll = XWCollection("", "e")
        assert coll.id == ""

    def test_title_description_optional(self):
        """title and description are optional and stored when provided."""
        coll = XWCollection("c", "e", title="T", description="D")
        assert getattr(coll, "_title", None) == "T"
        assert getattr(coll, "_description", None) == "D"

    def test_list_actions_returns_new_list(self):
        """list_actions returns a list (copy of keys)."""
        coll = XWCollection("c", "e")
        L1 = coll.list_actions()
        L2 = coll.list_actions()
        assert L1 is not L2
        assert L1 == L2
