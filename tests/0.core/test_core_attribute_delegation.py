#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_attribute_delegation.py
Core tests for XWEntity attribute delegation.
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
@pytest.mark.xwentity_core

class TestCoreAttributeDelegation:
    """Test core attribute delegation functionality."""

    def test_attribute_access_to_data(self, sample_entity):
        """Test accessing data properties via attribute."""
        # Should be able to access data properties directly
        assert sample_entity.get("name") == "Alice"

    def test_attribute_access_to_action(self, entity_with_actions):
        """Test accessing actions via attribute."""
        # Should be able to call action as method
        result = entity_with_actions.get_name()
        assert result == "Alice"

    def test_attribute_error_for_nonexistent(self, sample_entity):
        """Test AttributeError for non-existent attribute."""
        with pytest.raises(AttributeError):
            _ = sample_entity.nonexistent_attribute

    def test_action_via_attribute_with_params(self, entity_with_actions):
        """Test calling action via attribute with parameters."""
        result = entity_with_actions.update_age(25)
        assert result["success"] is True
        assert entity_with_actions.get("age") == 25

    def test_data_property_via_getattr(self, sample_entity):
        """Test data property access via __getattr__."""
        # This tests the fallback to data.get()
        name = sample_entity.get("name")
        assert name == "Alice"
