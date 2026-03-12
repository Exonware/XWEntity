#!/usr/bin/env python3
"""
#exonware/xwentity/tests/conftest.py
Shared test fixtures and configuration for xwentity tests.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 08-Nov-2025
"""

import pytest
from typing import Any, Optional


@pytest.fixture(autouse=True)
def clear_entity_cache_between_tests():
    """Clear global entity cache before each test to prevent cross-test pollution."""
    try:
        from exonware.xwentity.base import clear_entity_cache as _clear
        _clear()
    except Exception:
        pass
    yield

# Lazy imports: avoid pulling xwsystem heavy optional deps until fixtures are used.
# If ImportError occurs when a fixture runs, install the missing dep (e.g. msgspec)
# or use pip install -e ".[full]" for full xwsystem optional deps.


def _import_xwentity():
    from exonware.xwentity import XWEntity
    return XWEntity


def _import_xwschema():
    from exonware.xwschema import XWSchema
    return XWSchema


def _import_xwdata():
    from exonware.xwdata import XWData
    return XWData


def _import_xwaction():
    from exonware.xwaction import XWAction
    return XWAction


@pytest.fixture
def sample_schema():
    """Create a sample schema for testing."""
    XWSchema = _import_xwschema()
    return XWSchema({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer", "minimum": 0, "maximum": 150}
        },
        "required": ["name"]
    })


@pytest.fixture
def sample_data():
    """Create sample data for testing."""
    return {"name": "Alice", "age": 30}


@pytest.fixture
def sample_xwdata(sample_data):
    """Create sample XWData for testing."""
    XWData = _import_xwdata()
    return XWData.from_native(sample_data)


@pytest.fixture
def sample_entity(sample_schema, sample_xwdata):
    """Create a sample XWEntity for testing."""
    XWEntity = _import_xwentity()
    return XWEntity(schema=sample_schema, data=sample_xwdata)


@pytest.fixture
def sample_action():
    """Create a sample XWAction for testing."""
    XWAction = _import_xwaction()
    XWEntity = _import_xwentity()

    @XWAction(api_name="get_name", profile="query")
    def get_name_action(obj) -> str:
        """Get name from object data."""
        return obj.get("name")
    return get_name_action


@pytest.fixture
def action_with_schema():
    """Create an action with input/output schema validation."""
    XWSchema = _import_xwschema()
    XWAction = _import_xwaction()
    XWEntity = _import_xwentity()

    @XWAction(
        api_name="update_age",
        profile="command",
        in_types={
            "age": XWSchema({"type": "integer", "minimum": 0, "maximum": 150})
        },
        out_types={
            "result": XWSchema({"type": "object", "properties": {"success": {"type": "boolean"}}})
        }
    )
    def update_age_action(obj, age: int) -> dict[str, Any]:
        """Update age with validation."""
        obj.set("age", age)
        return {"success": True}
    return update_age_action
