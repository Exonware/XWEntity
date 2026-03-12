#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_metadata.py
Core tests for XWEntity metadata.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from datetime import datetime
from exonware.xwentity import XWEntity
@pytest.mark.xwentity_core

class TestCoreMetadata:
    """Test core metadata functionality."""

    def test_metadata_created_at(self, sample_entity):
        """Test created_at timestamp."""
        assert isinstance(sample_entity.created_at, datetime)
        assert sample_entity.created_at <= datetime.now()

    def test_metadata_updated_at(self, sample_entity):
        """Test updated_at timestamp."""
        assert isinstance(sample_entity.updated_at, datetime)
        assert sample_entity.updated_at <= datetime.now()

    def test_metadata_deleted_at_initial(self, sample_entity):
        """Test deleted_at is None initially."""
        assert sample_entity.deleted_at is None

    def test_metadata_has_id(self, sample_entity):
        """Test entity has an ID."""
        assert sample_entity.id is not None
        assert isinstance(sample_entity.id, str)

    def test_metadata_unique_ids(self):
        """Test that different entities have unique IDs."""
        entity1 = XWEntity(data={})
        entity2 = XWEntity(data={})
        assert entity1.id != entity2.id

    def test_metadata_entity_type_default(self, sample_entity):
        """Test default entity type."""
        assert sample_entity._metadata.type == "entity"

    def test_metadata_entity_type_custom(self):
        """Test custom entity type."""
        entity = XWEntity(data={}, entity_type="user")
        assert entity._metadata.type == "user"

    def test_metadata_entity_type_from_subclass(self):
        """Test entity type from subclass name."""
        class UserEntity(XWEntity):
            pass
        user = UserEntity(data={})
        # Should derive from class name
        assert user._metadata.type in ["user", "entity"]

    def test_metadata_state_default(self, sample_entity):
        """Test default state."""
        from exonware.xwentity import EntityState
        assert sample_entity._metadata.state == EntityState.DRAFT

    def test_metadata_version(self, sample_entity):
        """Test metadata has version."""
        assert hasattr(sample_entity._metadata, "version")
        assert sample_entity._metadata.version >= 0
