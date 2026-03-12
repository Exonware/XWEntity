#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_data_operations.py
Core tests for XWEntity data operations (get, set, delete, update).
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
@pytest.mark.xwentity_core

class TestCoreDataOperations:
    """Test core data operations."""

    def test_get_simple_path(self, sample_entity):
        """Test getting value with simple path."""
        assert sample_entity.get("name") == "Alice"
        assert sample_entity.get("age") == 30

    def test_get_nested_path(self):
        """Test getting value with nested path."""
        entity = XWEntity(data={"user": {"name": "Alice", "profile": {"age": 30}}})
        assert entity.get("user.name") == "Alice"
        assert entity.get("user.profile.age") == 30

    def test_get_with_default(self, sample_entity):
        """Test getting value with default."""
        assert sample_entity.get("nonexistent", "default") == "default"
        assert sample_entity.get("name", "default") == "Alice"

    def test_set_simple_path(self):
        """Test setting value with simple path."""
        entity = XWEntity(data={})
        entity.set("name", "Alice")
        assert entity.get("name") == "Alice"

    def test_set_nested_path(self):
        """Test setting value with nested path."""
        entity = XWEntity(data={})
        entity.set("user.name", "Alice")
        assert entity.get("user.name") == "Alice"

    def test_set_overwrite(self, sample_entity):
        """Test setting value overwrites existing."""
        sample_entity.set("name", "Bob")
        assert sample_entity.get("name") == "Bob"

    def test_delete_simple_path(self):
        """Test deleting value with simple path."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.delete("age")
        assert entity.get("age") is None
        assert entity.get("name") == "Alice"

    def test_delete_nested_path(self):
        """Test deleting value with nested path."""
        entity = XWEntity(data={"user": {"name": "Alice", "age": 30}})
        entity.delete("user.age")
        assert entity.get("user.age") is None
        assert entity.get("user.name") == "Alice"

    def test_update_multiple_values(self):
        """Test updating multiple values."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.update({"name": "Bob", "age": 25, "email": "bob@example.com"})
        assert entity.get("name") == "Bob"
        assert entity.get("age") == 25
        assert entity.get("email") == "bob@example.com"

    def test_update_nested_values(self):
        """Test updating nested values."""
        entity = XWEntity(data={"user": {"name": "Alice"}})
        entity.update({"user.age": 30, "user.email": "alice@example.com"})
        assert entity.get("user.name") == "Alice"
        assert entity.get("user.age") == 30
        assert entity.get("user.email") == "alice@example.com"

    def test_get_array_index(self):
        """Test getting value from array by index."""
        entity = XWEntity(data={"items": [1, 2, 3]})
        assert entity.get("items.0") == 1
        assert entity.get("items.1") == 2
        assert entity.get("items.2") == 3

    def test_set_array_index(self):
        """Test setting value in array by index."""
        entity = XWEntity(data={"items": [1, 2, 3]})
        entity.set("items.1", 99)
        assert entity.get("items.1") == 99

    def test_data_property(self, sample_entity):
        """Test data property access."""
        assert sample_entity.data is not None
        assert hasattr(sample_entity.data, "get")

    def test_get_complex_data(self):
        """Test getting complex nested data."""
        entity = XWEntity(data={
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ]
        })
        assert entity.get("users.0.name") == "Alice"
        assert entity.get("users.1.age") == 25
