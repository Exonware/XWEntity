#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/errors_tests/test_errors.py
Unit tests for XWEntity error classes.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityDataError,
    XWEntityNotFoundError,
)
@pytest.mark.xwentity_unit

class TestErrors:
    """Test error classes."""

    def test_xwentity_error(self):
        """Test XWEntityError can be raised."""
        with pytest.raises(XWEntityError):
            raise XWEntityError("Test error")

    def test_xwentity_error_with_cause(self):
        """Test XWEntityError with cause."""
        cause = ValueError("Original error")
        try:
            raise XWEntityError("Wrapper error", cause=cause)
        except XWEntityError as e:
            assert e.cause == cause

    def test_xwentity_validation_error(self):
        """Test XWEntityValidationError."""
        with pytest.raises(XWEntityValidationError):
            raise XWEntityValidationError("Validation failed")

    def test_xwentity_state_error(self):
        """Test XWEntityStateError."""
        with pytest.raises(XWEntityStateError):
            raise XWEntityStateError("Invalid state transition")

    def test_xwentity_action_error(self):
        """Test XWEntityActionError."""
        with pytest.raises(XWEntityActionError):
            raise XWEntityActionError("Action failed", action_name="test_action")

    def test_xwentity_data_error(self):
        """Test XWEntityDataError."""
        with pytest.raises(XWEntityDataError):
            raise XWEntityDataError("Data operation failed")

    def test_xwentity_not_found_error(self):
        """Test XWEntityNotFoundError."""
        with pytest.raises(XWEntityNotFoundError):
            raise XWEntityNotFoundError("Entity not found", entity_id="test-id")

    def test_error_inheritance(self):
        """Test error class inheritance."""
        assert issubclass(XWEntityValidationError, XWEntityError)
        assert issubclass(XWEntityStateError, XWEntityError)
        assert issubclass(XWEntityActionError, XWEntityError)
        assert issubclass(XWEntityDataError, XWEntityError)
        assert issubclass(XWEntityNotFoundError, XWEntityError)
