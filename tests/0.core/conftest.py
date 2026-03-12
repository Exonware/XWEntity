#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/conftest.py
Core-specific test fixtures for xwentity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from typing import Any, Optional
from pathlib import Path


def _xwentity():
    from exonware.xwentity import XWEntity, XWEntityConfig
    return XWEntity, XWEntityConfig


def _xwschema():
    from exonware.xwschema import XWSchema
    return XWSchema


def _xwdata():
    from exonware.xwdata import XWData
    return XWData


def _xwaction():
    from exonware.xwaction import XWAction
    return XWAction


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    XWSchema = _xwschema()
    return XWSchema({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150},
            "email": {"type": "string", "format": "email"},
            "active": {"type": "boolean"}
        },
        "required": ["name"]
    })


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {"name": "Alice", "age": 30, "email": "alice@example.com", "active": True}


@pytest.fixture
def sample_entity(sample_schema, sample_data):
    """Create a sample XWEntity for testing."""
    XWEntity, _ = _xwentity()
    return XWEntity(schema=sample_schema, data=sample_data)


@pytest.fixture
def sample_object(sample_entity):
    """Alias for sample_entity - used in some tests."""
    return sample_entity


@pytest.fixture
def entity_with_actions(sample_entity):
    """Create entity with registered actions."""
    XWAction = _xwaction()
    XWEntity, _ = _xwentity()

    @XWAction(api_name="get_name")
    def get_name_action(obj) -> str:
        return obj.get("name")

    @XWAction(api_name="update_age")
    def update_age_action(obj, age: int) -> dict[str, Any]:
        obj.set("age", age)
        return {"success": True, "age": age}

    sample_entity.register_action(get_name_action)
    sample_entity.register_action(update_age_action)
    return sample_entity
