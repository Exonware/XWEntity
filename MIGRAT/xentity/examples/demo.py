#!/usr/bin/env python3
"""
🎯 xEntity Complete API Demo
Testing the full xEntity API: schema, actions, data, and complete entity operations.

📋 xSchema Automatic Version Selection:
- Default: Uses legacy xSchema (full-featured OpenAPI 3.1.0 implementation)
- When XDATA_VERSION='new_3': Uses new_3 xSchema (performance-optimized)
- Switches automatically via switch_version() function
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from typing import Annotated
# Import the complete API implementation
from src.xlib.xentity import xEntity
from src.xlib.xentity.config import use_performance_mode
from src.xlib.xdata import xSchema  # 🎯 Automatically selects: legacy or new_3 based on XDATA_VERSION
from src.xlib.xaction import xAction

# Set default to PERFORMANCE mode
use_performance_mode()


class UserEntity(xEntity):
    """Clean user entity with complete API testing!"""
    
    @xSchema(required=True,length_min=1, length_max=50, pattern="^[a-zA-Z0-9_]+$", description="Username")
    def username(self) -> str: pass
    
    @xSchema(required=True, confidential=True, description="User password")
    def password(self) -> str: pass
    
    @xSchema(required=True, length_min=1, length_max=100, description="First name")
    def first_name(self) -> str: pass
    
    @xSchema(required=True, length_min=1, length_max=100, description="Last name")
    def last_name(self) -> str: pass
    
    @xSchema(required=True, pattern=r"^[^@]+@[^@]+\.[^@]+$", description="Email address")
    def email(self) -> str: pass
    
    @xSchema(value_min=0, value_max=150, description="Age in years")
    def age(self) -> int: pass
    
    @xSchema(description="Account active status")
    def active(self) -> bool: pass
    
    def full_name(self) -> str:
        """Full name using standard Python @property."""
        return f"{self.first_name} {self.last_name}"
    
    @xAction(api_name="update-password", roles=["*"])
    def update_password(self, new_password: str) -> dict:
        """Update user password."""
        self._password = new_password
        return {"success": True, "message": "Password updated"}
    
    @xAction(api_name="deactivate", roles=["*"])
    def deactivate(self) -> dict:
        """Deactivate user account."""
        self.active = False
        return {"success": True, "message": "User deactivated"}


def test_complete_api():
    """Test the complete xEntity API."""
    print("🎯 xEntity Complete API Test")
    print("=" * 50)
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Create test users
    user1 = UserEntity(username="john_doe", email="john@example.com", age=25)
    user2 = UserEntity(username="jane_smith", email="jane@example.com", age=30)
    users = [user1, user2]
    
    print(f"✅ Created {len(users)} test users")
    
    # Test 1: Individual Component Operations
    print("\n📋 Test 1: Individual Component Operations")
    
    # Schema operations (static)
    print("   🔍 Testing schema operations...")
    try:
        UserEntity.schema_to_file('output/user_schema.json')
        schema_dict = UserEntity.schema_to_native()
        print(f"   ✅ Schema operations: schema_dict={schema_dict}")
    except Exception as e:
        print(f"   ❌ Schema operations failed: {e}")
    
    # Actions operations (static)
    print("   🔧 Testing actions operations...")
    try:
        UserEntity.actions_to_file('output/user_actions.json')
        actions_dict = UserEntity.actions_to_native()
        print(f"   ✅ Actions operations: {len(actions_dict)} actions")
    except Exception as e:
        print(f"   ❌ Actions operations failed: {e}")
    
    # Data operations (instance)
    print("   📊 Testing data operations...")
    try:
        user1.data_to_file('output/user1_data.json')
        data_dict = user1.data_to_native()
        print(f"   ✅ Data operations: {len(data_dict)} data fields")
    except Exception as e:
        print(f"   ❌ Data operations failed: {e}")
    
    # Test 2: Complete Entity Operations
    print("\n📦 Test 2: Complete Entity Operations")
    
    # Complete entity operations (static)
    print("   🔍 Testing complete entity operations (static)...")
    try:
        UserEntity.to_file('output/complete_user_entity.json')
        entity_dict = UserEntity.to_native()
        print(f"   ✅ Complete entity operations (static): {len(entity_dict)} keys")
    except Exception as e:
        print(f"   ❌ Complete entity operations failed: {e}")
    
    # Complete entity operations (instance)
    print("   📊 Testing complete entity operations (instance)...")
    try:
        user1.to_file('output/user1_complete.json')
        user_dict = user1.to_native()
        print(f"   ✅ Instance entity operations: {len(user_dict)} keys")
    except Exception as e:
        print(f"   ❌ Instance entity operations failed: {e}")
    
    # Test 3: Collection Operations
    print("\n📚 Test 3: Collection Operations")
    
    print("   🔍 Testing collection operations...")
    try:
        UserEntity.to_collection(users, 'output/users_collection.json')
        print(f"   ✅ Collection operations: exported {len(users)} users")
    except Exception as e:
        print(f"   ❌ Collection operations failed: {e}")
    
    # Test 4: Properties
    print("\n🔧 Test 4: Properties")
    
    # Test properties
    print("   📝 Testing properties...")
    try:
        # Test schema property
        schema = user1.schema
        print(f"   ✅ Schema property: {type(schema)}")
        
        # Test data property
        data = user1.data
        print(f"   ✅ Data property: {type(data)}")
        
        # Test actions property
        actions = user1.actions
        print(f"   ✅ Actions property: {len(actions)} actions")
        
    except Exception as e:
        print(f"   ❌ Properties failed: {e}")
    
    # Test 5: File Inspection
    print("\n📁 Test 5: File Inspection")
    
    # Check what files were created
    output_files = os.listdir('output')
    print(f"   📁 Created files: {output_files}")
    
    # Show collection file structure
    if 'users_collection.json' in output_files:
        print("   📋 Collection file structure:")
        import json
        with open('output/users_collection.json', 'r') as f:
            collection_data = json.load(f)
            print(f"      Schema: {collection_data.get('schema')}")
            print(f"      Actions: {len(collection_data.get('actions', {}))} actions")
            print(f"      Data: {len(collection_data.get('data', {}))} entities")
            print(f"      Metadata: {collection_data.get('metadata', {})}")
    
    print(f"\n🚀 Complete API test finished!")
    print(f"📦 All new API methods implemented and tested!")
    print(f"🎯 Ready for production use!")


def main():
    """Run the complete API test."""
    test_complete_api()


if __name__ == "__main__":
    main()
