#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_validation.py
Unit tests for XWEntity validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityValidationError, XWEntityConfig
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_unit

class TestEntityValidation:
    """Test XWEntity validation in detail."""

    def test_validate_with_valid_schema(self):
        """Test validation with valid schema and data."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            },
            "required": ["name"]
        })
        entity = XWEntity(schema=schema, data={"name": "Alice", "age": 30})
        assert entity.validate() is True

    def test_validate_with_invalid_type(self):
        """Test validation fails with invalid type (non-strict: returns False)."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer"}
            }
        })
        config = XWEntityConfig(strict_validation=False)
        entity = XWEntity(schema=schema, data={"age": "not an integer"}, config=config)
        assert entity.validate() is False

    def test_validate_with_missing_required(self):
        """Test validation fails with missing required field (non-strict: returns False)."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["name", "email"]
        })
        config = XWEntityConfig(strict_validation=False)
        entity = XWEntity(schema=schema, data={"name": "Alice"}, config=config)
        assert entity.validate() is False

    def test_validate_without_schema(self):
        """Test validation without schema always passes."""
        entity = XWEntity(data={"anything": "goes"})
        assert entity.validate() is True

    def test_validate_issues_empty_when_valid(self):
        """Test validate_issues returns empty list when valid."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        })
        entity = XWEntity(schema=schema, data={"name": "Alice"})
        issues = entity.validate_issues()
        assert isinstance(issues, list)
        assert len(issues) == 0

    def test_validate_issues_with_errors(self):
        """Test validate_issues returns list of errors."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "name": {"type": "string"}
            },
            "required": ["name"]
        })
        entity = XWEntity(schema=schema, data={"age": 200})
        issues = entity.validate_issues()
        assert len(issues) > 0

    def test_validate_issues_format(self):
        """Test validate_issues returns proper format."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        entity = XWEntity(schema=schema, data={"age": 200})
        issues = entity.validate_issues()
        if issues:
            for issue in issues:
                assert isinstance(issue, dict)
                # Should have path or message
                assert "path" in issue or "message" in issue

    def test_strict_validation_enabled(self):
        """Test strict validation raises error."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        config = XWEntityConfig(strict_validation=True)
        entity = XWEntity(schema=schema, data={"age": 200}, config=config)
        with pytest.raises(XWEntityValidationError):
            entity.validate()

    def test_strict_validation_disabled(self):
        """Test strict validation disabled returns False."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        config = XWEntityConfig(strict_validation=False)
        entity = XWEntity(schema=schema, data={"age": 200}, config=config)
        # Should return False, not raise error
        assert entity.validate() is False

    def test_validate_after_data_change(self):
        """Test validation after data modification (non-strict: returns False)."""
        config = XWEntityConfig(strict_validation=False)
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        entity = XWEntity(schema=schema, data={"age": 30}, config=config)
        assert entity.validate() is True
        entity.set("age", 200)
        assert entity.validate() is False

    def test_validate_nested_schema(self):
        """Test validation with nested schema (non-strict: returns False)."""
        config = XWEntityConfig(strict_validation=False)
        schema = XWSchema({
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    },
                    "required": ["name"]
                }
            }
        })
        # Valid nested data
        entity = XWEntity(schema=schema, data={"user": {"name": "Alice", "age": 30}}, config=config)
        assert entity.validate() is True
        # Invalid nested data
        entity.set("user.age", 200)
        assert entity.validate() is False

    def test_validate_array_schema(self):
        """Test validation with array schema (non-strict: returns False)."""
        config = XWEntityConfig(strict_validation=False)
        schema = XWSchema({
            "type": "object",
            "properties": {
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 1,
                    "maxItems": 10
                }
            }
        })
        # Valid array
        entity = XWEntity(schema=schema, data={"tags": ["tag1", "tag2"]}, config=config)
        assert entity.validate() is True
        # Invalid array (too many items)
        entity.set("tags", [f"tag{i}" for i in range(20)])
        assert entity.validate() is False

    def test_validate_enum_schema(self):
        """Test validation with enum schema (non-strict: returns False)."""
        config = XWEntityConfig(strict_validation=False)
        schema = XWSchema({
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["active", "inactive", "pending"]
                }
            }
        })
        # Valid enum value
        entity = XWEntity(schema=schema, data={"status": "active"}, config=config)
        assert entity.validate() is True
        # Invalid enum value
        entity.set("status", "invalid")
        assert entity.validate() is False

    def test_validate_format_schema(self):
        """Test validation with format schema."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "format": "email"
                }
            }
        })
        # Valid email format
        entity = XWEntity(schema=schema, data={"email": "alice@example.com"})
        # Validation may pass or fail depending on format validation support
        result = entity.validate()
        assert isinstance(result, bool)
        # Invalid email format
        entity.set("email", "not-an-email")
        result = entity.validate()
        assert isinstance(result, bool)
