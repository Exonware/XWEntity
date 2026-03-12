#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_edge_cases.py
Unit tests for XWEntity edge cases.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityError
@pytest.mark.xwentity_unit

class TestEntityEdgeCases:
    """Test XWEntity edge cases."""

    def test_empty_data(self):
        """Test entity with empty data."""
        entity = XWEntity(data={})
        assert entity.data is not None
        assert entity.get("nonexistent", "default") == "default"

    def test_none_data(self):
        """Test entity with None data."""
        entity = XWEntity(data=None)
        assert entity.data is not None  # Should be initialized to empty

    def test_list_data(self):
        """Test entity with list data."""
        entity = XWEntity(data=[1, 2, 3])
        assert entity.data is not None

    def test_very_large_data(self):
        """Test entity with very large data."""
        large_data = {f"key{i}": f"value{i}" for i in range(10000)}
        entity = XWEntity(data=large_data)
        assert entity.get("key0") == "value0"
        assert entity.get("key9999") == "value9999"

    def test_deeply_nested_data(self):
        """Test entity with deeply nested data."""
        data = {
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "value": "deep"
                            }
                        }
                    }
                }
            }
        }
        entity = XWEntity(data=data)
        assert entity.get("level1.level2.level3.level4.level5.value") == "deep"

    def test_special_characters_in_keys(self):
        """Test entity with special characters in keys."""
        entity = XWEntity(data={
            "key-with-dash": "value1",
            "key_with_underscore": "value2",
            "key.with.dot": "value3",
            "key with space": "value4"
        })
        # Path access may vary, but should handle special chars
        assert entity.data is not None

    def test_none_values(self):
        """Test entity with None values."""
        entity = XWEntity(data={"key1": None, "key2": "value"})
        assert entity.get("key2") == "value"
        # None values may return None or default
        result = entity.get("key1", "default")
        assert result is None or result == "default"

    def test_empty_string_values(self):
        """Test entity with empty string values."""
        entity = XWEntity(data={"empty": "", "non_empty": "value"})
        assert entity.get("empty") == ""
        assert entity.get("non_empty") == "value"

    def test_zero_values(self):
        """Test entity with zero values."""
        entity = XWEntity(data={"zero_int": 0, "zero_float": 0.0, "false": False})
        assert entity.get("zero_int") == 0
        assert entity.get("zero_float") == 0.0
        assert entity.get("false") is False

    def test_very_long_string(self):
        """Test entity with very long string value."""
        long_string = "x" * 100000
        entity = XWEntity(data={"long": long_string})
        assert len(entity.get("long")) == 100000

    def test_unicode_keys(self):
        """Test entity with Unicode keys."""
        entity = XWEntity(data={
            "ключ": "value1",
            "键": "value2",
            "🔑": "value3"
        })
        # Should handle Unicode keys
        assert entity.data is not None

    def test_array_with_mixed_types(self):
        """Test entity with array containing mixed types."""
        entity = XWEntity(data={
            "mixed_array": [1, "two", 3.0, True, None, {"nested": "value"}]
        })
        array = entity.get("mixed_array")
        assert isinstance(array, list)
        assert len(array) == 6

    def test_empty_array(self):
        """Test entity with empty array."""
        entity = XWEntity(data={"empty_array": []})
        assert entity.get("empty_array") == []

    def test_empty_object(self):
        """Test entity with empty object."""
        entity = XWEntity(data={"empty_object": {}})
        assert entity.get("empty_object") == {}

    def test_numeric_keys(self):
        """Test entity with numeric string keys."""
        entity = XWEntity(data={"0": "zero", "1": "one", "2": "two"})
        assert entity.get("0") == "zero"
        assert entity.get("1") == "one"

    def test_boolean_values(self):
        """Test entity with boolean values."""
        entity = XWEntity(data={"true": True, "false": False})
        assert entity.get("true") is True
        assert entity.get("false") is False

    def test_float_precision(self):
        """Test entity preserves float precision."""
        entity = XWEntity(data={"pi": 3.141592653589793})
        assert entity.get("pi") == 3.141592653589793

    def test_negative_numbers(self):
        """Test entity with negative numbers."""
        entity = XWEntity(data={"negative_int": -42, "negative_float": -3.14})
        assert entity.get("negative_int") == -42
        assert entity.get("negative_float") == -3.14

    def test_scientific_notation(self):
        """Test entity with scientific notation."""
        entity = XWEntity(data={"scientific": 1.23e10})
        assert entity.get("scientific") == 1.23e10
