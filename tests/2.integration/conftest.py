#!/usr/bin/env python3
"""
#exonware/xwentity/tests/2.integration/conftest.py
Integration-specific test fixtures for xwentity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
@pytest.fixture

def complex_entity():
    """Create complex entity for integration tests."""
    schema = XWSchema({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "email": {"type": "string"},
            "tags": {"type": "array", "items": {"type": "string"}},
            "metadata": {
                "type": "object",
                "properties": {
                    "created": {"type": "string"},
                    "version": {"type": "integer"}
                }
            }
        },
        "required": ["name"]
    })
    return XWEntity(
        schema=schema,
        data={
            "name": "Alice",
            "age": 30,
            "email": "alice@example.com",
            "tags": ["developer", "python"],
            "metadata": {"created": "2026-01-28", "version": 1}
        }
    )
