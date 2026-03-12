#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_actions.py
Core tests for XWEntity actions.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityActionError
from exonware.xwaction import XWAction
@pytest.mark.xwentity_core

class TestCoreActions:
    """Test core actions functionality."""

    def test_register_action(self, sample_entity):
        """Test registering an action."""
        @XWAction(api_name="test_action")
        def test_action(obj: XWEntity) -> str:
            return "test"
        sample_entity.register_action(test_action)
        assert "test_action" in sample_entity.actions

    def test_execute_action(self, entity_with_actions):
        """Test executing a registered action."""
        result = entity_with_actions.execute_action("get_name")
        assert result == "Alice"

    def test_execute_action_with_params(self, entity_with_actions):
        """Test executing action with parameters."""
        result = entity_with_actions.execute_action("update_age", age=25)
        assert result["success"] is True
        assert entity_with_actions.get("age") == 25

    def test_execute_nonexistent_action(self, sample_entity):
        """Test executing non-existent action raises error."""
        with pytest.raises(XWEntityActionError):
            sample_entity.execute_action("nonexistent")

    def test_list_actions(self, entity_with_actions):
        """Test listing registered actions."""
        actions = entity_with_actions.list_actions()
        assert "get_name" in actions
        assert "update_age" in actions

    def test_action_attribute_access(self, entity_with_actions):
        """Test accessing action via attribute."""
        result = entity_with_actions.get_name()
        assert result == "Alice"

    def test_action_with_query(self, sample_entity):
        """Test action with query definition."""
        actions = {
            "get_age": {
                "query": {
                    "format": "xwqs",
                    "query": "SELECT age FROM table"
                }
            }
        }
        sample_entity = XWEntity(data={"age": 30}, actions=actions)
        assert "get_age" in sample_entity.actions

    def test_action_with_handler(self, sample_entity):
        """Test action with handler function."""
        def handler(obj: XWEntity) -> str:
            return f"Hello {obj.get('name')}"
        sample_entity.register_action(handler)
        result = sample_entity.execute_action("handler")
        assert "Hello" in result

    def test_multiple_actions(self, sample_entity):
        """Test registering multiple actions."""
        @XWAction(api_name="action1")
        def action1(obj: XWEntity) -> str:
            return "action1"
        @XWAction(api_name="action2")
        def action2(obj: XWEntity) -> str:
            return "action2"
        sample_entity.register_action(action1)
        sample_entity.register_action(action2)
        assert len(sample_entity.actions) >= 2
        assert sample_entity.execute_action("action1") == "action1"
        assert sample_entity.execute_action("action2") == "action2"

    def test_action_validation(self, sample_entity):
        """Test action input/output validation."""
        from exonware.xwschema import XWSchema
        @XWAction(
            api_name="validated_action",
            in_types={"age": XWSchema({"type": "integer", "minimum": 0, "maximum": 150})}
        )
        def validated_action(obj: XWEntity, age: int) -> dict:
            return {"age": age}
        sample_entity.register_action(validated_action)
        # Valid input
        result = sample_entity.execute_action("validated_action", age=30)
        assert result["age"] == 30
        # Invalid input should raise error
        with pytest.raises(Exception):
            sample_entity.execute_action("validated_action", age=200)
