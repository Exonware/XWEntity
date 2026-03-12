#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_action_validation.py
Core tests for XWEntity action execution with input/output validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 08-Nov-2025
"""

import pytest
from exonware.xwentity import XWEntity, XWEntityActionError, XWEntityValidationError
from exonware.xwschema import XWSchema, XWSchemaValidationError
from exonware.xwdata import XWData
from exonware.xwaction import XWAction
@pytest.mark.xwentity_core

class TestCoreActionValidation:
    """Test core action execution with validation."""

    def test_execute_action_with_valid_input(self, sample_object, action_with_schema):
        """Test action execution with valid input that passes validation."""
        sample_object.register_action(action_with_schema)
        result = sample_object.execute_action("update_age", age=25)
        assert result.get("success") is True
        assert sample_object.get("age") == 25

    def test_execute_action_with_invalid_input(self, sample_object, action_with_schema):
        """Test action execution with invalid input that fails validation."""
        sample_object.register_action(action_with_schema)
        # XWAction.execute() raises XWSchemaValidationError when validation fails
        with pytest.raises((XWEntityValidationError, XWSchemaValidationError)):
            sample_object.execute_action("update_age", age=200)  # age > 150

    def test_execute_action_with_missing_action(self, sample_object):
        """Test action execution with non-existent action."""
        with pytest.raises(XWEntityActionError, match="Action 'nonexistent' not found"):
            sample_object.execute_action("nonexistent")

    def test_action_input_validation_uses_schema(self, sample_object):
        """Test that action input validation uses XWSchema."""
        from exonware.xwschema import XWSchema
        @XWAction(
            api_name="test_action",
            in_types={"value": XWSchema({"type": "string", "minLength": 3})}
        )
        def test_action(obj: XWEntity, value: str) -> str:
            return value
        sample_object.register_action(test_action)
        # Valid input
        result = sample_object.execute_action("test_action", value="valid")
        assert result == "valid"
        # Invalid input (too short)
        # XWAction.execute() raises XWSchemaValidationError when validation fails
        with pytest.raises((XWEntityValidationError, XWSchemaValidationError)):
            sample_object.execute_action("test_action", value="ab")  # < minLength 3

    def test_action_output_validation_uses_schema(self, sample_object):
        """Test that action output validation uses XWSchema."""
        from exonware.xwschema import XWSchema
        @XWAction(
            api_name="test_action",
            out_types={"result": XWSchema({"type": "object", "properties": {"value": {"type": "integer"}}})}
        )
        def test_action(obj: XWEntity) -> dict:
            return {"value": 42}
        sample_object.register_action(test_action)
        # Valid output
        result = sample_object.execute_action("test_action")
        assert result["value"] == 42

    def test_list_actions(self, sample_object, action_with_schema):
        """Test listing registered actions."""
        sample_object.register_action(action_with_schema)
        actions = sample_object.list_actions()
        assert "update_age" in actions
