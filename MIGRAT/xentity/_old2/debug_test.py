#!/usr/bin/env python3
"""
Debug test to understand xEntity data initialization issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.xlib.xentity.complete_api import xEntity
from src.xlib.xentity.config import use_performance_mode
from src.xlib.xdata.new_3.schema import xSchema
from src.xlib.xaction import xAction

# Set default to PERFORMANCE mode
use_performance_mode()


class UserEntity(xEntity):
    """Simple user entity for debugging."""
    
    @xSchema(length_min=1, length_max=50, pattern="^[a-zA-Z0-9_]+$", required=True)
    def username(self) -> str: pass
    
    @xAction(api_name="update-password", roles=["*"])
    def update_password(self, new_password: str) -> dict:
        """Update user password."""
        return {"success": True, "message": "Password updated"}


def debug_test():
    """Debug the data initialization issue."""
    print("🔍 Debug Test: xEntity Data Initialization")
    print("=" * 50)
    
    # Create user
    user = UserEntity(username="john_doe", email="john@example.com")
    print(f"✅ User created: {user.username}")
    
    # Debug engine
    print(f"\n🔧 Engine Debug:")
    print(f"   Engine: {type(user._engine)}")
    print(f"   Engine data: {type(user._engine.data)}")
    print(f"   Engine data value: {user._engine.data}")
    
    # Debug properties
    print(f"\n📊 Properties Debug:")
    print(f"   Data property: {type(user.data)}")
    print(f"   Data value: {user.data}")
    print(f"   Schema property: {type(user.schema)}")
    print(f"   Schema value: {user.schema}")
    
    # Test data operations
    print(f"\n🔧 Data Operations Debug:")
    try:
        data_dict = user.data_to_native()
        print(f"   Data to native: {data_dict}")
    except Exception as e:
        print(f"   ❌ Data to native failed: {e}")
    
    try:
        user.data_to_file('output/debug_data.json')
        print(f"   ✅ Data to file: output/debug_data.json")
    except Exception as e:
        print(f"   ❌ Data to file failed: {e}")
    
    # Test actions
    print(f"\n🔧 Actions Debug:")
    try:
        actions = user.actions
        print(f"   Actions: {len(actions)} actions")
        for name, action in actions.items():
            print(f"     - {name}: {action.get('api_name', 'N/A')}")
    except Exception as e:
        print(f"   ❌ Actions failed: {e}")


if __name__ == "__main__":
    debug_test()
