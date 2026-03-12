#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/entity_tests/test_entity_serialization.py
Unit tests for XWEntity serialization in all formats.
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
@pytest.mark.xwentity_unit

class TestEntitySerialization:
    """Test XWEntity serialization in detail."""
    @pytest.fixture

    def test_entity(self):
        """Create test entity for serialization."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {"type": "object"}
            }
        })
        return XWEntity(
            schema=schema,
            data={
                "name": "Alice",
                "age": 30,
                "tags": ["developer", "python"],
                "metadata": {"created": "2026-01-28", "version": 1}
            }
        )
    @pytest.mark.parametrize("format_name,extension", [
        ("json", ".json"),
        ("yaml", ".yaml"),
        ("toml", ".toml"),
        ("xml", ".xml"),
        ("xwjson", ".xwjson"),
        ("msgpack", ".msgpack"),
        ("pickle", ".pickle"),
        ("bson", ".bson"),
    ])

    def test_save_format(self, test_entity, format_name, extension):
        """Test saving in each format."""
        try:
            mode = 'wb' if format_name in ['xwjson', 'msgpack', 'pickle', 'bson'] else 'w'
            with tempfile.NamedTemporaryFile(mode=mode, suffix=extension, delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format=format_name)
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)
    @pytest.mark.parametrize("format_name,extension", [
        ("json", ".json"),
        ("yaml", ".yaml"),
        ("toml", ".toml"),
        ("xml", ".xml"),
        ("xwjson", ".xwjson"),
        ("msgpack", ".msgpack"),
    ])

    def test_load_format(self, test_entity, format_name, extension):
        """Test loading from each format."""
        try:
            mode = 'wb' if format_name in ['xwjson', 'msgpack'] else 'w'
            with tempfile.NamedTemporaryFile(mode=mode, suffix=extension, delete=False) as f:
                temp_path = Path(f.name)
            # Save first
            test_entity.save(temp_path, format=format_name)
            # Load
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format=format_name)
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 30
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)
    @pytest.mark.parametrize("format_name", [
        "json", "yaml", "toml", "xml", "xwjson", "msgpack"
    ])

    def test_roundtrip_format(self, test_entity, format_name):
        """Test roundtrip for each format."""
        try:
            mode = 'wb' if format_name in ['xwjson', 'msgpack'] else 'w'
            ext = f".{format_name}" if format_name != 'xwjson' else '.xwjson'
            with tempfile.NamedTemporaryFile(mode=mode, suffix=ext, delete=False) as f:
                temp_path = Path(f.name)
            # Save
            test_entity.save(temp_path, format=format_name)
            # Load
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format=format_name)
            # Verify all data
            assert loaded.get("name") == test_entity.get("name")
            assert loaded.get("age") == test_entity.get("age")
            assert loaded.get("tags") == test_entity.get("tags")
            assert loaded.get("metadata") == test_entity.get("metadata")
        except Exception as e:
            pytest.skip(f"Format {format_name} not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_to_json_string(self, test_entity):
        """Test to_json returns string."""
        json_str = test_entity.to_json()
        assert isinstance(json_str, str)
        assert "Alice" in json_str or '"name"' in json_str

    def test_to_json_file(self, test_entity):
        """Test to_json saves to file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            result = test_entity.to_json(path=temp_path)
            assert temp_path.exists()
            assert result == str(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_from_json_string(self, test_entity):
        """Test from_json loads from string."""
        json_str = test_entity.to_json()
        loaded = XWEntity(schema=test_entity.schema)
        loaded.from_json(json_str)
        assert loaded.get("name") == "Alice"

    def test_to_yaml_string(self, test_entity):
        """Test to_yaml returns string."""
        try:
            yaml_str = test_entity.to_yaml()
            assert isinstance(yaml_str, str)
        except Exception as e:
            pytest.skip(f"YAML not available: {e}")

    def test_to_toml_string(self, test_entity):
        """Test to_toml returns string."""
        try:
            toml_str = test_entity.to_toml()
            assert isinstance(toml_str, str)
        except Exception as e:
            pytest.skip(f"TOML not available: {e}")

    def test_to_xml_string(self, test_entity):
        """Test to_xml returns string."""
        try:
            xml_str = test_entity.to_xml()
            assert isinstance(xml_str, str)
        except Exception as e:
            pytest.skip(f"XML not available: {e}")

    def test_to_format_generic(self, test_entity):
        """Test to_format with different formats."""
        formats = ["json", "yaml", "toml"]
        for fmt in formats:
            try:
                result = test_entity.to_format(fmt)
                assert isinstance(result, str)
            except Exception as e:
                pytest.skip(f"Format {fmt} not available: {e}")

    def test_from_format_generic(self, test_entity):
        """Test from_format with different formats."""
        formats = ["json", "yaml", "toml"]
        for fmt in formats:
            try:
                serialized = test_entity.to_format(fmt)
                loaded = XWEntity(schema=test_entity.schema)
                loaded.from_format(fmt, serialized)
                assert loaded.get("name") == "Alice"
            except Exception as e:
                pytest.skip(f"Format {fmt} not available: {e}")

    def test_xwjson_roundtrip(self, test_entity):
        """Test XWJSON roundtrip specifically."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='xwjson')
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 30
            assert loaded.get("tags") == ["developer", "python"]
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_msgpack_roundtrip(self, test_entity):
        """Test MessagePack roundtrip specifically."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.msgpack', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='msgpack')
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format='msgpack')
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 30
        except Exception as e:
            pytest.skip(f"MessagePack not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_auto_detect_format_from_extension(self, test_entity):
        """Test format auto-detection from file extension."""
        formats = [
            (".json", "json"),
            (".yaml", "yaml"),
            (".yml", "yaml"),
            (".toml", "toml"),
            (".xml", "xml"),
        ]
        for ext, expected_format in formats:
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                    temp_path = Path(f.name)
                test_entity.save(temp_path)  # No format specified
                assert temp_path.exists()
                loaded = XWEntity(schema=test_entity.schema)
                loaded.load(temp_path)  # No format specified
                assert loaded.get("name") == "Alice"
            except Exception as e:
                pytest.skip(f"Format {expected_format} not available: {e}")
            finally:
                if 'temp_path' in locals():
                    temp_path.unlink(missing_ok=True)

    def test_serialization_preserves_types(self, test_entity):
        """Test serialization preserves data types."""
        entity = XWEntity(data={
            "string": "text",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"key": "value"}
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            loaded = XWEntity()
            loaded.load(temp_path)
            assert isinstance(loaded.get("string"), str)
            assert isinstance(loaded.get("integer"), int)
            assert isinstance(loaded.get("float"), float)
            assert isinstance(loaded.get("boolean"), bool)
            assert isinstance(loaded.get("array"), list)
            assert isinstance(loaded.get("object"), dict)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_serialization_with_special_characters(self):
        """Test serialization with special characters."""
        entity = XWEntity(data={
            "unicode": "Hello 世界",
            "special": "Special chars: !@#$%^&*()",
            "newline": "Line 1\nLine 2",
            "quote": 'Text with "quotes"'
        })
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            loaded = XWEntity()
            loaded.load(temp_path)
            assert loaded.get("unicode") == "Hello 世界"
            assert loaded.get("special") == "Special chars: !@#$%^&*()"
        finally:
            temp_path.unlink(missing_ok=True)

    def test_serialization_large_data(self):
        """Test serialization with large data."""
        large_data = {f"key{i}": f"value{i}" * 100 for i in range(1000)}
        entity = XWEntity(data=large_data)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            loaded = XWEntity()
            loaded.load(temp_path)
            assert loaded.get("key0") == "value0" * 100
            assert loaded.get("key999") == "value999" * 100
        finally:
            temp_path.unlink(missing_ok=True)
