#!/usr/bin/env python3
"""
#exonware/xwentity/tests/1.unit/test_entity.py

Unit Tests for Entity Components

This module tests IEntity, AEntity, and XWEntity components.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.1
Generation Date: 08-Nov-2025
"""

import pytest
from datetime import datetime

from exonware.xwentity import (
    XWEntity,
    AEntity,
    IEntity,
    EntityState,
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityConfig,
)


class TestIEntity:
    """Tests for IEntity interface."""
    
    def test_interface_is_abstract(self):
        """Test that IEntity is an abstract class."""
        with pytest.raises(TypeError):
            IEntity()


class TestAEntity:
    """Tests for AEntity abstract class."""
    
    def test_abstract_class_cannot_be_instantiated(self):
        """Test that AEntity cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AEntity()


class TestXWEntity:
    """Tests for XWEntity concrete class."""
    
    def test_create_entity_with_dict_data(self):
        """Test creating entity with dictionary data."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        assert entity is not None
        assert entity.type == "entity"
        assert entity.state == EntityState.DRAFT
    
    def test_entity_has_id(self):
        """Test that entity has an ID."""
        entity = XWEntity(data={})
        assert entity.id is not None
        assert isinstance(entity.id, str)
        assert len(entity.id) > 0
    
    def test_entity_has_timestamps(self):
        """Test that entity has creation and update timestamps."""
        entity = XWEntity(data={})
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert isinstance(entity.created_at, datetime)
        assert isinstance(entity.updated_at, datetime)
    
    def test_get_data(self):
        """Test getting data from entity."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        name = entity.get("name")
        assert name == "Alice"
        age = entity.get("age")
        assert age == 30
    
    def test_set_data(self):
        """Test setting data in entity."""
        entity = XWEntity(data={"name": "Alice"})
        entity.set("age", 30)
        age = entity.get("age")
        assert age == 30
    
    def test_delete_data(self):
        """Test deleting data from entity."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.delete("age")
        age = entity.get("age")
        assert age is None
    
    def test_update_data(self):
        """Test updating multiple values."""
        entity = XWEntity(data={"name": "Alice", "age": 30})
        entity.update({"age": 31, "city": "New York"})
        assert entity.get("age") == 31
        assert entity.get("city") == "New York"
    
    def test_entity_version_increments(self):
        """Test that entity version increments on updates."""
        entity = XWEntity(data={})
        initial_version = entity.version
        entity.set("test", "value")
        assert entity.version > initial_version
    
    def test_state_transitions(self):
        """Test entity state transitions."""
        entity = XWEntity(data={})
        assert entity.state == EntityState.DRAFT
        
        # Transition to validated
        entity.transition_to(EntityState.VALIDATED)
        assert entity.state == EntityState.VALIDATED
        
        # Transition to committed
        entity.transition_to(EntityState.COMMITTED)
        assert entity.state == EntityState.COMMITTED
    
    def test_invalid_state_transition(self):
        """Test that invalid state transitions raise error."""
        entity = XWEntity(data={})
        entity.transition_to(EntityState.COMMITTED)
        
        # Cannot go back to draft from committed
        with pytest.raises(XWEntityStateError):
            entity.transition_to(EntityState.DRAFT)
    
    def test_can_transition_to(self):
        """Test checking if state transition is allowed."""
        entity = XWEntity(data={})
        assert entity.can_transition_to(EntityState.VALIDATED) is True
        assert entity.can_transition_to(EntityState.ARCHIVED) is True
        assert entity.can_transition_to(EntityState.COMMITTED) is False
    
    def test_register_action(self):
        """Test registering an action."""
        entity = XWEntity(data={})
        
        # Create a simple action-like object
        class SimpleAction:
            def __init__(self):
                self.api_name = "test_action"
        
        action = SimpleAction()
        entity.register_action(action)
        
        actions = entity.list_actions()
        assert "test_action" in actions
    
    def test_execute_action_not_found(self):
        """Test executing non-existent action raises error."""
        entity = XWEntity(data={})
        with pytest.raises(XWEntityActionError):
            entity.execute_action("nonexistent_action")
    
    def test_to_dict(self):
        """Test converting entity to dictionary."""
        entity = XWEntity(data={"name": "Alice"})
        data_dict = entity.to_dict()
        
        assert isinstance(data_dict, dict)
        assert "_metadata" in data_dict
        assert "_data" in data_dict
    
    def test_from_dict(self):
        """Test creating entity from dictionary."""
        entity = XWEntity(data={"name": "Alice"})
        data_dict = entity.to_dict()
        
        new_entity = XWEntity.from_dict(data_dict["_data"])
        assert new_entity is not None
    
    def test_entity_with_config(self):
        """Test creating entity with custom configuration."""
        config = XWEntityConfig(
            default_entity_type="user",
            node_mode="HASH_MAP",
            graph_manager_enabled=False,
        )
        entity = XWEntity(data={}, config=config)
        assert entity.type == "user"
    
    def test_entity_with_node_config(self):
        """Test creating entity with node configuration."""
        entity = XWEntity(
            data={"name": "Alice"},
            node_mode="HASH_MAP",
            edge_mode="AUTO",
            graph_manager_enabled=False,
        )
        assert entity is not None
        assert entity.get("name") == "Alice"
    
    def test_entity_validation_without_schema(self):
        """Test entity validation without schema (should pass)."""
        entity = XWEntity(data={"name": "Alice"})
        assert entity.validate() is True
    
    def test_entity_actions_list(self):
        """Test listing entity actions."""
        entity = XWEntity(data={})
        actions = entity.list_actions()
        assert isinstance(actions, list)
    
    def test_entity_performance_stats(self):
        """Test getting performance statistics."""
        entity = XWEntity(data={"name": "Alice"})
        entity.get("name")
        entity.get("nonexistent")
        
        stats = entity.get_performance_stats()
        assert isinstance(stats, dict)
        assert "access_count" in stats
        assert stats["access_count"] > 0
