#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/base_tests/test_base_entity.py
Unit tests for AEntity base class.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import AEntity, XWEntity, XWEntityMetadata, EntityState
@pytest.mark.xwentity_unit

class TestBaseEntity:
    """Test AEntity base class."""

    def test_entity_metadata_creation(self):
        """Test XWEntityMetadata creation: both id and uid present; uid auto-generated."""
        metadata = XWEntityMetadata("user")
        assert metadata.type == "user"  # Use 'type' property, not 'entity_type'
        assert metadata.state == EntityState.DRAFT
        assert metadata.uid is not None
        assert metadata.uid != ""
        # id is user-set (may be "" until set); uid is always present and distinct
        assert metadata.id is not None  # may be ""
        assert metadata.to_dict().get("id") is not None
        assert metadata.to_dict().get("uid") is not None

    def test_entity_metadata_timestamps(self):
        """Test metadata timestamps."""
        metadata = XWEntityMetadata("user")
        assert metadata.created_at is not None
        assert metadata.updated_at is not None
        assert metadata.deleted_at is None

    def test_entity_metadata_version(self):
        """Test metadata version."""
        metadata = XWEntityMetadata("user")
        assert metadata.version >= 0

    def test_entity_inherits_from_base(self):
        """Test XWEntity inherits from AEntity."""
        entity = XWEntity(data={})
        assert isinstance(entity, AEntity)

    def test_entity_has_metadata(self):
        """Test entity has metadata."""
        entity = XWEntity(data={})
        assert hasattr(entity, "_metadata")
        assert isinstance(entity._metadata, XWEntityMetadata)

    def test_entity_metadata_properties(self):
        """Test entity metadata properties."""
        entity = XWEntity(data={})
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.deleted_at is None
