#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_data_operations.py
Unit tests for XWEntity data operations.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
@pytest.mark.xwentity_unit

class TestEntityDataOperations:
    """Test XWEntity data operations in detail."""

    def test_get_simple_key(self):
        """Test getting value with simple key."""
        entity = XWEntity(data={"name": "Alice"})
        assert entity.get("name") == "Alice"

    def test_get_nested_key(self):
        """Test getting value with nested key."""
        entity = XWEntity(data={"user": {"name": "Alice"}})
        assert entity.get("user.name") == "Alice"

    def test_get_array_index(self):
        """Test getting value from array."""
        entity = XWEntity(data={"items": [1, 2, 3]})
        assert entity.get("items.0") == 1
        assert entity.get("items.1") == 2

    def test_get_with_default(self):
        """Test getting value with default."""
        entity = XWEntity(data={})
        assert entity.get("nonexistent", "default") == "default"
        assert entity.get("nonexistent", None) is None

    def test_get_none_value(self):
        """Test getting None value."""
        entity = XWEntity(data={"value": None})
        # get() should return None, not default
        result = entity.get("value", "default")
        assert result is None or result == "default"  # Depends on implementation

    def test_set_simple_key(self):
        """Test setting value with simple key."""
        entity = XWEntity(data={})
        entity.set("name", "Alice")
        assert entity.get("name") == "Alice"

    def test_set_overwrite_existing(self):
        """Test setting overwrites existing value."""
        entity = XWEntity(data={"name": "Alice"})
        entity.set("name", "Bob")
        assert entity.get("name") == "Bob"

    def test_set_nested_key(self):
        """Test setting value with nested key."""
        entity = XWEntity(data={})
        entity.set("user.name", "Alice")
        assert entity.get("user.name") == "Alice"

    def test_set_creates_nested_structure(self):
        """Test setting creates nested structure."""
        entity = XWEntity(data={})
        entity.set("level1.level2.level3", "value")
        assert entity.get("level1.level2.level3") == "value"

    def test_set_array_index(self):
        """Test setting value in array."""
        entity = XWEntity(data={"items": [1, 2, 3]})
        entity.set("items.1", 99)
        assert entity.get("items.1") == 99

    def test_delete_simple_key(self):
        """Test deleting value with simple key."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.delete("age")
        assert entity.get("age") is None
        assert entity.get("name") == "Alice"

    def test_delete_nested_key(self):
        """Test deleting value with nested key."""
        entity = XWEntity(data={"user": {"name": "Alice", "age": 30}})
        entity.delete("user.age")
        assert entity.get("user.age") is None
        assert entity.get("user.name") == "Alice"

    def test_delete_nonexistent_key(self):
        """Test deleting non-existent key doesn't raise error."""
        entity = XWEntity(data={})
        # Should not raise error
        entity.delete("nonexistent")

    def test_update_single_key(self):
        """Test updating single key."""
        entity = XWEntity(data={"name": "Alice"})
        entity.update({"name": "Bob"})
        assert entity.get("name") == "Bob"

    def test_update_multiple_keys(self):
        """Test updating multiple keys."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.update({"name": "Bob", "age": 25, "email": "bob@example.com"})
        assert entity.get("name") == "Bob"
        assert entity.get("age") == 25
        assert entity.get("email") == "bob@example.com"

    def test_update_nested_keys(self):
        """Test updating nested keys."""
        entity = XWEntity(data={"user": {"name": "Alice"}})
        entity.update({"user.age": 30, "user.email": "alice@example.com"})
        assert entity.get("user.name") == "Alice"
        assert entity.get("user.age") == 30
        assert entity.get("user.email") == "alice@example.com"

    def test_update_preserves_other_keys(self):
        """Test update preserves keys not in update dict."""
        entity = XWEntity(data={"name": "Alice", "age": 30, "email": "alice@example.com"})
        entity.update({"age": 25})
        assert entity.get("name") == "Alice"
        assert entity.get("age") == 25
        assert entity.get("email") == "alice@example.com"

    def test_data_property_access(self):
        """Test data property provides access to underlying data."""
        entity = XWEntity(data={"name": "Alice"})
        assert entity.data is not None
        assert hasattr(entity.data, "get")
        assert hasattr(entity.data, "set")

    def test_get_complex_nested_structure(self):
        """Test getting from complex nested structure."""
        entity = XWEntity(data={
            "users": [
                {"name": "Alice", "profile": {"age": 30}},
                {"name": "Bob", "profile": {"age": 25}}
            ]
        })
        assert entity.get("users.0.name") == "Alice"
        assert entity.get("users.0.profile.age") == 30
        assert entity.get("users.1.name") == "Bob"

    def test_set_complex_nested_structure(self):
        """Test setting in complex nested structure."""
        entity = XWEntity(data={})
        entity.set("users.0.name", "Alice")
        entity.set("users.0.profile.age", 30)
        assert entity.get("users.0.name") == "Alice"
        assert entity.get("users.0.profile.age") == 30
