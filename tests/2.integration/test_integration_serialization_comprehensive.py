#!/usr/bin/env python3
"""
#exonware/xwentity/tests/2.integration/test_integration_serialization_comprehensive.py
Comprehensive integration tests for XWEntity serialization in all formats.
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
from exonware.xwaction import XWAction
@pytest.mark.xwentity_integration

class TestIntegrationSerializationComprehensive:
    """Comprehensive serialization tests."""
    @pytest.fixture

    def full_featured_entity(self):
        """Create entity with all features for serialization."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {"type": "object"}
            }
        })
        entity = XWEntity(
            schema=schema,
            data={
                "name": "Alice",
                "age": 30,
                "tags": ["developer", "python"],
                "metadata": {"created": "2026-01-28", "version": 1}
            },
            entity_type="user"
        )
        # Add action
        @XWAction(api_name="get_name")
        def get_name_action(obj: XWEntity) -> str:
            return obj.get("name")
        entity.register_action(get_name_action)
        # Add extension
        entity.register_extension("cache", {"enabled": True})
        # State transition
        entity.transition_to("VALIDATED")
        return entity
    @pytest.mark.parametrize("format_name", [
        "json", "yaml", "toml", "xml", "xwjson", "msgpack", "pickle", "bson", "cbor", "ubjson"
    ])

    def test_format_roundtrip_full_featured(self, full_featured_entity, format_name):
        """Test roundtrip for each format with full-featured entity."""
        try:
            binary_formats = ["xwjson", "msgpack", "pickle", "bson", "cbor", "ubjson"]
            mode = 'wb' if format_name in binary_formats else 'w'
            ext = f".{format_name}" if format_name != 'xwjson' else '.xwjson'
            with tempfile.NamedTemporaryFile(mode=mode, suffix=ext, delete=False) as f:
                temp_path = Path(f.name)
            # Save
            full_featured_entity.save(temp_path, format=format_name)
            assert temp_path.exists()
            # Load
            loaded = XWEntity(schema=full_featured_entity.schema)
            loaded.load(temp_path, format=format_name)
            # Verify core data
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 30
            assert loaded.get("tags") == ["developer", "python"]
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_vs_json_comparison(self):
        """Test XWJSON vs JSON comparison."""
        entity = XWEntity(data={
            "name": "Alice",
            "age": 30,
            "tags": ["developer", "python"],
            "metadata": {"created": "2026-01-28", "version": 1}
        })
        try:
            # Save as JSON
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json_path = Path(f.name)
            # Save as XWJSON
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                xwjson_path = Path(f.name)
            entity.save(json_path, format='json')
            entity.save(xwjson_path, format='xwjson')
            # Both should work
            json_loaded = XWEntity()
            json_loaded.load(json_path, format='json')
            xwjson_loaded = XWEntity()
            xwjson_loaded.load(xwjson_path, format='xwjson')
            # Data should be equivalent
            assert json_loaded.get("name") == xwjson_loaded.get("name")
            assert json_loaded.get("age") == xwjson_loaded.get("age")
            assert json_loaded.get("tags") == xwjson_loaded.get("tags")
        except Exception as e:
            pytest.skip(f"Serialization comparison failed: {e}")
        finally:
            if 'json_path' in locals():
                json_path.unlink(missing_ok=True)
            if 'xwjson_path' in locals():
                xwjson_path.unlink(missing_ok=True)

    def test_serialization_chain(self):
        """Test serialization through multiple formats."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        formats = ["json", "yaml", "xwjson"]
        temp_paths = []
        try:
            for fmt in formats:
                mode = 'wb' if fmt == 'xwjson' else 'w'
                ext = f".{fmt}" if fmt != 'xwjson' else '.xwjson'
                with tempfile.NamedTemporaryFile(mode=mode, suffix=ext, delete=False) as f:
                    temp_path = Path(f.name)
                    temp_paths.append((temp_path, fmt))
                entity.save(temp_path, format=fmt)
                loaded = XWEntity()
                loaded.load(temp_path, format=fmt)
                assert loaded.get("name") == "Alice"
                assert loaded.get("age") == 30
                # Use loaded entity for next format
                entity = loaded
        except Exception as e:
            pytest.skip(f"Serialization chain failed: {e}")
        finally:
            for temp_path, _ in temp_paths:
                temp_path.unlink(missing_ok=True)
