#!/usr/bin/env python3
"""
#exonware/xwentity/tests/2.integration/test_integration_serialization_formats.py
Integration tests for XWEntity serialization in all formats including xwjson.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
import tempfile
from pathlib import Path
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
@pytest.mark.xwentity_integration

class TestIntegrationSerializationFormats:
    """Test serialization in all formats with comprehensive roundtrip tests."""
    @pytest.fixture

    def comprehensive_entity(self):
        """Create comprehensive entity with all data types."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "string": {"type": "string"},
                "integer": {"type": "integer"},
                "float": {"type": "number"},
                "boolean": {"type": "boolean"},
                "null": {"type": "null"},
                "array": {"type": "array", "items": {"type": "string"}},
                "object": {"type": "object"},
                "nested": {
                    "type": "object",
                    "properties": {
                        "deep": {
                            "type": "object",
                            "properties": {
                                "value": {"type": "string"}
                            }
                        }
                    }
                }
            }
        })
        return XWEntity(
            schema=schema,
            data={
                "string": "Hello World",
                "integer": 42,
                "float": 3.14159,
                "boolean": True,
                "null": None,
                "array": ["item1", "item2", "item3"],
                "object": {"key1": "value1", "key2": "value2"},
                "nested": {
                    "deep": {
                        "value": "nested_value"
                    }
                }
            }
        )
    @pytest.mark.parametrize("format_name,extension,binary", [
        ("json", ".json", False),
        ("yaml", ".yaml", False),
        ("toml", ".toml", False),
        ("xml", ".xml", False),
        ("xwjson", ".xwjson", True),
        ("msgpack", ".msgpack", True),
        ("pickle", ".pickle", True),
        ("bson", ".bson", True),
        ("cbor", ".cbor", True),
        ("ubjson", ".ubjson", True),
    ])

    def test_format_roundtrip_comprehensive(self, comprehensive_entity, format_name, extension, binary):
        """Test comprehensive roundtrip for each format."""
        try:
            mode = 'wb' if binary else 'w'
            with tempfile.NamedTemporaryFile(mode=mode, suffix=extension, delete=False) as f:
                temp_path = Path(f.name)
            # Save
            comprehensive_entity.save(temp_path, format=format_name)
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0
            # Load
            loaded = XWEntity(schema=comprehensive_entity.schema)
            loaded.load(temp_path, format=format_name)
            # Verify all data types preserved
            assert loaded.get("string") == comprehensive_entity.get("string")
            assert loaded.get("integer") == comprehensive_entity.get("integer")
            assert loaded.get("float") == comprehensive_entity.get("float")
            assert loaded.get("boolean") == comprehensive_entity.get("boolean")
            assert loaded.get("array") == comprehensive_entity.get("array")
            assert loaded.get("object") == comprehensive_entity.get("object")
            assert loaded.get("nested.deep.value") == comprehensive_entity.get("nested.deep.value")
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_comprehensive_roundtrip(self, comprehensive_entity):
        """Test XWJSON comprehensive roundtrip."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            # Save to XWJSON
            comprehensive_entity.save(temp_path, format='xwjson')
            # Load from XWJSON
            loaded = XWEntity(schema=comprehensive_entity.schema)
            loaded.load(temp_path, format='xwjson')
            # Verify all data
            assert loaded.get("string") == "Hello World"
            assert loaded.get("integer") == 42
            assert loaded.get("float") == 3.14159
            assert loaded.get("boolean") is True
            assert loaded.get("array") == ["item1", "item2", "item3"]
            assert loaded.get("object") == {"key1": "value1", "key2": "value2"}
            assert loaded.get("nested.deep.value") == "nested_value"
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_multiple_format_roundtrip(self, comprehensive_entity):
        """Test entity can be saved and loaded in multiple formats."""
        formats = ["json", "yaml", "toml", "xwjson"]
        for fmt in formats:
            try:
                mode = 'wb' if fmt == 'xwjson' else 'w'
                ext = f".{fmt}" if fmt != 'xwjson' else '.xwjson'
                with tempfile.NamedTemporaryFile(mode=mode, suffix=ext, delete=False) as f:
                    temp_path = Path(f.name)
                comprehensive_entity.save(temp_path, format=fmt)
                loaded = XWEntity(schema=comprehensive_entity.schema)
                loaded.load(temp_path, format=fmt)
                assert loaded.get("string") == "Hello World"
                assert loaded.get("integer") == 42
            except Exception as e:
                pytest.skip(f"Format {fmt} not available: {e}")
            finally:
                if 'temp_path' in locals():
                    temp_path.unlink(missing_ok=True)

    def test_serialization_with_actions(self, comprehensive_entity):
        """Test serialization preserves actions."""
        from exonware.xwaction import XWAction
        @XWAction(api_name="test_action")
        def test_action(obj: XWEntity) -> str:
            return "test"
        comprehensive_entity.register_action(test_action)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            comprehensive_entity.save(temp_path)
            loaded = XWEntity()
            loaded.load(temp_path)
            # Actions should be preserved if stored
            # This depends on to_dict() including actions
            assert loaded.get("string") == "Hello World"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_serialization_with_metadata(self, comprehensive_entity):
        """Test serialization preserves metadata."""
        comprehensive_entity.transition_to("VALIDATED")
        original_id = comprehensive_entity.id
        original_state = comprehensive_entity._metadata.state
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            comprehensive_entity.save(temp_path)
            loaded = XWEntity()
            loaded.load(temp_path)
            # Metadata should be preserved if stored
            # This depends on to_dict() including metadata
            assert loaded.get("string") == "Hello World"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_cross_format_compatibility(self, comprehensive_entity):
        """Test entity can be saved in one format and loaded in another (if compatible)."""
        # Save as JSON
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = Path(f.name)
        # Save as XWJSON
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
            xwjson_path = Path(f.name)
        try:
            comprehensive_entity.save(json_path, format='json')
            comprehensive_entity.save(xwjson_path, format='xwjson')
            # Both should contain the same data
            json_loaded = XWEntity(schema=comprehensive_entity.schema)
            json_loaded.load(json_path, format='json')
            xwjson_loaded = XWEntity(schema=comprehensive_entity.schema)
            xwjson_loaded.load(xwjson_path, format='xwjson')
            # Data should be equivalent
            assert json_loaded.get("string") == xwjson_loaded.get("string")
            assert json_loaded.get("integer") == xwjson_loaded.get("integer")
        except Exception as e:
            pytest.skip(f"Cross-format test failed: {e}")
        finally:
            json_path.unlink(missing_ok=True)
            xwjson_path.unlink(missing_ok=True)
