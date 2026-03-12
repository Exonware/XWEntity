#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_state_management.py
Core tests for XWEntity state management.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, EntityState
@pytest.mark.xwentity_core

class TestCoreStateManagement:
    """Test core state management functionality."""

    def test_initial_state(self, sample_entity):
        """Test that entity starts in DRAFT state."""
        assert sample_entity._metadata.state == EntityState.DRAFT

    def test_transition_to_validated(self, sample_entity):
        """Test transition to VALIDATED state."""
        sample_entity.transition_to(EntityState.VALIDATED)
        assert sample_entity._metadata.state == EntityState.VALIDATED

    def test_transition_to_committed(self, sample_entity):
        """Test transition to COMMITTED state."""
        sample_entity.transition_to(EntityState.VALIDATED)
        sample_entity.transition_to(EntityState.COMMITTED)
        assert sample_entity._metadata.state == EntityState.COMMITTED

    def test_transition_to_archived(self, sample_entity):
        """Test transition to ARCHIVED state."""
        sample_entity.transition_to(EntityState.VALIDATED)
        sample_entity.transition_to(EntityState.ARCHIVED)
        assert sample_entity._metadata.state == EntityState.ARCHIVED

    def test_can_transition_from_draft(self, sample_entity):
        """Test can_transition_to from DRAFT state."""
        assert sample_entity.can_transition_to(EntityState.VALIDATED) is True
        assert sample_entity.can_transition_to(EntityState.ARCHIVED) is True
        assert sample_entity.can_transition_to(EntityState.COMMITTED) is False

    def test_can_transition_from_validated(self, sample_entity):
        """Test can_transition_to from VALIDATED state."""
        sample_entity.transition_to(EntityState.VALIDATED)
        assert sample_entity.can_transition_to(EntityState.COMMITTED) is True
        assert sample_entity.can_transition_to(EntityState.DRAFT) is True
        assert sample_entity.can_transition_to(EntityState.ARCHIVED) is True

    def test_invalid_transition_raises_error(self, sample_entity):
        """Test that invalid transition raises error."""
        with pytest.raises(Exception):  # XWEntityStateError
            sample_entity.transition_to(EntityState.COMMITTED)  # Cannot go directly from DRAFT to COMMITTED

    def test_transition_to_active(self):
        """Test transition to ACTIVE state."""
        entity = XWEntity(data={})
        entity.transition_to(EntityState.ACTIVE)
        assert entity._metadata.state == EntityState.ACTIVE

    def test_transition_to_inactive(self):
        """Test transition to INACTIVE state."""
        entity = XWEntity(data={})
        entity.transition_to(EntityState.ACTIVE)
        entity.transition_to(EntityState.INACTIVE)
        assert entity._metadata.state == EntityState.INACTIVE

    def test_transition_to_deleted(self):
        """Test transition to DELETED state."""
        entity = XWEntity(data={})
        entity.transition_to(EntityState.ACTIVE)
        entity.transition_to(EntityState.DELETED)
        assert entity._metadata.state == EntityState.DELETED

    def test_deleted_is_terminal(self):
        """Test that DELETED is a terminal state."""
        entity = XWEntity(data={})
        entity.transition_to(EntityState.ACTIVE)
        entity.transition_to(EntityState.DELETED)
        # Cannot transition from DELETED
        assert entity.can_transition_to(EntityState.ACTIVE) is False

    def test_restore_from_archived(self, sample_entity):
        """Test restoring from ARCHIVED to DRAFT."""
        sample_entity.transition_to(EntityState.VALIDATED)
        sample_entity.transition_to(EntityState.ARCHIVED)
        sample_entity.transition_to(EntityState.DRAFT)
        assert sample_entity._metadata.state == EntityState.DRAFT
