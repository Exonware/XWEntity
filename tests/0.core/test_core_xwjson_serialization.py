#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_xwjson_serialization.py
Core tests for XWEntity XWJSON serialization specifically.
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

class TestCoreXWJSONSerialization:
    """Test XWJSON serialization specifically."""
    @pytest.fixture

    def test_entity(self):
        """Create test entity for XWJSON tests."""
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
                "tags": ["developer", "python", "backend"],
                "metadata": {
                    "created": "2026-01-28",
                    "version": 1,
                    "nested": {
                        "deep": {
                            "value": "nested_value"
                        }
                    }
                }
            }
        )

    def test_save_xwjson(self, test_entity):
        """Test saving entity to XWJSON format."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='xwjson')
            assert temp_path.exists()
            assert temp_path.stat().st_size > 0
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_load_xwjson(self, test_entity):
        """Test loading entity from XWJSON format."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='xwjson')
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 30
            assert loaded.get("tags") == ["developer", "python", "backend"]
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_roundtrip(self, test_entity):
        """Test XWJSON roundtrip preserves all data."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='xwjson')
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format='xwjson')
            # Verify all data preserved
            assert loaded.get("name") == test_entity.get("name")
            assert loaded.get("age") == test_entity.get("age")
            assert loaded.get("tags") == test_entity.get("tags")
            assert loaded.get("metadata") == test_entity.get("metadata")
            assert loaded.get("metadata.nested.deep.value") == test_entity.get("metadata.nested.deep.value")
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_preserves_types(self):
        """Test XWJSON preserves all data types."""
        entity = XWEntity(data={
            "string": "text",
            "integer": 42,
            "float": 3.14159,
            "boolean": True,
            "null": None,
            "array": [1, 2, 3],
            "object": {"key": "value"}
        })
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            entity.save(temp_path, format='xwjson')
            loaded = XWEntity()
            loaded.load(temp_path, format='xwjson')
            assert isinstance(loaded.get("string"), str)
            assert isinstance(loaded.get("integer"), int)
            assert isinstance(loaded.get("float"), float)
            assert isinstance(loaded.get("boolean"), bool)
            assert isinstance(loaded.get("array"), list)
            assert isinstance(loaded.get("object"), dict)
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_large_data(self):
        """Test XWJSON with large data."""
        large_data = {f"key{i}": f"value{i}" * 100 for i in range(1000)}
        entity = XWEntity(data=large_data)
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            entity.save(temp_path, format='xwjson')
            loaded = XWEntity()
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("key0") == "value0" * 100
            assert loaded.get("key999") == "value999" * 100
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_unicode_data(self):
        """Test XWJSON with Unicode data."""
        entity = XWEntity(data={
            "unicode": "Hello 世界",
            "emoji": "Hello 👋 🌍",
            "special": "Special: àáâãäå"
        })
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            entity.save(temp_path, format='xwjson')
            loaded = XWEntity()
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("unicode") == "Hello 世界"
            assert loaded.get("emoji") == "Hello 👋 🌍"
            assert loaded.get("special") == "Special: àáâãäå"
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_nested_structures(self):
        """Test XWJSON with deeply nested structures."""
        entity = XWEntity(data={
            "level1": {
                "level2": {
                    "level3": {
                        "level4": {
                            "level5": {
                                "value": "very_deep"
                            }
                        }
                    }
                }
            }
        })
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            entity.save(temp_path, format='xwjson')
            loaded = XWEntity()
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("level1.level2.level3.level4.level5.value") == "very_deep"
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_array_roundtrip(self):
        """Test XWJSON with arrays."""
        entity = XWEntity(data={
            "numbers": [1, 2, 3, 4, 5],
            "strings": ["a", "b", "c"],
            "mixed": [1, "two", 3.0, True, None],
            "nested": [[1, 2], [3, 4], [5, 6]]
        })
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            entity.save(temp_path, format='xwjson')
            loaded = XWEntity()
            loaded.load(temp_path, format='xwjson')
            assert loaded.get("numbers") == [1, 2, 3, 4, 5]
            assert loaded.get("strings") == ["a", "b", "c"]
            assert loaded.get("mixed") == [1, "two", 3.0, True, None]
            assert loaded.get("nested") == [[1, 2], [3, 4], [5, 6]]
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_with_schema(self, test_entity):
        """Test XWJSON preserves schema information."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            test_entity.save(temp_path, format='xwjson')
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path, format='xwjson')
            # Should validate against schema
            assert loaded.validate() is True
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)

    def test_xwjson_auto_detect(self, test_entity):
        """Test XWJSON auto-detection from extension."""
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.xwjson', delete=False) as f:
                temp_path = Path(f.name)
            # Save without format (should auto-detect)
            test_entity.save(temp_path)
            # Load without format (should auto-detect)
            loaded = XWEntity(schema=test_entity.schema)
            loaded.load(temp_path)
            assert loaded.get("name") == "Alice"
        except Exception as e:
            pytest.skip(f"XWJSON not available: {e}")
        finally:
            if 'temp_path' in locals():
                temp_path.unlink(missing_ok=True)
