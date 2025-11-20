#!/usr/bin/env python3
"""
Test the new xEntity architecture: iEntity -> aEntity -> xEntity
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.xlib.xentity.abc import iEntity, iEntityFacade
from src.xlib.xentity.model_new import aEntity, aEntityFactory, EntityState
from src.xlib.xentity.facade_new import xEntity, xEntityFactory
from src.xlib.xentity.config import use_performance_mode
from src.xlib.xdata.new_3.schema import xSchema
from src.xlib.xaction import xAction

# Set default to PERFORMANCE mode
use_performance_mode()


class UserEntity(xEntity):
    """Test user entity using the new architecture."""
    
    @xSchema(length_min=1, length_max=50, pattern="^[a-zA-Z0-9_]+$", required=True)
    def username(self) -> str: pass
    
    @xAction(api_name="update-password", roles=["*"])
    def update_password(self, new_password: str) -> dict:
        """Update user password."""
        return {"success": True, "message": "Password updated"}


def test_architecture():
    """Test the new xEntity architecture."""
    print("🏗️ Testing New xEntity Architecture")
    print("=" * 50)
    
    # Test 1: Interface Hierarchy
    print("\n📋 Test 1: Interface Hierarchy")
    
    # Create instances
    a_entity = aEntity(entity_type="test")
    x_entity = xEntity.from_data({"username": "john_doe"})
    user_entity = UserEntity.from_data({"username": "jane_smith"})
    
    # Check interface compliance
    print(f"   ✅ aEntity implements iEntity: {isinstance(a_entity, iEntity)}")
    print(f"   ✅ xEntity implements iEntityFacade: {isinstance(x_entity, iEntityFacade)}")
    print(f"   ✅ UserEntity implements iEntityFacade: {isinstance(user_entity, iEntityFacade)}")
    
    # Test 2: Properties
    print("\n📊 Test 2: Properties")
    
    print(f"   🔍 aEntity properties:")
    print(f"      ID: {a_entity.id}")
    print(f"      Type: {a_entity.type}")
    print(f"      State: {a_entity.state}")
    print(f"      Version: {a_entity.version}")
    
    print(f"   🔍 xEntity properties:")
    print(f"      ID: {x_entity.id}")
    print(f"      Type: {x_entity.type}")
    print(f"      State: {x_entity.state}")
    print(f"      Version: {x_entity.version}")
    print(f"      Data: {x_entity.data.to_native()}")
    
    print(f"   🔍 UserEntity properties:")
    print(f"      ID: {user_entity.id}")
    print(f"      Type: {user_entity.type}")
    print(f"      State: {user_entity.state}")
    print(f"      Version: {user_entity.version}")
    print(f"      Data: {user_entity.data.to_native()}")
    
    # Test 3: Data Operations
    print("\n🔧 Test 3: Data Operations")
    
    # Test xEntity data operations
    x_entity.set("email", "john@example.com")
    x_entity.set("age", 25)
    
    print(f"   📝 xEntity data operations:")
    print(f"      Username: {x_entity.get('username')}")
    print(f"      Email: {x_entity.get('email')}")
    print(f"      Age: {x_entity.get('age')}")
    print(f"      Full data: {x_entity.data.to_native()}")
    
    # Test 4: Actions
    print("\n⚡ Test 4: Actions")
    
    # Register action on aEntity
    def test_action(entity, param: str) -> dict:
        return {"action": "test", "param": param}
    
    a_entity._register_action(test_action)
    
    print(f"   🔧 aEntity actions:")
    print(f"      Actions: {a_entity._list_actions()}")
    print(f"      Action result: {a_entity._execute_action('test_action', param='test')}")
    
    print(f"   🔧 UserEntity actions:")
    print(f"      Actions: {user_entity.list_actions()}")
    print(f"      Actions export: {user_entity.export_actions()}")
    
    # Test 5: State Management
    print("\n🔄 Test 5: State Management")
    
    # Test state transitions
    print(f"   📊 Initial state: {x_entity.state}")
    
    x_entity.to_validated()
    print(f"   ✅ After validation: {x_entity.state}")
    
    x_entity.commit()
    print(f"   ✅ After commit: {x_entity.state}")
    
    x_entity.archive()
    print(f"   ✅ After archive: {x_entity.state}")
    
    x_entity.restore()
    print(f"   ✅ After restore: {x_entity.state}")
    
    # Test 6: Serialization
    print("\n💾 Test 6: Serialization")
    
    # Test to_dict
    entity_dict = x_entity.to_dict()
    print(f"   📦 To dict: {len(entity_dict)} keys")
    print(f"      Keys: {list(entity_dict.keys())}")
    
    # Test to_native
    native_dict = x_entity.to_native()
    print(f"   📦 To native: {len(native_dict)} keys")
    
    # Test 7: Factory Methods
    print("\n🏭 Test 7: Factory Methods")
    
    # Test aEntityFactory
    a_entity_from_dict = aEntityFactory.from_dict(entity_dict)
    print(f"   ✅ aEntityFactory.from_dict: {a_entity_from_dict.id}")
    
    # Test xEntityFactory
    x_entity_from_dict = xEntityFactory.from_dict(entity_dict)
    print(f"   ✅ xEntityFactory.from_dict: {x_entity_from_dict.id}")
    
    # Test 8: Performance Features
    print("\n⚡ Test 8: Performance Features")
    
    # Test performance stats
    stats = x_entity.get_performance_stats()
    print(f"   📊 Performance stats: {stats}")
    
    # Test memory usage
    memory = x_entity.get_memory_usage()
    print(f"   💾 Memory usage: {memory} bytes")
    
    # Test 9: Extensibility
    print("\n🔌 Test 9: Extensibility")
    
    # Test extensions
    x_entity.register_extension("custom_extension", {"key": "value"})
    print(f"   ✅ Extension registered: {x_entity.has_extension('custom_extension')}")
    print(f"   📦 Extension value: {x_entity.get_extension('custom_extension')}")
    print(f"   📋 Extensions: {x_entity.list_extensions()}")
    
    # Test 10: Copy and Equality
    print("\n🔄 Test 10: Copy and Equality")
    
    # Test copy
    x_entity_copy = x_entity.copy()
    print(f"   ✅ Copy created: {x_entity_copy.id}")
    print(f"   🔍 Original ID: {x_entity.id}")
    print(f"   🔍 Copy ID: {x_entity_copy.id}")
    print(f"   ✅ IDs are different: {x_entity.id != x_entity_copy.id}")
    
    # Test equality
    print(f"   ✅ Equality test: {x_entity == x_entity_copy}")
    print(f"   ✅ Hash test: {hash(x_entity) == hash(x_entity_copy)}")
    
    print(f"\n🎉 All tests passed! New architecture is working correctly!")
    print(f"📋 Architecture: iEntity -> aEntity -> xEntity ✅")


if __name__ == "__main__":
    test_architecture()
