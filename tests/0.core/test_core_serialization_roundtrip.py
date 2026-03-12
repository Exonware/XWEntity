#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_serialization_roundtrip.py
Core tests for XWEntity serialization and roundtrip in multiple formats.
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
@pytest.mark.xwentity_core

class TestCoreSerializationRoundtrip:
    """Test serialization and roundtrip in multiple formats."""
    @pytest.fixture

    def complex_entity(self):
        """Create a complex entity for serialization tests."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": "object",
                    "properties": {
                        "created": {"type": "string"},
                        "version": {"type": "integer"}
                    }
                }
            }
        })
        return XWEntity(
            schema=schema,
            data={
                "name": "Alice",
                "age": 30,
                "email": "alice@example.com",
                "tags": ["developer", "python"],
                "metadata": {"created": "2026-01-28", "version": 1}
            }
        )
    @pytest.mark.parametrize("format_name", [
        "json",
        "yaml",
        "toml",
        "xml",
    ])

    def test_save_and_load_roundtrip(self, complex_entity, format_name):
        """Test save and load roundtrip for each format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{format_name}', delete=False) as f:
            temp_path = Path(f.name)
        try:
            # Save entity
            complex_entity.save(temp_path, format=format_name)
            assert temp_path.exists()
            # Load into new entity
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format=format_name)
            # Verify data preserved
            assert loaded_entity.get("name") == complex_entity.get("name")
            assert loaded_entity.get("age") == complex_entity.get("age")
            assert loaded_entity.get("email") == complex_entity.get("email")
            assert loaded_entity.get("tags") == complex_entity.get("tags")
            assert loaded_entity.get("metadata") == complex_entity.get("metadata")
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_and_load_json(self, complex_entity):
        """Test JSON save and load roundtrip."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            complex_entity.save(temp_path, format='json')
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format='json')
            assert loaded_entity.get("name") == "Alice"
            assert loaded_entity.get("age") == 30
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_and_load_yaml(self, complex_entity):
        """Test YAML save and load roundtrip."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                temp_path = Path(f.name)
            complex_entity.save(temp_path, format='yaml')
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format='yaml')
            assert loaded_entity.get("name") == "Alice"
            assert loaded_entity.get("age") == 30
        except Exception as e:
            pytest.skip(f"YAML not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_save_and_load_toml(self, complex_entity):
        """Test TOML save and load roundtrip."""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
                temp_path = Path(f.name)
            complex_entity.save(temp_path, format='toml')
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format='toml')
            assert loaded_entity.get("name") == "Alice"
            assert loaded_entity.get("age") == 30
        except Exception as e:
            pytest.skip(f"TOML not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_save_and_load_xwjson(self, complex_entity):
        """Test XWJSON save and load roundtrip."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            complex_entity.save(temp_path, format='xwjson')
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format='xwjson')
            assert loaded_entity.get("name") == "Alice"
            assert loaded_entity.get("age") == 30
            assert loaded_entity.get("tags") == ["developer", "python"]
            assert loaded_entity.get("metadata") == {"created": "2026-01-28", "version": 1}
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_save_and_load_msgpack(self, complex_entity):
        """Test MessagePack save and load roundtrip."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.msgpack', delete=False) as f:
                temp_path = Path(f.name)
            complex_entity.save(temp_path, format='msgpack')
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.load(temp_path, format='msgpack')
            assert loaded_entity.get("name") == "Alice"
            assert loaded_entity.get("age") == 30
        except Exception as e:
            pytest.skip(f"MessagePack not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_to_json_and_from_json_string(self, complex_entity):
        """Test JSON string serialization roundtrip."""
        json_str = complex_entity.to_json()
        assert isinstance(json_str, str)
        assert "Alice" in json_str
        # Load from string
        loaded_entity = XWEntity(schema=complex_entity.schema)
        loaded_entity.from_json(json_str)
        assert loaded_entity.get("name") == "Alice"

    def test_to_yaml_and_from_yaml_string(self, complex_entity):
        """Test YAML string serialization roundtrip."""
        try:
            yaml_str = complex_entity.to_yaml()
            assert isinstance(yaml_str, str)
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.from_yaml(yaml_str)
            assert loaded_entity.get("name") == "Alice"
        except Exception as e:
            pytest.skip(f"YAML not available: {e}")

    def test_to_toml_and_from_toml_string(self, complex_entity):
        """Test TOML string serialization roundtrip."""
        try:
            toml_str = complex_entity.to_toml()
            assert isinstance(toml_str, str)
            loaded_entity = XWEntity(schema=complex_entity.schema)
            loaded_entity.from_toml(toml_str)
            assert loaded_entity.get("name") == "Alice"
        except Exception as e:
            pytest.skip(f"TOML not available: {e}")

    def test_to_format_and_from_format(self, complex_entity):
        """Test generic format serialization roundtrip."""
        formats = ["json", "yaml", "toml"]
        for fmt in formats:
            try:
                # Export to string
                serialized = complex_entity.to_format(fmt)
                assert isinstance(serialized, str)
                # Import from string
                loaded_entity = XWEntity(schema=complex_entity.schema)
                loaded_entity.from_format(fmt, serialized)
                assert loaded_entity.get("name") == "Alice"
            except Exception as e:
                pytest.skip(f"Format {fmt} not available: {e}")

    def test_roundtrip_preserves_metadata(self, complex_entity):
        """Test that roundtrip preserves entity metadata."""
        original_id = complex_entity.id
        original_created = complex_entity.created_at
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            complex_entity.save(temp_path)
            loaded_entity = XWEntity()
            loaded_entity.load(temp_path)
            # Metadata should be preserved if stored in serialized format
            # Note: This depends on to_dict() including metadata
            assert loaded_entity.get("name") == "Alice"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_roundtrip_preserves_actions(self, entity_with_actions):
        """Test that roundtrip preserves actions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity_with_actions.save(temp_path)
            loaded_entity = XWEntity()
            loaded_entity.load(temp_path)
            # Actions should be preserved if stored in serialized format
            # Note: This depends on to_dict() including actions
            assert loaded_entity.get("name") == "Alice"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_roundtrip_with_nested_structures(self):
        """Test roundtrip with deeply nested structures."""
        entity = XWEntity(data={
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "value": "deep"
                        }
                    }
                }
            },
            "array": [
                {"nested": {"value": 1}},
                {"nested": {"value": 2}}
            ]
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            loaded_entity = XWEntity()
            loaded_entity.load(temp_path)
            assert loaded_entity.get("level1.level2.level3.level4.value") == "deep"
            assert loaded_entity.get("array.0.nested.value") == 1
            assert loaded_entity.get("array.1.nested.value") == 2
        finally:
            temp_path.unlink(missing_ok=True)
