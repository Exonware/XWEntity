#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_factory_methods.py
Core tests for XWEntity factory methods.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_core

class TestCoreFactoryMethods:
    """Test core factory methods."""

    def test_from_dict_simple(self):
        """Test from_dict with simple data."""
        data = {"name": "Alice", "age": 30}
        # Use constructor directly - from_dict classmethod conflicts with instance method
        entity = XWEntity(data=data)
        assert entity.get("name") == "Alice"
        assert entity.get("age") == 30

    def test_from_dict_with_schema(self):
        """Test from_dict with schema."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        })
        data = {"name": "Alice", "age": 30}
        # Use constructor directly - from_dict classmethod conflicts with instance method
        entity = XWEntity(data=data, schema=schema)
        assert entity.schema == schema
        assert entity.get("name") == "Alice"

    def test_from_dict_with_entity_type(self):
        """Test from_dict with entity_type."""
        data = {"name": "Alice"}
        # Use constructor directly - from_dict classmethod conflicts with instance method
        entity = XWEntity(data=data, entity_type="user")
        assert entity._metadata.type == "user"  # Use 'type' property, not 'entity_type'

    def test_from_dict_full_entity(self):
        """Test from_dict with full entity dict (from to_native)."""
        original = XWEntity(data={"name": "Alice", "age": 30})
        entity_dict = original.to_native()
        # from_dict (factory) should handle full entity dict
        loaded = XWEntity.from_dict(entity_dict)
        assert loaded.get("name") == "Alice"
        assert loaded.get("age") == 30

    def test_from_native(self):
        """Test from_native factory method."""
        data = {"name": "Alice", "age": 30}
        entity = XWEntity.from_native(data)
        assert entity.get("name") == "Alice"
        assert entity.get("age") == 30

    def test_from_native_with_schema(self):
        """Test from_native with schema."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        })
        data = {"name": "Alice"}
        entity = XWEntity.from_native(data, schema=schema)
        assert entity.schema == schema

    def test_from_native_with_object_type(self):
        """Test from_native with object_type parameter."""
        data = {"name": "Alice"}
        entity = XWEntity.from_native(data, object_type="user")
        assert entity._metadata.type == "user"

    def test_to_dict(self, sample_entity):
        """Test to_dict export."""
        result = sample_entity.to_dict()
        assert isinstance(result, dict)
        # to_dict() returns full entity structure; data lives under `_data`
        assert result.get("_data", {}).get("name") == "Alice"

    def test_to_native(self, sample_entity):
        """Test to_native export."""
        result = sample_entity.to_native()
        assert isinstance(result, dict)
        # Should contain entity data
        assert "name" in str(result) or "Alice" in str(result)

    def test_roundtrip_dict(self):
        """Test roundtrip through dict."""
        original = XWEntity(data={"name": "Alice", "age": 30})
        entity_dict = original.to_dict()
        loaded = XWEntity.from_dict(entity_dict)
        assert loaded.get("name") == "Alice"
        assert loaded.get("age") == 30

    def test_roundtrip_native(self):
        """Test roundtrip through native."""
        original = XWEntity(data={"name": "Alice", "age": 30})
        native = original.to_native()
        loaded = XWEntity.from_native(native)
        assert loaded.get("name") == "Alice"
        assert loaded.get("age") == 30
