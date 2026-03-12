#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_actions.py
Unit tests for XWEntity actions.
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
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_unit

class TestEntityActions:
    """Test XWEntity actions in detail."""

    def test_register_simple_action(self):
        """Test registering simple action."""
        entity = XWEntity(data={})
        @XWAction(api_name="simple")
        def simple_action(obj: XWEntity) -> str:
            return "result"
        entity.register_action(simple_action)
        assert "simple" in entity.actions
        assert entity.execute_action("simple") == "result"

    def test_register_action_with_params(self):
        """Test registering action with parameters."""
        entity = XWEntity(data={"value": 10})
        @XWAction(api_name="multiply")
        def multiply_action(obj: XWEntity, factor: int) -> int:
            return obj.get("value") * factor
        entity.register_action(multiply_action)
        result = entity.execute_action("multiply", factor=5)
        assert result == 50

    def test_register_action_with_validation(self):
        """Test registering action with input validation."""
        entity = XWEntity(data={})
        @XWAction(
            api_name="validated",
            in_types={"age": XWSchema({"type": "integer", "minimum": 0, "maximum": 150})}
        )
        def validated_action(obj: XWEntity, age: int) -> dict:
            return {"age": age}
        entity.register_action(validated_action)
        # Valid input
        result = entity.execute_action("validated", age=30)
        assert result["age"] == 30
        # Invalid input
        with pytest.raises(Exception):
            entity.execute_action("validated", age=200)

    def test_register_query_action(self):
        """Test registering query-based action."""
        entity = XWEntity(data={"users": [{"name": "Alice", "age": 30}]})
        actions = {
            "get_users": {
                "query": {
                    "format": "xwqs",
                    "query": "SELECT * FROM users"
                }
            }
        }
        entity = XWEntity(data={"users": [{"name": "Alice", "age": 30}]}, actions=actions)
        assert "get_users" in entity.actions

    def test_execute_action_with_args(self):
        """Test executing action with positional args."""
        entity = XWEntity(data={})
        @XWAction(api_name="add")
        def add_action(obj: XWEntity, a: int, b: int) -> int:
            return a + b
        entity.register_action(add_action)
        result = entity.execute_action("add", 10, 20)
        assert result == 30

    def test_execute_action_with_kwargs(self):
        """Test executing action with keyword args."""
        entity = XWEntity(data={})
        @XWAction(api_name="subtract")
        def subtract_action(obj: XWEntity, a: int, b: int) -> int:
            return a - b
        entity.register_action(subtract_action)
        result = entity.execute_action("subtract", a=20, b=10)
        assert result == 10

    def test_execute_action_mixed_args(self):
        """Test executing action with mixed args and kwargs."""
        entity = XWEntity(data={})
        @XWAction(api_name="calculate")
        def calculate_action(obj: XWEntity, a: int, b: int, c: int = 0) -> int:
            return a + b + c
        entity.register_action(calculate_action)
        result = entity.execute_action("calculate", 10, 20, c=5)
        assert result == 35

    def test_list_actions_empty(self):
        """Test listing actions when none registered."""
        entity = XWEntity(data={})
        actions = entity.list_actions()
        assert isinstance(actions, list)
        assert len(actions) == 0

    def test_list_actions_multiple(self):
        """Test listing multiple actions."""
        entity = XWEntity(data={})
        for i in range(5):
            @XWAction(api_name=f"action{i}")
            def action(obj: XWEntity) -> str:
                return f"action{i}"
            entity.register_action(action)
        actions = entity.list_actions()
        assert len(actions) >= 5
        for i in range(5):
            assert f"action{i}" in actions

    def test_action_not_found_error(self):
        """Test error when action not found."""
        entity = XWEntity(data={})
        with pytest.raises(XWEntityActionError):
            entity.execute_action("nonexistent")

    def test_action_attribute_access(self):
        """Test accessing action via attribute."""
        entity = XWEntity(data={"name": "Alice"})
        @XWAction(api_name="get_name")
        def get_name_action(obj: XWEntity) -> str:
            return obj.get("name")
        entity.register_action(get_name_action)
        result = entity.get_name()
        assert result == "Alice"

    def test_action_attribute_with_params(self):
        """Test accessing action via attribute with parameters."""
        entity = XWEntity(data={"value": 10})
        @XWAction(api_name="multiply")
        def multiply_action(obj: XWEntity, factor: int) -> int:
            return obj.get("value") * factor
        entity.register_action(multiply_action)
        result = entity.multiply(5)
        assert result == 50

    def test_action_modifies_entity(self):
        """Test action that modifies entity data."""
        entity = XWEntity(data={"count": 0})
        @XWAction(api_name="increment")
        def increment_action(obj: XWEntity) -> int:
            current = obj.get("count", 0)
            obj.set("count", current + 1)
            return current + 1
        entity.register_action(increment_action)
        result = entity.execute_action("increment")
        assert result == 1
        assert entity.get("count") == 1

    def test_multiple_actions_same_name_overwrites(self):
        """Test registering action with same name overwrites."""
        entity = XWEntity(data={})
        @XWAction(api_name="test")
        def action1(obj: XWEntity) -> str:
            return "first"
        @XWAction(api_name="test")
        def action2(obj: XWEntity) -> str:
            return "second"
        entity.register_action(action1)
        assert entity.execute_action("test") == "first"
        entity.register_action(action2)
        assert entity.execute_action("test") == "second"

    def test_action_with_output_validation(self):
        """Test action with output validation."""
        entity = XWEntity(data={})
        @XWAction(
            api_name="validated_output",
            out_types={"result": XWSchema({"type": "object", "properties": {"value": {"type": "integer"}}})}
        )
        def validated_output_action(obj: XWEntity) -> dict:
            return {"value": 42}
        entity.register_action(validated_output_action)
        result = entity.execute_action("validated_output")
        assert result["value"] == 42

    def test_action_with_handler_function(self):
        """Test registering action with handler function."""
        entity = XWEntity(data={"name": "Alice"})
        def handler(obj: XWEntity) -> str:
            return f"Hello {obj.get('name')}"
        entity.register_action(handler)
        # Handler function name should be used or api_name
        assert len(entity.actions) > 0
