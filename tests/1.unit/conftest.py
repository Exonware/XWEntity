#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/conftest.py
Unit-specific test fixtures for xwentity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest


def _xwentity():
    from exonware.xwentity import XWEntity, XWEntityConfig
    return XWEntity, XWEntityConfig


@pytest.fixture
def empty_entity():
    """Create an empty entity for unit tests."""
    XWEntity, _ = _xwentity()
    return XWEntity()


@pytest.fixture
def entity_with_config():
    """Create entity with custom config."""
    XWEntity, XWEntityConfig = _xwentity()
    config = XWEntityConfig(
        default_entity_type="test",
        auto_validate=False,
        strict_validation=False
    )
    return XWEntity(data={}, config=config)
