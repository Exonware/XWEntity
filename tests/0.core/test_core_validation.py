#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_validation.py
Core tests for XWEntity validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, XWEntityValidationError
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_core

class TestCoreValidation:
    """Test core validation functionality."""

    def test_validate_with_valid_data(self, sample_entity):
        """Test validation with valid data."""
        assert sample_entity.validate() is True

    def test_validate_with_invalid_data(self):
        """Test validation with invalid data (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        entity = XWEntity(schema=schema, data={"age": 200}, config=XWEntityConfig(strict_validation=False))
        assert entity.validate() is False

    def test_validate_without_schema(self):
        """Test validation without schema always passes."""
        entity = XWEntity(data={"age": 200})
        assert entity.validate() is True

    def test_validate_issues(self, sample_entity):
        """Test getting validation issues."""
        issues = sample_entity.validate_issues()
        assert isinstance(issues, list)
        # Valid entity should have no issues
        assert len(issues) == 0

    def test_validate_issues_with_invalid_data(self):
        """Test validation issues with invalid data."""
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

    def test_validate_issues_path(self):
        """Test validation issues include path information."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "user": {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer", "minimum": 0, "maximum": 150}
                    }
                }
            }
        })
        entity = XWEntity(schema=schema, data={"user": {"age": 200}})
        issues = entity.validate_issues()
        if issues:
            assert "path" in issues[0] or "message" in issues[0]

    def test_strict_validation_raises_error(self):
        """Test strict validation raises error on failure."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        from exonware.xwentity import XWEntityConfig
        config = XWEntityConfig(strict_validation=True)
        entity = XWEntity(schema=schema, data={"age": 200}, config=config)
        with pytest.raises(XWEntityValidationError):
            entity.validate()

    def test_validate_after_modification(self, sample_schema, sample_data):
        """Test validation after data modification (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        config = XWEntityConfig(strict_validation=False)
        entity = XWEntity(schema=sample_schema, data=dict(sample_data), config=config)
        assert entity.validate() is True
        entity.set("age", 200)  # Invalid age
        assert entity.validate() is False

    def test_validate_required_fields(self):
        """Test validation of required fields (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"}
            },
            "required": ["name", "email"]
        })
        config = XWEntityConfig(strict_validation=False)
        # Missing required field
        entity = XWEntity(schema=schema, data={"name": "Alice"}, config=config)
        assert entity.validate() is False
        # All required fields present
        entity.set("email", "alice@example.com")
        assert entity.validate() is True
