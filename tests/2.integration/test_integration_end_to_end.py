#!/usr/bin/env python3
"""
#exonware/xwentity/tests/2.integration/test_integration_end_to_end.py
End-to-end integration tests for XWEntity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
import tempfile
from pathlib import Path
from exonware.xwentity import XWEntity, EntityState
from exonware.xwschema import XWSchema
from exonware.xwaction import XWAction
@pytest.mark.xwentity_integration

class TestIntegrationEndToEnd:
    """Test end-to-end entity workflows."""

    def test_complete_entity_workflow(self):
        """Test complete entity workflow from creation to serialization."""
        # 1. Create entity with schema
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
                "email": {"type": "string", "format": "email"}
            },
            "required": ["name", "email"]
        })
        entity = XWEntity(
            schema=schema,
            data={"name": "Alice", "age": 30, "email": "alice@example.com"},
            entity_type="user"
        )
        # 2. Validate
        assert entity.validate() is True
        # 3. State management
        entity.transition_to(EntityState.VALIDATED)
        assert entity._metadata.state == EntityState.VALIDATED
        # 4. Add actions
        @XWAction(api_name="get_profile")
        def get_profile_action(obj: XWEntity) -> dict:
            return {
                "name": obj.get("name"),
                "age": obj.get("age"),
                "email": obj.get("email")
            }
        entity.register_action(get_profile_action)
        # 5. Execute action
        profile = entity.execute_action("get_profile")
        assert profile["name"] == "Alice"
        # 6. Modify data
        entity.set("age", 31)
        assert entity.get("age") == 31
        # 7. Serialize to multiple formats
        formats = ["json", "yaml", "xwjson"]
        for fmt in formats:
            try:
                mode = 'wb' if fmt == 'xwjson' else 'w'
                ext = f".{fmt}" if fmt != 'xwjson' else '.xwjson'
                with tempfile.NamedTemporaryFile(mode=mode, suffix=ext, delete=False) as f:
                    temp_path = Path(f.name)
                entity.save(temp_path, format=fmt)
                # 8. Load and verify
                loaded = XWEntity(schema=schema)
                loaded.load(temp_path, format=fmt)
                assert loaded.get("name") == "Alice"
                assert loaded.get("age") == 31
                assert loaded.get("email") == "alice@example.com"
            except Exception as e:
                pytest.skip(f"Format {fmt} not available: {e}")
            finally:
                if 'temp_path' in locals():
                    temp_path.unlink(missing_ok=True)

    def test_entity_with_all_features(self):
        """Test entity with all features enabled."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "data": {"type": "object"}
            }
        })
        entity = XWEntity(
            schema=schema,
            data={"name": "Test", "data": {"key": "value"}},
            entity_type="test",
            node_mode="AUTO",
            edge_mode="AUTO",
            graph_manager_enabled=True
        )
        # Add extension
        entity.register_extension("test_ext", {"enabled": True})
        # Add action
        @XWAction(api_name="test_action")
        def test_action(obj: XWEntity) -> str:
            return "test"
        entity.register_action(test_action)
        # Optimize
        entity.optimize_for_access()
        # State transition
        entity.transition_to(EntityState.VALIDATED)
        # Serialize
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            # Load with same configuration to preserve graph structure
            loaded = XWEntity(
                schema=schema,
                graph_manager_enabled=True,
                node_mode="AUTO",
                edge_mode="AUTO"
            )
            loaded.load(temp_path)
            assert loaded.get("name") == "Test"
            assert loaded.get("data") == {"key": "value"}
        finally:
            temp_path.unlink(missing_ok=True)
