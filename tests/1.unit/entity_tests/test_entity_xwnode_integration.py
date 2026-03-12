#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_xwnode_integration.py
Unit tests for XWEntity XWNode integration.
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

class TestEntityXWNodeIntegration:
    """Test XWEntity XWNode integration."""

    def test_entity_uses_xwnode(self):
        """Test entity uses XWNode for data storage."""
        entity = XWEntity(data={"name": "Alice"})
        # Data should be backed by XWNode
        assert entity.data is not None
        assert hasattr(entity.data, "get")

    def test_node_mode_configuration(self):
        """Test node_mode configuration."""
        entity = XWEntity(data={"name": "Alice"}, node_mode="AUTO")
        assert entity.get("name") == "Alice"

    def test_edge_mode_configuration(self):
        """Test edge_mode configuration."""
        entity = XWEntity(data={"name": "Alice"}, edge_mode="AUTO")
        assert entity.get("name") == "Alice"

    def test_graph_manager_disabled(self):
        """Test graph_manager_enabled=False."""
        entity = XWEntity(data={"name": "Alice"}, graph_manager_enabled=False)
        assert entity.get("name") == "Alice"

    def test_graph_manager_enabled(self):
        """Test graph_manager_enabled=True."""
        entity = XWEntity(data={"name": "Alice"}, graph_manager_enabled=True)
        assert entity.get("name") == "Alice"

    def test_node_options(self):
        """Test node_options configuration."""
        entity = XWEntity(
            data={"name": "Alice"},
            node_mode="AUTO",
            edge_mode="AUTO",
            immutable=True
        )
        assert entity.get("name") == "Alice"
