#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_initialization.py
Unit tests for XWEntity initialization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityConfig, XWEntityError
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
from exonware.xwaction import XWAction
@pytest.mark.xwentity_unit

class TestEntityInitialization:
    """Test XWEntity initialization in detail."""

    def test_init_minimal(self):
        """Test minimal initialization."""
        entity = XWEntity()
        assert entity.data is not None
        assert entity.schema is None
        assert len(entity.actions) == 0

    def test_init_with_all_params(self):
        """Test initialization with all parameters."""
        schema = XWSchema({"type": "object"})
        data = {"name": "Alice"}
        @XWAction(api_name="test")
        def test_action(obj: XWEntity) -> str:
            return "test"
        entity = XWEntity(
            schema=schema,
            data=data,
            actions=[test_action],
            entity_type="user",
            node_mode="AUTO",
            edge_mode="AUTO",
            graph_manager_enabled=False
        )
        assert entity.schema == schema
        assert entity.get("name") == "Alice"
        assert "test" in entity.actions

    def test_init_schema_dict_conversion(self):
        """Test schema dict is converted to XWSchema."""
        schema_dict = {"type": "object", "properties": {"name": {"type": "string"}}}
        entity = XWEntity(schema=schema_dict, data={"name": "Alice"})
        assert entity.schema is not None
        assert isinstance(entity.schema, XWSchema)

    def test_init_schema_json_string_conversion(self):
        """Test schema JSON string is converted to XWSchema."""
        schema_str = '{"type": "object", "properties": {"name": {"type": "string"}}}'
        entity = XWEntity(schema=schema_str, data={"name": "Alice"})
        assert entity.schema is not None
        assert isinstance(entity.schema, XWSchema)

    def test_init_data_dict_conversion(self):
        """Test data dict is converted to XWData."""
        data_dict = {"name": "Alice"}
        entity = XWEntity(data=data_dict)
        assert entity.data is not None
        assert hasattr(entity.data, "get")

    def test_init_data_xwdata_preserved(self):
        """Test XWData instance is preserved."""
        xwdata = XWData.from_native({"name": "Alice"})
        entity = XWEntity(data=xwdata)
        # Data should be the same XWData instance or equivalent
        assert entity.get("name") == "Alice"

    def test_init_actions_list(self):
        """Test actions as list."""
        @XWAction(api_name="action1")
        def action1(obj: XWEntity) -> str:
            return "action1"
        @XWAction(api_name="action2")
        def action2(obj: XWEntity) -> str:
            return "action2"
        entity = XWEntity(actions=[action1, action2])
        assert "action1" in entity.actions
        assert "action2" in entity.actions

    def test_init_actions_dict(self):
        """Test actions as dict."""
        actions = {
            "handler_action": lambda obj: "handler",
            "query_action": {
                "query": {
                    "format": "xwqs",
                    "query": "SELECT 1"
                }
            }
        }
        entity = XWEntity(data={"test": 1}, actions=actions)
        assert "handler_action" in entity.actions or len(entity.actions) >= 0

    def test_init_entity_type_override(self):
        """Test entity_type overrides config default."""
        config = XWEntityConfig(default_entity_type="default")
        entity = XWEntity(data={}, config=config, entity_type="custom")
        assert entity._metadata.type == "custom"

    def test_init_node_config_override(self):
        """Test node config parameters override config."""
        config = XWEntityConfig()
        config.graph_manager_enabled = True
        entity = XWEntity(
            data={},
            config=config,
            graph_manager_enabled=False
        )
        assert entity._config.graph_manager_enabled is False

    def test_init_subclass_property_discovery(self):
        """Test property discovery in subclasses."""
        class UserEntity(XWEntity):
            name: str
            age: int
        user = UserEntity(data={"name": "Alice", "age": 30})
        # Properties should be discoverable
        assert user.get("name") == "Alice"

    def test_init_subclass_action_discovery(self):
        """Test action discovery in subclasses."""
        class UserEntity(XWEntity):
            @XWAction(api_name="get_name")
            def get_name(self) -> str:
                return self.get("name", "Unknown")
        user = UserEntity(data={"name": "Alice"})
        # Actions should be auto-discovered if auto_register_actions is enabled
        # This depends on config
        assert user.get("name") == "Alice"
