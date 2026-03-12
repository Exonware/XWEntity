#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_errors.py
Unit tests for XWEntity error handling.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import (
    XWEntity,
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityDataError,
    EntityState
)
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_unit

class TestEntityErrors:
    """Test XWEntity error handling."""

    def test_invalid_schema_type(self):
        """Test error with invalid schema type."""
        with pytest.raises(XWEntityError):
            XWEntity(schema=123)  # Invalid schema type

    def test_invalid_json_schema_string(self):
        """Test error with invalid JSON schema string."""
        with pytest.raises(Exception):  # May raise JSON decode error or XWEntityError
            XWEntity(schema='{"invalid": json}')  # Invalid JSON

    def test_validation_error_strict_mode(self):
        """Test validation error in strict mode."""
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

    def test_state_transition_error(self):
        """Test state transition error."""
        entity = XWEntity(data={})
        # Cannot go directly from DRAFT to COMMITTED
        with pytest.raises(XWEntityStateError):
            entity.transition_to(EntityState.COMMITTED)

    def test_action_not_found_error(self):
        """Test action not found error."""
        entity = XWEntity(data={})
        with pytest.raises(XWEntityActionError):
            entity.execute_action("nonexistent")

    def test_load_invalid_format(self):
        """Test error loading invalid format."""
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("not valid json")
            temp_path = Path(f.name)
        try:
            entity = XWEntity()
            with pytest.raises(Exception):  # May raise various errors
                entity.load(temp_path, format='json')
        finally:
            temp_path.unlink(missing_ok=True)

    def test_load_nonexistent_file(self):
        """Test error loading nonexistent file."""
        entity = XWEntity()
        with pytest.raises(Exception):  # FileNotFoundError or XWEntityError
            entity.load("nonexistent_file.json")

    def test_from_dict_invalid_data(self):
        """Test error with invalid data type."""
        with pytest.raises(XWEntityError):
            XWEntity.from_dict("not a dict")  # Should be dict

    def test_attribute_error(self):
        """Test AttributeError for non-existent attribute."""
        entity = XWEntity(data={})
        with pytest.raises(AttributeError):
            _ = entity.nonexistent_attribute
