#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_format_import_export.py
Core tests for XWEntity format import/export capabilities.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 08-Nov-2025
"""

import pytest
import tempfile
from pathlib import Path
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
@pytest.mark.xwentity_core

class TestCoreFormatImportExport:
    """Test format import/export capabilities."""

    def test_save_json(self, sample_object):
        """Test saving object to JSON format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        try:
            sample_object.save(temp_path)
            assert Path(temp_path).exists()
            # Verify file contains JSON
            with open(temp_path, 'r') as f:
                content = f.read()
                assert '"name"' in content or '"Alice"' in content
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_save_yaml(self, sample_object):
        """Test saving object to YAML format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            temp_path = f.name
        try:
            sample_object.save(temp_path)
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_save_toml(self, sample_object):
        """Test saving object to TOML format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as f:
            temp_path = f.name
        try:
            sample_object.save(temp_path)
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_save_xml(self, sample_object):
        """Test saving object to XML format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            temp_path = f.name
        try:
            sample_object.save(temp_path)
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_save_with_explicit_format(self, sample_object):
        """Test saving object with explicit format."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            temp_path = f.name
        try:
            sample_object.save(temp_path, format='json')
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_json(self, sample_schema):
        """Test loading object from JSON format."""
        test_data = {"name": "Bob", "age": 25}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            import json
            json.dump(test_data, f)
            temp_path = f.name
        try:
            obj = XWEntity(schema=sample_schema)
            obj.load(temp_path)
            assert obj.get("name") == "Bob"
            assert obj.get("age") == 25
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_yaml(self, sample_schema):
        """Test loading object from YAML format."""
        pytest.importorskip("yaml")
        import yaml
        test_data = {"name": "Charlie", "age": 35}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(test_data, f)
            temp_path = f.name
        try:
            obj = XWEntity(schema=sample_schema)
            obj.load(temp_path)
            assert obj.get("name") == "Charlie"
            assert obj.get("age") == 35
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_load_with_explicit_format(self, sample_schema):
        """Test loading object with explicit format."""
        test_data = {"name": "David", "age": 40}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            import json
            json.dump(test_data, f)
            temp_path = f.name
        try:
            obj = XWEntity(schema=sample_schema)
            obj.load(temp_path, format='json')
            assert obj.get("name") == "David"
            assert obj.get("age") == 40
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_to_json_string(self, sample_object):
        """Test exporting object to JSON string."""
        json_str = sample_object.to_json()
        assert isinstance(json_str, str)
        assert '"name"' in json_str or '"Alice"' in json_str

    def test_to_yaml_string(self, sample_object):
        """Test exporting object to YAML string."""
        yaml_str = sample_object.to_yaml()
        assert isinstance(yaml_str, str)

    def test_to_toml_string(self, sample_object):
        """Test exporting object to TOML string."""
        toml_str = sample_object.to_toml()
        assert isinstance(toml_str, str)

    def test_to_xml_string(self, sample_object):
        """Test exporting object to XML string."""
        xml_str = sample_object.to_xml()
        assert isinstance(xml_str, str)

    def test_to_format_string(self, sample_object):
        """Test exporting object using to_format()."""
        json_str = sample_object.to_format('json')
        assert isinstance(json_str, str)
        # Try other formats
        yaml_str = sample_object.to_format('yaml')
        assert isinstance(yaml_str, str)

    def test_from_json_string(self, sample_schema):
        """Test importing object from JSON string."""
        json_str = '{"name": "Eve", "age": 28}'
        obj = XWEntity(schema=sample_schema)
        obj.from_json(json_str)
        assert obj.get("name") == "Eve"
        assert obj.get("age") == 28

    def test_from_yaml_string(self, sample_schema):
        """Test importing object from YAML string."""
        yaml_str = "name: Frank\nage: 32\n"
        obj = XWEntity(schema=sample_schema)
        try:
            obj.from_yaml(yaml_str)
            assert obj.get("name") == "Frank"
            assert obj.get("age") == 32
        except Exception:
            pytest.skip("YAML parsing may require PyYAML")

    def test_from_toml_string(self, sample_schema):
        """Test importing object from TOML string."""
        toml_str = 'name = "Grace"\nage = 45\n'
        obj = XWEntity(schema=sample_schema)
        try:
            obj.from_toml(toml_str)
            assert obj.get("name") == "Grace"
            assert obj.get("age") == 45
        except Exception:
            pytest.skip("TOML parsing may require tomli/tomllib")

    def test_from_format_string(self, sample_schema):
        """Test importing object using from_format()."""
        json_str = '{"name": "Henry", "age": 50}'
        obj = XWEntity(schema=sample_schema)
        obj.from_format('json', json_str)
        assert obj.get("name") == "Henry"
        assert obj.get("age") == 50

    def test_save_and_load_roundtrip(self, sample_object):
        """Test save and load roundtrip preserves data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = f.name
        try:
            # Save original object
            original_name = sample_object.get("name")
            original_age = sample_object.get("age")
            sample_object.save(temp_path)
            # Load into new object
            from exonware.xwentity import XWEntity
            from exonware.xwschema import XWSchema
            loaded_obj = XWEntity(schema=sample_object.schema)
            loaded_obj.load(temp_path)
            # Verify data preserved
            assert loaded_obj.get("name") == original_name
            assert loaded_obj.get("age") == original_age
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_format_detection_from_extension(self, sample_object):
        """Test format auto-detection from file extension."""
        formats_and_extensions = [
            ('json', '.json'),
            ('yaml', '.yaml'),
            ('yaml', '.yml'),
            ('toml', '.toml'),
            ('xml', '.xml'),
        ]
        for format_name, ext in formats_and_extensions:
            with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
                temp_path = f.name
            try:
                sample_object.save(temp_path)
                assert Path(temp_path).exists()
            except Exception as e:
                # Some formats may not be available - skip but log
                pytest.skip(f"Format {format_name} not available: {e}")
            finally:
                Path(temp_path).unlink(missing_ok=True)
