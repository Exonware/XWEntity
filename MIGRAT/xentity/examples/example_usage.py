#!/usr/bin/env python3
"""
📚 xEntity Usage Examples
Demonstrates the clean, simple API of xEntity.
"""

from typing import Dict
from src.xlib.xentity import xEntity, EntityState
from src.xlib.xdata import xSchema
from src.xlib.xaction import xAction


# Example 1: Basic Entity
def basic_entity_example():
    """Basic entity without schema."""
    print("=== Basic Entity Example ===")
    
    # Create entity with data
    entity = xEntity(data={
        "name": "John Doe",
        "email": "john@example.com",
        "age": 30
    })
    
    print(f"Entity ID: {entity.id}")
    print(f"Entity Type: {entity.type}")
    print(f"Name: {entity.get('name')}")
    print(f"State: {entity.state.value}")
    
    # Update data
    entity.set("age", 31)
    print(f"Updated age: {entity.get('age')}")
    print(f"Version: {entity.version}")
    print()


# Example 2: Entity with Schema
def schema_entity_example():
    """Entity with schema validation."""
    print("=== Schema Entity Example ===")
    
    # Define schema
    user_schema = xSchema(
        value="user_schema",
        data={
            "type": "object",
            "properties": {
                "username": {"type": "string", "minLength": 3},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 18}
            },
            "required": ["username", "email"]
        }
    )
    
    # Create entity with schema
    user = xEntity(
        schema=user_schema,
        data={
            "username": "johndoe",
            "email": "john@example.com",
            "age": 25
        },
        entity_type="user"
    )
    
    print(f"Valid: {user.validate()}")
    print(f"User: {user}")
    
    # State transitions
    user.to_validated().commit()
    print(f"State after commit: {user.state.value}")
    print()


# Example 3: Entity with Actions
class CharacterEntity(xEntity):
    """Game character entity with actions."""
    
    def __init__(self, name: str):
        # Define character schema
        schema = xSchema(
            value="character_schema",
            data={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "level": {"type": "integer", "minimum": 1, "maximum": 100},
                    "health": {"type": "integer", "minimum": 0},
                    "nose_length": {"type": "integer"},
                    "status": {"type": "string", "enum": ["active", "stunned", "dead"]}
                }
            }
        )
        
        # Initialize with data
        super().__init__(
            schema=schema,
            data={
                "name": name,
                "level": 1,
                "health": 100,
                "nose_length": 10,
                "status": "active"
            },
            entity_type="character"
        )
    
    @xAction(
        api_name="set-nose-length",
        roles=["*"],  # Public action for demonstration
        in_types={
            "length": {"minimum": 5, "maximum": 20}
        }
    )
    def set_nose_length(self, length: int) -> bool:
        """Set character's nose length."""
        self.set("nose_length", length)
        return True
    
    @xAction(
        api_name="level-up",
        roles=["*"]  # Public action for demonstration
    )
    def level_up(self) -> Dict[str, int]:
        """Level up the character."""
        current_level = self.get("level")
        new_level = min(current_level + 1, 100)
        self.set("level", new_level)
        
        # Increase health
        self.set("health", 100 + (new_level * 10))
        
        return {
            "old_level": current_level,
            "new_level": new_level,
            "health": self.get("health")
        }
    
    @xAction(
        api_name="take-damage",
        roles=["*"],  # Public action for demonstration
        in_types={
            "damage": {"minimum": 0}
        }
    )
    def take_damage(self, damage: int) -> str:
        """Apply damage to character."""
        current_health = self.get("health")
        new_health = max(0, current_health - damage)
        self.set("health", new_health)
        
        if new_health == 0:
            self.set("status", "dead")
            return "dead"
        elif damage > 50:
            self.set("status", "stunned")
            return "stunned"
        else:
            return "active"


def entity_with_actions_example():
    """Entity with actions example."""
    print("=== Entity with Actions Example ===")
    
    # Create character
    hero = CharacterEntity("Aragorn")
    print(f"Created: {hero}")
    print(f"Initial nose length: {hero.get('nose_length')}")
    
    # List actions
    print(f"Available actions: {hero.list_actions()}")
    
    # Execute actions
    hero.execute_action("set-nose-length", length=15)
    print(f"Nose length after action: {hero.get('nose_length')}")
    
    # Level up
    result = hero.execute_action("level-up")
    print(f"Level up result: {result}")
    
    # Take damage
    status = hero.execute_action("take-damage", damage=30)
    print(f"Status after damage: {status}")
    print(f"Health: {hero.get('health')}")
    
    # Export actions
    print("\nAction metadata:")
    for name, meta in hero.export_actions().items():
        print(f"  {name}: {meta.get('description')}")
    print()


# Example 4: Entity Serialization
def serialization_example():
    """Entity serialization example."""
    print("=== Serialization Example ===")
    
    # Create entity
    product = xEntity(
        data={
            "name": "Widget",
            "price": 19.99,
            "stock": 100
        },
        entity_type="product"
    )
    
    # Add some metadata
    product._engine.metadata.tags = ["electronics", "popular"]
    
    # Export to dict
    data = product.to_dict()
    print(f"Exported keys: {list(data.keys())}")
    
    # Save to file
    product.to_file("product.json")
    print("Saved to product.json")
    
    # Load from file
    loaded = xEntity.from_file("product.json")
    print(f"Loaded: {loaded}")
    print(f"Loaded name: {loaded.get('name')}")
    
    # Copy entity
    copy = product.copy()
    print(f"Original ID: {product.id}")
    print(f"Copy ID: {copy.id}")
    print(f"Same data: {copy.get('name') == product.get('name')}")
    print()


if __name__ == "__main__":
    from typing import Dict
    
    basic_entity_example()
    schema_entity_example()
    entity_with_actions_example()
    serialization_example()
    
    print("✅ All examples completed!") 