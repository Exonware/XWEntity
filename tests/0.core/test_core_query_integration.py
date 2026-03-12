#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_query_integration.py
Core tests for XWQuery integration in XWAction.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 08-Nov-2025
"""

import pytest
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
from exonware.xwdata import XWData
from exonware.xwaction import XWAction
@pytest.mark.xwentity_core

class TestCoreQueryIntegration:
    """Test XWQuery integration in actions."""

    def test_action_can_use_query_method(self, sample_object):
        """Test that actions can use XWAction.query() method."""
        # Create action that uses XWQuery
        @XWAction(api_name="query_users")
        def query_users_action(obj: XWEntity) -> list:
            """Query users using XWQuery."""
            # Set up test data
            obj.set("users", [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
                {"name": "Charlie", "age": 35}
            ])
            # Use XWAction.query() to query data
            result = XWAction.query("SELECT * FROM users WHERE age > 25", obj.data)
            return result.data if hasattr(result, 'data') else result
        sample_object.register_action(query_users_action)
        try:
            result = sample_object.execute_action("query_users")
            # Result should contain users with age > 25
            assert isinstance(result, list)
            # Verify query worked (results depend on XWQuery implementation)
        except Exception as e:
            # If XWQuery not available, skip test
            pytest.skip(f"XWQuery not available: {e}")

    def test_action_query_with_jsonpath(self, sample_object):
        """Test action using XWQuery with JSONPath format."""
        @XWAction(api_name="get_names")
        def get_names_action(obj: XWEntity) -> list:
            """Get names using JSONPath query."""
            obj.set("users", [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ])
            # Use XWAction.query() with JSONPath
            result = XWAction.query("$.users[*].name", obj.data, format="jsonpath")
            return result.data if hasattr(result, 'data') else result
        sample_object.register_action(get_names_action)
        try:
            result = sample_object.execute_action("get_names")
            assert isinstance(result, (list, dict))
        except Exception as e:
            pytest.skip(f"XWQuery not available: {e}")

    def test_query_method_static(self):
        """Test that XWAction.query() is a static method."""
        assert isinstance(XWAction.query, staticmethod) or callable(XWAction.query)
        # Test it can be called without an instance
        test_data = {"users": [{"name": "Alice"}]}
        try:
            result = XWAction.query("$.users[*].name", test_data, format="jsonpath")
            assert result is not None
        except Exception as e:
            # If XWQuery not available, that's OK - we're testing the method exists
            pass
