#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/group_tests/test_group.py
Unit tests for XWGroup.
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
    XWCollection,
    XWGroup,
    XWEntityActionError,
)
from exonware.xwentity.contracts import IGroup
from exonware.xwentity.base import AGroup
from exonware.xwsystem.shared import XWObject


@pytest.mark.xwentity_unit
class TestXWGroupIdentity:
    """XWGroup identity and XWObject integration."""

    def test_id_from_object_id(self):
        """id property returns object_id passed to constructor."""
        g = XWGroup("my_group")
        assert g.id == "my_group"

    def test_uid_present(self):
        """XWObject provides uid."""
        g = XWGroup("g")
        assert hasattr(g, "uid")
        assert g.uid is not None

    def test_extends_agroup_and_xwobject(self):
        """XWGroup extends AGroup and XWObject."""
        g = XWGroup("g")
        assert isinstance(g, AGroup)
        assert isinstance(g, XWObject)

    def test_implements_igroup(self):
        """XWGroup implements IGroup."""
        g = XWGroup("g")
        assert isinstance(g, IGroup)


@pytest.mark.xwentity_unit
class TestXWGroupHierarchy:
    """Parent and subgroups."""

    def test_parent_none_by_default(self):
        """parent is None when not provided."""
        g = XWGroup("g")
        assert g.parent is None

    def test_parent_set_via_constructor(self):
        """parent can be set via constructor."""
        parent = XWGroup("parent")
        child = XWGroup("child", parent=parent)
        assert child.parent is parent

    def test_parent_registers_subgroup(self):
        """When parent is provided, parent._subgroups contains this group."""
        parent = XWGroup("parent")
        child = XWGroup("child", parent=parent)
        assert "child" in parent.subgroups
        assert parent.subgroups["child"] is child

    def test_subgroups_copy(self):
        """subgroups property returns a copy of the dict."""
        parent = XWGroup("p")
        XWGroup("c", parent=parent)
        s1 = parent.subgroups
        s2 = parent.subgroups
        assert s1 is not s2
        assert s1 == s2


@pytest.mark.xwentity_unit
class TestXWGroupCollections:
    """add_collection, remove_collection, get_collection, iter_collections."""

    def test_add_collection(self):
        """add_collection stores collection by id."""
        g = XWGroup("g")
        c = XWCollection("users", "user")
        g.add_collection(c)
        assert g.collections.get("users") is c

    def test_add_collection_backlink(self):
        """add_collection sets collection.group to this group."""
        g = XWGroup("g")
        c = XWCollection("users", "user")
        g.add_collection(c)
        assert c.group is g

    def test_remove_collection(self):
        """remove_collection removes by id and returns True."""
        g = XWGroup("g")
        c = XWCollection("users", "user")
        g.add_collection(c)
        ok = g.remove_collection("users")
        assert ok is True
        assert g.get_collection("users") is None

    def test_remove_collection_nonexistent(self):
        """remove_collection returns False when id not in group."""
        g = XWGroup("g")
        ok = g.remove_collection("nonexistent")
        assert ok is False

    def test_get_collection_nonexistent(self):
        """get_collection returns None when id not in group."""
        g = XWGroup("g")
        assert g.get_collection("x") is None

    def test_collections_returns_copy(self):
        """collections() returns a copy of the internal dict."""
        g = XWGroup("g")
        c = XWCollection("u", "user")
        g.add_collection(c)
        col1 = g.collections
        col2 = g.collections
        assert col1 is not col2
        assert col1 == col2

    def test_iter_collections(self):
        """iter_collections yields all collections."""
        g = XWGroup("g")
        c1 = XWCollection("a", "x")
        c2 = XWCollection("b", "y")
        g.add_collection(c1)
        g.add_collection(c2)
        ids = [c.id for c in g.iter_collections()]
        assert set(ids) == {"a", "b"}

    def test_iter_subgroups(self):
        """iter_subgroups yields direct child groups."""
        parent = XWGroup("parent")
        XWGroup("c1", parent=parent)
        XWGroup("c2", parent=parent)
        ids = [g.id for g in parent.iter_subgroups()]
        assert set(ids) == {"c1", "c2"}


@pytest.mark.xwentity_unit
class TestXWGroupActions:
    """register_action, list_actions, execute_action."""

    def test_register_and_list(self):
        """register_action and list_actions."""
        g = XWGroup("g")

        def report(grp: XWGroup) -> str:
            return grp.id

        g.register_action(report)
        assert "report" in g.list_actions()

    def test_execute_action(self):
        """execute_action invokes callable and returns result."""
        g = XWGroup("g")

        def double(grp: XWGroup, n: int) -> int:
            return n * 2

        g.register_action(double)
        result = g.execute_action("double", n=7)
        assert result == 14

    def test_execute_nonexistent_raises(self):
        """execute_action with unknown name raises XWEntityActionError."""
        g = XWGroup("g")
        with pytest.raises(XWEntityActionError):
            g.execute_action("nonexistent")


@pytest.mark.xwentity_unit
class TestXWGroupTimestamps:
    """created_at, updated_at, _touch."""

    def test_created_at_set(self):
        """created_at is set on creation."""
        g = XWGroup("g")
        assert isinstance(g.created_at, datetime)

    def test_updated_at_after_add_collection(self):
        """updated_at is updated when collection is added."""
        g = XWGroup("g")
        before = g.updated_at
        g.add_collection(XWCollection("x", "e"))
        assert g.updated_at >= before

    def test_updated_at_after_remove_collection(self):
        """updated_at is updated when collection is removed."""
        g = XWGroup("g")
        g.add_collection(XWCollection("x", "e"))
        before = g.updated_at
        g.remove_collection("x")
        assert g.updated_at >= before


@pytest.mark.xwentity_unit
class TestXWGroupEdgeCases:
    """Edge cases."""

    def test_title_description_optional(self):
        """title and description stored when provided."""
        g = XWGroup("g", title="T", description="D")
        assert getattr(g, "_title", None) == "T"
        assert getattr(g, "_description", None) == "D"

    def test_add_same_collection_id_twice_replaces(self):
        """Adding another collection with same id replaces the first."""
        g = XWGroup("g")
        c1 = XWCollection("users", "user")
        c2 = XWCollection("users", "person")
        g.add_collection(c1)
        g.add_collection(c2)
        assert g.get_collection("users") is c2
