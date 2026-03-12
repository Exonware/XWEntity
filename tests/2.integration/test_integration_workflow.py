#!/usr/bin/env python3
"""
#exonware/xwentity/tests/2.integration/test_integration_workflow.py
Integration tests for XWEntity complete workflows.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity, EntityState
from exonware.xwschema import XWSchema
from exonware.xwaction import XWAction
@pytest.mark.xwentity_integration

class TestIntegrationWorkflow:
    """Test complete entity workflows."""

    def test_complete_entity_lifecycle(self):
        """Test complete entity lifecycle."""
        # Create entity
        schema = XWSchema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        })
        entity = XWEntity(schema=schema, data={"name": "Alice", "age": 30})
        # Validate
        assert entity.validate() is True
        # State transitions
        entity.transition_to(EntityState.VALIDATED)
        assert entity._metadata.state == EntityState.VALIDATED
        entity.transition_to(EntityState.COMMITTED)
        assert entity._metadata.state == EntityState.COMMITTED
        # Add actions
        @XWAction(api_name="get_name")
        def get_name_action(obj: XWEntity) -> str:
            return obj.get("name")
        entity.register_action(get_name_action)
        assert entity.execute_action("get_name") == "Alice"
        # Modify data
        entity.set("age", 31)
        assert entity.get("age") == 31
        # Serialize and deserialize
        import tempfile
        from pathlib import Path
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        try:
            entity.save(temp_path)
            loaded = XWEntity(schema=schema)
            loaded.load(temp_path)
            assert loaded.get("name") == "Alice"
            assert loaded.get("age") == 31
        finally:
            temp_path.unlink(missing_ok=True)

    def test_entity_with_actions_and_validation(self):
        """Test entity with actions and validation."""
        schema = XWSchema({
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        })
        entity = XWEntity(schema=schema, data={"age": 30})
        @XWAction(
            api_name="update_age",
            in_types={"age": XWSchema({"type": "integer", "minimum": 0, "maximum": 150})}
        )
        def update_age_action(obj: XWEntity, age: int) -> dict:
            obj.set("age", age)
            return {"success": True, "age": age}
        entity.register_action(update_age_action)
        # Valid update
        result = entity.execute_action("update_age", age=25)
        assert result["success"] is True
        assert entity.get("age") == 25
        assert entity.validate() is True
        # Invalid update (should fail validation)
        with pytest.raises(Exception):
            entity.execute_action("update_age", age=200)

    def test_entity_optimization_workflow(self):
        """Test entity optimization workflow."""
        entity = XWEntity(data={f"key{i}": f"value{i}" for i in range(100)})
        # Get initial memory usage
        initial_memory = entity.get_memory_usage()
        # Optimize for access
        entity.optimize_for_access()
        access_memory = entity.get_memory_usage()
        # Optimize for memory
        entity.optimize_memory()
        memory_optimized = entity.get_memory_usage()
        # Get performance stats
        stats = entity.get_performance_stats()
        assert isinstance(stats, dict)
        # All should be valid
        assert initial_memory >= 0
        assert access_memory >= 0
        assert memory_optimized >= 0

    def test_entity_extension_workflow(self):
        """Test entity extension workflow."""
        entity = XWEntity(data={"name": "Alice"})
        # Register extensions
        entity.register_extension("cache", {"enabled": True})
        entity.register_extension("logger", {"level": "INFO"})
        # Use extensions
        cache = entity.get_extension("cache")
        assert cache["enabled"] is True
        # List extensions
        extensions = entity.list_extensions()
        assert "cache" in extensions
        assert "logger" in extensions
        # Remove extension
        entity.remove_extension("cache")
        assert entity.has_extension("cache") is False
        assert entity.has_extension("logger") is True
