#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_schema_validation.py
Core tests for XWEntity schema validation.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 08-Nov-2025
"""

import pytest
from exonware.xwentity import XWEntity, XWEntityValidationError
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
@pytest.mark.xwentity_core

class TestCoreSchemaValidation:
    """Test core schema validation functionality."""

    def test_validate_with_valid_data(self, sample_schema, sample_xwdata):
        """Test validation with valid data."""
        obj = XWEntity(schema=sample_schema, data=sample_xwdata)
        assert obj.validate() is True

    def test_validate_with_invalid_data(self, sample_schema):
        """Test validation with invalid data (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        invalid_data = XWData.from_native({"name": "Alice", "age": 200})  # age > 150
        obj = XWEntity(schema=sample_schema, data=invalid_data, config=XWEntityConfig(strict_validation=False))
        assert obj.validate() is False

    def test_validate_with_missing_required_field(self, sample_schema):
        """Test validation with missing required field (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        incomplete_data = XWData.from_native({"age": 30})  # missing "name"
        obj = XWEntity(schema=sample_schema, data=incomplete_data, config=XWEntityConfig(strict_validation=False))
        assert obj.validate() is False

    def test_validate_without_schema(self, sample_xwdata):
        """Test validation without schema (should pass)."""
        obj = XWEntity(data=sample_xwdata)
        assert obj.validate() is True  # No schema means no validation

    def test_validate_with_empty_data(self, sample_schema):
        """Test validation with empty data (non-strict: returns False)."""
        from exonware.xwentity import XWEntityConfig
        empty_data = XWData.from_native({})
        obj = XWEntity(schema=sample_schema, data=empty_data, config=XWEntityConfig(strict_validation=False))
        assert obj.validate() is False  # Missing required "name" field

    def test_schema_property(self, sample_schema, sample_xwdata):
        """Test schema property access."""
        obj = XWEntity(schema=sample_schema, data=sample_xwdata)
        assert obj.schema is sample_schema
