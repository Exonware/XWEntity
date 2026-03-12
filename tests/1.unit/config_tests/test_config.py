#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/config_tests/test_config.py
Unit tests for XWEntityConfig.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntityConfig, get_config, set_config, PerformanceMode
@pytest.mark.xwentity_unit

class TestConfig:
    """Test XWEntityConfig."""

    def test_config_default_values(self):
        """Test config default values."""
        config = XWEntityConfig()
        assert config.default_entity_type == "entity"
        assert config.auto_validate is False
        assert config.strict_validation is True  # Default is True

    def test_config_custom_values(self):
        """Test config with custom values."""
        config = XWEntityConfig(
            default_entity_type="user",
            auto_validate=True,
            strict_validation=True
        )
        assert config.default_entity_type == "user"
        assert config.auto_validate is True
        assert config.strict_validation is True

    def test_config_performance_mode(self):
        """Test config performance mode."""
        config = XWEntityConfig(performance_mode=PerformanceMode.PERFORMANCE)
        assert config.performance_mode == PerformanceMode.PERFORMANCE

    def test_get_config(self):
        """Test get_config function."""
        config = get_config()
        assert isinstance(config, XWEntityConfig)

    def test_set_config(self):
        """Test set_config function."""
        original = get_config()
        new_config = XWEntityConfig(default_entity_type="custom")
        set_config(new_config)
        current = get_config()
        assert current.default_entity_type == "custom"
        # Restore
        set_config(original)

    def test_config_node_mode(self):
        """Test config node_mode."""
        config = XWEntityConfig()
        config.node_mode = "AUTO"
        assert config.node_mode == "AUTO"

    def test_config_edge_mode(self):
        """Test config edge_mode."""
        config = XWEntityConfig()
        config.edge_mode = "AUTO"
        assert config.edge_mode == "AUTO"

    def test_config_graph_manager(self):
        """Test config graph_manager_enabled."""
        config = XWEntityConfig()
        config.graph_manager_enabled = True
        assert config.graph_manager_enabled is True

    def test_config_node_options(self):
        """Test config node_options."""
        config = XWEntityConfig()
        config.node_options["test_option"] = "test_value"
        assert config.node_options["test_option"] == "test_value"

    def test_config_get_node_config(self):
        """Test get_node_config method."""
        config = XWEntityConfig()
        node_config = config.get_node_config()
        assert isinstance(node_config, dict)
        assert "mode" in node_config or "node_mode" in node_config
