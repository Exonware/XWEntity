#!/usr/bin/env python3
"""
Simple test using the existing xEntity facade.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.xlib.xentity import xEntity
from src.xlib.xentity.config import use_performance_mode
from src.xlib.xdata.new_3.schema import xSchema
from src.xlib.xaction import xAction

# Set default to PERFORMANCE mode
use_performance_mode()


class UserEntity(xEntity):
    """Simple user entity using existing facade."""
    
    @xSchema(length_min=1, length_max=50, pattern="^[a-zA-Z0-9_]+$", required=True)
    def username(self) -> str: pass
    
    @xAction(api_name="update-password", roles=["*"])
    def update_password(self, new_password: str) -> dict:
        """Update user password."""
        return {"success": True, "message": "Password updated"}


def simple_test():
    """Test the existing facade."""
    print("🔍 Simple Test: Existing xEntity Facade")
    print("=" * 50)
    
    # Create user
    user = UserEntity(username="john_doe", email="john@example.com")
    print(f"✅ User created: {user.username}")
    
    # Test properties
    print(f"\n📊 Properties:")
    print(f"   Data: {type(user.data)}")
    print(f"   Data value: {user.data}")
    print(f"   Schema: {type(user.schema)}")
    print(f"   Schema value: {user.schema}")
    
    # Test actions
    print(f"\n🔧 Actions:")
    actions = user.export_actions()
    print(f"   Actions: {len(actions)} actions")
    for name, action in actions.items():
        print(f"     - {name}: {action.get('api_name', 'N/A')}")
    
    # Test to_dict
    print(f"\n📦 To Dict:")
    entity_dict = user.to_dict()
    print(f"   Keys: {list(entity_dict.keys())}")
    print(f"   Data: {entity_dict.get('_data', {})}")
    
    # Test to_file
    print(f"\n💾 To File:")
    user.to_file('output/simple_test.json')
    print(f"   ✅ Saved to: output/simple_test.json")


if __name__ == "__main__":
    simple_test()
