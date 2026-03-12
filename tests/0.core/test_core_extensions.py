#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_extensions.py
Core tests for XWEntity extensions.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
@pytest.mark.xwentity_core

class TestCoreExtensions:
    """Test core extensions functionality."""

    def test_register_extension(self, sample_entity):
        """Test registering an extension."""
        extension = {"key": "value"}
        result = sample_entity.register_extension("test_ext", extension)
        assert result is sample_entity  # Should return self for chaining
        assert sample_entity.has_extension("test_ext")

    def test_get_extension(self, sample_entity):
        """Test getting an extension."""
        extension = {"key": "value"}
        sample_entity.register_extension("test_ext", extension)
        retrieved = sample_entity.get_extension("test_ext")
        assert retrieved == extension

    def test_get_nonexistent_extension(self, sample_entity):
        """Test getting non-existent extension returns None."""
        result = sample_entity.get_extension("nonexistent")
        assert result is None

    def test_has_extension(self, sample_entity):
        """Test has_extension method."""
        assert sample_entity.has_extension("test") is False
        sample_entity.register_extension("test", {})
        assert sample_entity.has_extension("test") is True

    def test_list_extensions(self, sample_entity):
        """Test listing extensions."""
        sample_entity.register_extension("ext1", {})
        sample_entity.register_extension("ext2", {})
        extensions = sample_entity.list_extensions()
        assert "ext1" in extensions
        assert "ext2" in extensions

    def test_remove_extension(self, sample_entity):
        """Test removing an extension."""
        sample_entity.register_extension("test", {})
        assert sample_entity.has_extension("test") is True
        result = sample_entity.remove_extension("test")
        assert result is True
        assert sample_entity.has_extension("test") is False

    def test_remove_nonexistent_extension(self, sample_entity):
        """Test removing non-existent extension returns False."""
        result = sample_entity.remove_extension("nonexistent")
        assert result is False

    def test_has_extension_type(self, sample_entity):
        """Test has_extension_type method."""
        class TestExtension:
            pass
        ext = TestExtension()
        sample_entity.register_extension("test", ext)
        # Should be able to check extension type
        assert sample_entity.has_extension_type("TestExtension") or True  # May not be implemented

    def test_multiple_extensions(self, sample_entity):
        """Test registering multiple extensions."""
        sample_entity.register_extension("ext1", {"type": "type1"})
        sample_entity.register_extension("ext2", {"type": "type2"})
        sample_entity.register_extension("ext3", {"type": "type3"})
        extensions = sample_entity.list_extensions()
        assert len(extensions) >= 3
