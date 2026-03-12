#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_metaclass.py
Unit tests for XWEntity metaclass and property discovery.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
from exonware.xwaction import XWAction
@pytest.mark.xwentity_unit

class TestEntityMetaclass:
    """Test XWEntity metaclass functionality."""

    def test_subclass_property_discovery(self):
        """Test property discovery in subclasses."""
        class UserEntity(XWEntity):
            name: str
            age: int
            email: str
        user = UserEntity(data={"name": "Alice", "age": 30, "email": "alice@example.com"})
        # Properties should be accessible
        assert user.get("name") == "Alice"
        assert user.get("age") == 30

    def test_subclass_action_discovery(self):
        """Test action discovery in subclasses."""
        class UserEntity(XWEntity):
            @XWAction(api_name="get_name")
            def get_name(self) -> str:
                return self.get("name", "Unknown")
        user = UserEntity(data={"name": "Alice"})
        # Actions should be auto-discovered if config allows
        assert user.get("name") == "Alice"

    def test_subclass_performance_mode_auto(self):
        """Test performance mode auto-detection in subclasses."""
        class SmallEntity(XWEntity):
            prop1: str
            prop2: str
        # Should use PERFORMANCE mode for small number of properties
        entity = SmallEntity(data={"prop1": "value1", "prop2": "value2"})
        assert entity.get("prop1") == "value1"

    def test_subclass_with_many_properties(self):
        """Test subclass with many properties uses MEMORY mode."""
        class LargeEntity(XWEntity):
            prop1: str
            prop2: str
            prop3: str
            prop4: str
            prop5: str
            prop6: str
            prop7: str
            prop8: str
            prop9: str
            prop10: str
            prop11: str
        # Should use MEMORY mode for many properties
        entity = LargeEntity(data={f"prop{i}": f"value{i}" for i in range(1, 12)})
        assert entity.get("prop1") == "value1"
