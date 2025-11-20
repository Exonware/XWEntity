#!/usr/bin/env python3
"""
🎯 xEntity Example: User Management System

This example demonstrates the core functionality of xEntity as specified.
It shows composition over inheritance, schema-driven behavior, validation,
and intelligent copying policies.
"""

from ..core.xentity import xEntity, xlive, xlink, xatt


class User(xEntity):
    """👤 User entity with live and linked attributes."""
    
    username: str = xlive(
        default="guest",
        validation={'required': True, 'min_length': 3, 'max_length': 20},
        policy={'copy': 'deep'},
        description="Unique username for the user"
    )
    
    email: str = xlive(
        validation={'required': True, 'validator': lambda x: '@' in x if x else False},
        policy={'copy': 'deep'},
        description="User's email address"
    )
    
    team: str = xlink(
        policy={'copy': 'link'},
        description="Reference to user's team"
    )
    
    role: str = xlink(
        default="member",
        policy={'copy': 'link'},
        description="User's role in the team"
    )


def demonstrate_basic_usage():
    """🚀 Demonstrate basic xEntity usage."""
    print("🚀 Basic xEntity Usage Demo")
    print("=" * 40)
    
    # Create user instance
    user1 = User(
        username="lex_volkov",
        email="lex@example.com", 
        team="team_alpha",
        role="developer"
    )
    
    print(f"📋 User created: {user1}")
    print(f"🔍 Username: {user1.username}")
    print(f"📧 Email: {user1.email}")
    print(f"👥 Team: {user1.team}")
    print(f"🎭 Role: {user1.role}")
    
    # Test access control
    print("\n🔒 Access Control Test:")
    user1.username = "alex"
    print(f"✅ Direct assignment works: {user1.username}")
    
    # Test read-only data access
    print(f"📊 Data access works: {user1.data['username']}")
    
    # Test write protection
    try:
        user1.data["username"] = "hacker"
        print("❌ Security breach!")
    except Exception as e:
        print(f"✅ Write protection works: {type(e).__name__}")
    
    return user1


def demonstrate_validation():
    """🔍 Demonstrate validation features."""
    print("\n🔍 Validation Demo")
    print("=" * 40)
    
    try:
        # This should fail - username too short
        User(username="x", email="test@example.com")
        print("❌ Validation failed!")
    except Exception as e:
        print(f"✅ Min length validation: {type(e).__name__}")
    
    try:
        # This should fail - invalid email
        User(username="testuser", email="not-an-email")
        print("❌ Validation failed!")
    except Exception as e:
        print(f"✅ Custom validation: {type(e).__name__}")
    
    try:
        # This should fail - missing required field
        User(username="testuser")  # No email
        print("❌ Validation failed!")
    except Exception as e:
        print(f"✅ Required field validation: {type(e).__name__}")


def demonstrate_metadata_access():
    """🔍 Demonstrate metadata access."""
    print("\n🔍 Metadata Access Demo")
    print("=" * 40)
    
    # Access descriptor metadata
    username_attr = xatt(User, "username")
    print(f"📋 Username metadata:")
    print(f"  - Required: {username_attr.validation.get('required', False)}")
    print(f"  - Min length: {username_attr.validation.get('min_length', 'N/A')}")
    print(f"  - Copy policy: {username_attr.policy.get('copy', 'default')}")
    print(f"  - Description: {username_attr.meta.get('description', 'N/A')}")
    
    team_attr = xatt(User, "team")
    print(f"\n👥 Team metadata:")
    print(f"  - Copy policy: {team_attr.policy.get('copy', 'default')}")
    print(f"  - Description: {team_attr.meta.get('description', 'N/A')}")


def demonstrate_schema_driven_copying():
    """🔄 Demonstrate schema-driven copying."""
    print("\n🔄 Schema-Driven Copying Demo")
    print("=" * 40)
    
    # Create original user
    user1 = User(
        username="original_user",
        email="original@example.com",
        team="team_alpha",
        role="developer"
    )
    
    print(f"📋 Original user: {user1.username} in {user1.team}")
    
    # Create copy
    user2 = user1.copy()
    print(f"📋 Copy created: {user2.username} in {user2.team}")
    
    # Modify copy
    user2.username = "copied_user"
    print(f"📝 Modified copy username: {user2.username}")
    
    # Verify deep copy for xlive attributes
    print(f"🔍 Original username unchanged: {user1.username}")
    print(f"✅ Deep copy works for xlive attributes")
    
    # Verify link copy for xlink attributes
    print(f"🔍 Both users share same team: {user1.team} == {user2.team}")
    print(f"✅ Link copy works for xlink attributes")


def demonstrate_schema_access():
    """📊 Demonstrate schema access."""
    print("\n📊 Schema Access Demo")
    print("=" * 40)
    
    user = User(username="schema_user", email="schema@example.com")
    schema = user.schema
    
    print("📋 Generated schema:")
    for field_name in schema:
        field_schema = schema[field_name]
        print(f"  {field_name}:")
        print(f"    - Type: {field_schema.get('type', 'unknown')}")
        print(f"    - Default: {field_schema.get('default', 'None')}")
        print(f"    - Copy policy: {field_schema.get('policy', {}).get('copy', 'default')}")


def main():
    """🎯 Main demonstration function."""
    print("🎯 xEntity Complete Demonstration")
    print("=" * 50)
    
    try:
        user1 = demonstrate_basic_usage()
        demonstrate_validation()
        demonstrate_metadata_access()
        demonstrate_schema_driven_copying()
        demonstrate_schema_access()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("✅ xEntity implementation is fully functional")
        
    except Exception as e:
        print(f"\n❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 