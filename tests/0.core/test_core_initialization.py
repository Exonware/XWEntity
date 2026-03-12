#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_initialization.py
Core tests for XWEntity initialization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityConfig
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
from exonware.xwaction import XWAction
@pytest.mark.xwentity_core

class TestCoreInitialization:
    """Test core initialization functionality."""

    def test_init_with_schema_dict(self):
        """Test initialization with schema as dict."""
        schema = {"type": "object", "properties": {"name": {"type": "string"}}}
        entity = XWEntity(schema=schema, data={"name": "Alice"})
        assert entity.schema is not None
        assert entity.get("name") == "Alice"

    def test_init_with_schema_xwschema(self):
        """Test initialization with XWSchema instance."""
        schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}}})
        entity = XWEntity(schema=schema, data={"name": "Alice"})
        assert entity.schema == schema
        assert entity.get("name") == "Alice"

    def test_init_with_schema_json_string(self):
        """Test initialization with schema as JSON string."""
        schema_str = '{"type": "object", "properties": {"name": {"type": "string"}}}'
        entity = XWEntity(schema=schema_str, data={"name": "Alice"})
        assert entity.schema is not None
        assert entity.get("name") == "Alice"

    def test_init_without_schema(self):
        """Test initialization without schema."""
        entity = XWEntity(data={"name": "Alice"})
        assert entity.schema is None
        assert entity.get("name") == "Alice"

    def test_init_with_data_dict(self):
        """Test initialization with data as dict."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        assert entity.get("name") == "Alice"
        assert entity.get("age") == 30

    def test_init_with_data_xwdata(self):
        """Test initialization with XWData instance."""
        xwdata = XWData.from_native({"name": "Alice", "age": 30})
        entity = XWEntity(data=xwdata)
        assert entity.get("name") == "Alice"
        assert entity.get("age") == 30

    def test_init_with_data_list(self):
        """Test initialization with data as list."""
        entity = XWEntity(data=[1, 2, 3])
        # List data should be accessible
        assert entity.data is not None

    def test_init_with_actions_list(self):
        """Test initialization with actions as list."""
        @XWAction(api_name="test_action")
        def test_action(obj: XWEntity) -> str:
            return "test"
        entity = XWEntity(data={}, actions=[test_action])
        assert "test_action" in entity.actions
        assert entity.execute_action("test_action") == "test"

    def test_init_with_actions_dict(self):
        """Test initialization with actions as dict."""
        actions = {
            "get_name": {
                "handler": lambda obj: obj.get("name", "Unknown")
            }
        }
        entity = XWEntity(data={"name": "Alice"}, actions=actions)
        assert "get_name" in entity.actions

    def test_init_with_entity_type(self):
        """Test initialization with entity_type."""
        entity = XWEntity(data={}, entity_type="user")
        assert entity._metadata.type == "user"

    def test_init_with_config(self):
        """Test initialization with custom config."""
        config = XWEntityConfig(default_entity_type="custom")
        entity = XWEntity(data={}, config=config)
        assert entity._config.default_entity_type == "custom"

    def test_init_with_node_config(self):
        """Test initialization with XWNode configuration."""
        entity = XWEntity(
            data={"name": "Alice"},
            node_mode="AUTO",
            edge_mode="AUTO",
            graph_manager_enabled=False
        )
        assert entity.get("name") == "Alice"

    def test_init_empty(self):
        """Test initialization with no arguments."""
        entity = XWEntity()
        assert entity.data is not None
        assert entity.schema is None
        assert len(entity.actions) == 0

    def test_init_metadata_created(self):
        """Test that metadata is created on initialization."""
        entity = XWEntity(data={"name": "Alice"})
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.deleted_at is None

    def test_init_with_subclass(self):
        """Test initialization with subclass."""
        class UserEntity(XWEntity):
            pass
        user = UserEntity(data={"name": "Alice"})
        assert isinstance(user, XWEntity)
        assert user.get("name") == "Alice"
