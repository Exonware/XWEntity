#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_collection_group.py
Core tests for XWCollection and XWGroup.
High-value tests covering identity, hierarchy, actions, and ICollection/IGroup contracts.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 05-Mar-2026
"""

from __future__ import annotations

import pytest
from typing import Any
from exonware.xwentity import (
    XWEntity,
    XWCollection,
    XWGroup,
    XWEntityActionError,
)
from exonware.xwentity.contracts import ICollection, IGroup
from exonware.xwschema import XWSchema


@pytest.mark.xwentity_core
class TestCoreXWCollection:
    """Core tests for XWCollection: identity, entity_type, actions, ICollection contract."""

    def test_collection_creation_with_entity_type_str(self):
        """XWCollection can be created with entity type as string."""
        coll = XWCollection("users", "user")
        assert coll.id == "users"
        assert coll.entity_type == "user"
        assert coll.group is None
        assert coll.created_at is not None
        assert coll.updated_at is not None

    def test_collection_creation_with_entity_type_class(self):
        """XWCollection can be created with entity type as class."""
        coll = XWCollection("people", XWEntity)
        assert coll.id == "people"
        assert coll.entity_type is XWEntity or coll.entity_type == "XWEntity"

    def test_collection_creation_with_group(self):
        """XWCollection can be created with optional group."""
        group = XWGroup("main")
        coll = XWCollection("items", "item", group=group)
        assert coll.group is group
        assert coll.id == "items"

    def test_collection_creation_with_title_and_description(self):
        """XWCollection accepts optional title and description."""
        coll = XWCollection(
            "docs",
            "document",
            title="Documents",
            description="All documents",
        )
        assert coll.id == "docs"
        assert getattr(coll, "_title", None) == "Documents"
        assert getattr(coll, "_description", None) == "All documents"

    def test_collection_implements_icollection(self):
        """XWCollection implements ICollection protocol."""
        coll = XWCollection("x", "entity")
        assert isinstance(coll, ICollection)

    def test_collection_list_actions_initially_empty(self):
        """New collection has no actions."""
        coll = XWCollection("x", "entity")
        assert coll.list_actions() == []

    def test_collection_register_and_list_actions(self):
        """Register action and list_actions returns it."""
        coll = XWCollection("x", "entity")

        def search(c: XWCollection[Any], q: str = "") -> list:
            return []

        coll.register_action(search)
        names = coll.list_actions()
        assert "search" in names

    def test_collection_execute_plain_callable_action(self):
        """Execute a plain callable action passes collection and kwargs."""
        coll = XWCollection("x", "entity")

        def greet(c: XWCollection[Any], name: str = "World") -> str:
            return f"Hello, {name}!"

        coll.register_action(greet)
        result = coll.execute_action("greet", name="Alice")
        assert result == "Hello, Alice!"

    def test_collection_execute_nonexistent_action_raises(self):
        """Executing non-existent action raises XWEntityActionError."""
        coll = XWCollection("x", "entity")
        with pytest.raises(XWEntityActionError) as exc_info:
            coll.execute_action("nonexistent")
        assert "not found" in str(exc_info.value).lower() or "nonexistent" in str(exc_info.value).lower()

    def test_collection_group_setter_updates_updated_at(self):
        """Setting group updates updated_at."""
        coll = XWCollection("x", "entity")
        group = XWGroup("g1")
        before = coll.updated_at
        coll.group = group
        assert coll.group is group
        assert coll.updated_at >= before


@pytest.mark.xwentity_core
class TestCoreXWGroup:
    """Core tests for XWGroup: identity, hierarchy, collections, actions, IGroup contract."""

    def test_group_creation_minimal(self):
        """XWGroup can be created with only object_id."""
        group = XWGroup("main")
        assert group.id == "main"
        assert group.parent is None
        assert group.collections == {}
        assert group.subgroups == {}
        assert group.created_at is not None
        assert group.updated_at is not None

    def test_group_creation_with_title_description(self):
        """XWGroup accepts optional title and description."""
        group = XWGroup("g1", title="My Group", description="Description")
        assert group.id == "g1"
        assert getattr(group, "_title", None) == "My Group"
        assert getattr(group, "_description", None) == "Description"

    def test_group_creation_with_parent(self):
        """XWGroup can have optional parent and registers itself with parent."""
        parent = XWGroup("parent")
        child = XWGroup("child", parent=parent)
        assert child.parent is parent
        assert parent.subgroups.get("child") is child

    def test_group_implements_igroup(self):
        """XWGroup implements IGroup protocol."""
        group = XWGroup("g")
        assert isinstance(group, IGroup)

    def test_group_add_and_get_collection(self):
        """Add collection to group and retrieve by id."""
        group = XWGroup("g")
        coll = XWCollection("users", "user")
        group.add_collection(coll)
        assert group.collections.get("users") is coll
        assert group.get_collection("users") is coll

    def test_group_add_collection_backlinks_collection_to_group(self):
        """Adding collection to group sets collection.group to this group."""
        group = XWGroup("g")
        coll = XWCollection("users", "user")
        group.add_collection(coll)
        assert coll.group is group

    def test_group_remove_collection(self):
        """remove_collection removes by id and returns True when present."""
        group = XWGroup("g")
        coll = XWCollection("users", "user")
        group.add_collection(coll)
        ok = group.remove_collection("users")
        assert ok is True
        assert group.get_collection("users") is None
        assert "users" not in group.collections

    def test_group_remove_collection_nonexistent_returns_false(self):
        """remove_collection returns False when id not present."""
        group = XWGroup("g")
        ok = group.remove_collection("nonexistent")
        assert ok is False

    def test_group_iter_collections(self):
        """iter_collections yields all collections."""
        group = XWGroup("g")
        c1 = XWCollection("a", "x")
        c2 = XWCollection("b", "y")
        group.add_collection(c1)
        group.add_collection(c2)
        ids = [c.id for c in group.iter_collections()]
        assert set(ids) == {"a", "b"}

    def test_group_iter_subgroups(self):
        """iter_subgroups yields direct child groups."""
        parent = XWGroup("parent")
        XWGroup("child1", parent=parent)
        XWGroup("child2", parent=parent)
        ids = [g.id for g in parent.iter_subgroups()]
        assert set(ids) == {"child1", "child2"}

    def test_group_list_actions_initially_empty(self):
        """New group has no actions."""
        group = XWGroup("g")
        assert group.list_actions() == []

    def test_group_register_and_execute_action(self):
        """Register and execute a plain callable action."""
        group = XWGroup("g")

        def report(g: XWGroup) -> str:
            return f"Group {g.id} has {len(g.collections)} collections"

        group.register_action(report)
        result = group.execute_action("report")
        assert "Group g" in result and "0 collections" in result

    def test_group_execute_nonexistent_action_raises(self):
        """Executing non-existent action raises XWEntityActionError."""
        group = XWGroup("g")
        with pytest.raises(XWEntityActionError):
            group.execute_action("nonexistent")


@pytest.mark.xwentity_core
class TestCoreCollectionGroupIntegration:
    """Core integration: collection-group hierarchy and multiple collections."""

    def test_group_with_multiple_collections(self):
        """Group can hold multiple collections; each has correct entity_type."""
        group = XWGroup("app")
        users = XWCollection("users", "user")
        posts = XWCollection("posts", "post")
        group.add_collection(users)
        group.add_collection(posts)
        assert len(group.collections) == 2
        assert group.get_collection("users").entity_type == "user"
        assert group.get_collection("posts").entity_type == "post"

    def test_collection_group_roundtrip(self):
        """Add collection to group, remove it, add again."""
        group = XWGroup("g")
        coll = XWCollection("items", "item")
        group.add_collection(coll)
        assert coll.group is group
        group.remove_collection("items")
        assert group.get_collection("items") is None
        coll.group = None
        group.add_collection(coll)
        assert group.get_collection("items") is coll and coll.group is group

    def test_nested_groups_and_collections(self):
        """Parent group has subgroups; each can have collections."""
        root = XWGroup("root")
        team_a = XWGroup("team_a", parent=root)
        team_b = XWGroup("team_b", parent=root)
        ca = XWCollection("a_items", "item")
        cb = XWCollection("b_items", "item")
        team_a.add_collection(ca)
        team_b.add_collection(cb)
        assert root.subgroups["team_a"] is team_a
        assert root.subgroups["team_b"] is team_b
        assert team_a.get_collection("a_items") is ca
        assert team_b.get_collection("b_items") is cb
        assert ca.group is team_a
        assert cb.group is team_b

    def test_group_execute_action_on_collections(self):
        """Group can execute action on all collections (mass operation)."""
        group = XWGroup("g")
        c1 = XWCollection("c1", "x")
        c2 = XWCollection("c2", "y")

        def report(c: XWCollection[Any], prefix: str = "") -> str:
            return f"{prefix}{c.id}"

        c1.register_action(report)
        c2.register_action(report)
        group.add_collection(c1)
        group.add_collection(c2)
        results = group.execute_action_on_collections("report", prefix="coll:")
        assert results == ["coll:c1", "coll:c2"]

    def test_collection_execute_action_on_entities(self):
        """Collection can execute action on given entities (mass transaction)."""
        coll = XWCollection("users", "user")
        e1 = XWEntity(data={"name": "Alice", "age": 30})
        e2 = XWEntity(data={"name": "Bob", "age": 25})

        def get_name(obj: XWEntity) -> str:
            return obj.get("name") or ""

        e1.register_action(get_name)
        e2.register_action(get_name)
        results = coll.execute_action_on_entities("get_name", [e1, e2])
        assert results == ["Alice", "Bob"]
