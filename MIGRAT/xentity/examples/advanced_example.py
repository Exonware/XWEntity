#!/usr/bin/env python3
"""
🏢 Advanced xEntity Example
Demonstrates xEntity using both xAction decoration and xSchema with advanced features.

This example shows:
- Complex schema definitions with confidential fields
- Multiple xAction decorators with validation
- Schema validation and data transformation
- Advanced entity lifecycle management
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from src.xlib.xentity import xEntity, EntityState
from src.xlib.xdata import xSchema
from src.xlib.xaction import xAction


class UserEntity(xEntity):
    """
    🧑‍💼 Advanced User Entity Example
    
    Demonstrates:
    - Complex schema with confidential fields
    - Multiple xAction decorators
    - Schema validation and transformation
    - Entity lifecycle management
    """
    
    def __init__(self, username: str, email: str, password: str):
        # Define comprehensive user schema with confidential fields
        user_schema = xSchema(
            value="user_schema",
            data={
                "type": "object",
                "title": "User Account Schema",
                "description": "Complete user account with security features",
                "properties": {
                    "username": {
                        "type": "string",
                        "minLength": 3,
                        "maxLength": 50,
                        "pattern": "^[a-zA-Z0-9_]+$",
                        "description": "Unique username for login"
                    },
                    "email": {
                        "type": "string",
                        "format": "email",
                        "description": "User's email address"
                    },
                    "password": {
                        "type": "string",
                        "minLength": 8,
                        "pattern": "^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]",
                        "description": "Secure password with complexity requirements",
                        "confidential": True  # 🔒 Mark as confidential
                    },
                    "password_hash": {
                        "type": "string",
                        "description": "Hashed password for storage",
                        "confidential": True  # 🔒 Mark as confidential
                    },
                    "salt": {
                        "type": "string",
                        "description": "Password salt for security",
                        "confidential": True  # 🔒 Mark as confidential
                    },
                    "profile": {
                        "type": "object",
                        "properties": {
                            "first_name": {"type": "string", "minLength": 1},
                            "last_name": {"type": "string", "minLength": 1},
                            "age": {"type": "integer", "minimum": 13, "maximum": 120},
                            "bio": {"type": "string", "maxLength": 500},
                            "avatar_url": {"type": "string", "format": "uri"}
                        },
                        "required": ["first_name", "last_name"]
                    },
                    "preferences": {
                        "type": "object",
                        "properties": {
                            "theme": {"type": "string", "enum": ["light", "dark", "auto"]},
                            "language": {"type": "string", "enum": ["en", "es", "fr", "de"]},
                            "notifications": {"type": "boolean"},
                            "timezone": {"type": "string"}
                        },
                        "default": {
                            "theme": "auto",
                            "language": "en",
                            "notifications": True,
                            "timezone": "UTC"
                        }
                    },
                    "security": {
                        "type": "object",
                        "properties": {
                            "two_factor_enabled": {"type": "boolean", "default": False},
                            "last_login": {"type": "string", "format": "date-time"},
                            "login_attempts": {"type": "integer", "minimum": 0, "default": 0},
                            "locked_until": {"type": "string", "format": "date-time"},
                            "api_keys": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "key": {"type": "string", "confidential": True},
                                        "name": {"type": "string"},
                                        "created": {"type": "string", "format": "date-time"},
                                        "last_used": {"type": "string", "format": "date-time"}
                                    }
                                }
                            }
                        }
                    },
                    "status": {
                        "type": "string",
                        "enum": ["active", "inactive", "suspended", "pending_verification"],
                        "default": "pending_verification"
                    },
                    "roles": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["user", "moderator", "admin", "super_admin"]},
                        "default": ["user"]
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "readOnly": True
                    }
                },
                "required": ["username", "email", "password", "profile"]
            }
        )
        
        # Initialize with data
        super().__init__(
            schema=user_schema,
            data={
                "username": username,
                "email": email,
                "password": password,  # Will be hashed by action
                "profile": {
                    "first_name": "",
                    "last_name": "",
                    "age": None,
                    "bio": "",
                    "avatar_url": ""
                },
                "preferences": {
                    "theme": "auto",
                    "language": "en",
                    "notifications": True,
                    "timezone": "UTC"
                },
                "security": {
                    "two_factor_enabled": False,
                    "last_login": None,
                    "login_attempts": 0,
                    "locked_until": None,
                    "api_keys": []
                },
                "status": "pending_verification",
                "roles": ["user"],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            },
            entity_type="user"
        )
    
    @xAction(
        api_name="hash-password",
        roles=["*"],  # Internal action
        description="Hash the password for secure storage",
        input_schemas={
            "password": {"type": "string", "minLength": 8}
        }
    )
    def _hash_password(self, password: str) -> Dict[str, str]:
        """Hash password and return salt and hash."""
        import hashlib
        import secrets
        
        # Generate salt
        salt = secrets.token_hex(16)
        
        # Hash password with salt
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        return {
            "password_hash": password_hash,
            "salt": salt
        }
    
    @xAction(
        api_name="verify-password",
        roles=["*"],  # Internal action
        description="Verify password against stored hash",
        input_schemas={
            "password": {"type": "string", "minLength": 1}
        }
    )
    def _verify_password(self, password: str) -> bool:
        """Verify password against stored hash."""
        import hashlib
        
        stored_hash = self.get("password_hash")
        salt = self.get("salt")
        
        if not stored_hash or not salt:
            return False
        
        # Hash input password with stored salt
        input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        
        return input_hash == stored_hash
    
    @xAction(
        api_name="complete-registration",
        roles=["*"],  # Public action
        description="Complete user registration with profile data",
        input_schemas={
            "first_name": {"type": "string", "minLength": 1, "maxLength": 50},
            "last_name": {"type": "string", "minLength": 1, "maxLength": 50},
            "age": {"type": "integer", "minimum": 13, "maximum": 120},
            "bio": {"type": "string", "maxLength": 500},
            "avatar_url": {"type": "string", "format": "uri"}
        }
    )
    def complete_registration(self, first_name: str, last_name: str, 
                            age: Optional[int] = None, bio: str = "", 
                            avatar_url: str = "") -> Dict[str, Any]:
        """Complete user registration with profile information."""
        # Hash password if not already done
        if not self.get("password_hash"):
            password = self.get("password")
            hash_result = self._hash_password(password)
            self.set("password_hash", hash_result["password_hash"])
            self.set("salt", hash_result["salt"])
            # Remove plain password
            self.set("password", None)
        
        # Update profile
        profile = self.get("profile", {})
        profile.update({
            "first_name": first_name,
            "last_name": last_name,
            "age": age,
            "bio": bio,
            "avatar_url": avatar_url
        })
        self.set("profile", profile)
        
        # Update status and timestamps
        self.set("status", "active")
        self.set("updated_at", datetime.utcnow().isoformat())
        
        return {
            "success": True,
            "user_id": self.id,
            "status": "active",
            "profile": profile
        }
    
    @xAction(
        api_name="authenticate",
        roles=["*"],  # Public action
        description="Authenticate user with password",
        input_schemas={
            "password": {"type": "string", "minLength": 1}
        }
    )
    def authenticate(self, password: str) -> Dict[str, Any]:
        """Authenticate user with password."""
        # Check if account is locked
        locked_until = self.get("security", {}).get("locked_until")
        if locked_until:
            lock_time = datetime.fromisoformat(locked_until)
            if datetime.utcnow() < lock_time:
                return {
                    "success": False,
                    "error": "Account temporarily locked",
                    "locked_until": locked_until
                }
        
        # Verify password
        if self._verify_password(password):
            # Reset login attempts
            security = self.get("security", {})
            security["login_attempts"] = 0
            security["last_login"] = datetime.utcnow().isoformat()
            security["locked_until"] = None
            self.set("security", security)
            
            return {
                "success": True,
                "user_id": self.id,
                "username": self.get("username"),
                "roles": self.get("roles", []),
                "last_login": security["last_login"]
            }
        else:
            # Increment login attempts
            security = self.get("security", {})
            security["login_attempts"] = security.get("login_attempts", 0) + 1
            
            # Lock account after 5 failed attempts
            if security["login_attempts"] >= 5:
                lock_time = datetime.utcnow() + timedelta(minutes=30)
                security["locked_until"] = lock_time.isoformat()
            
            self.set("security", security)
            
            return {
                "success": False,
                "error": "Invalid password",
                "attempts_remaining": max(0, 5 - security["login_attempts"])
            }
    
    @xAction(
        api_name="update-preferences",
        roles=["user", "moderator", "admin", "super_admin"],
        description="Update user preferences",
        input_schemas={
            "theme": {"type": "string", "enum": ["light", "dark", "auto"]},
            "language": {"type": "string", "enum": ["en", "es", "fr", "de"]},
            "notifications": {"type": "boolean"},
            "timezone": {"type": "string"}
        }
    )
    def update_preferences(self, theme: Optional[str] = None, 
                          language: Optional[str] = None,
                          notifications: Optional[bool] = None,
                          timezone: Optional[str] = None) -> Dict[str, Any]:
        """Update user preferences."""
        preferences = self.get("preferences", {})
        
        if theme is not None:
            preferences["theme"] = theme
        if language is not None:
            preferences["language"] = language
        if notifications is not None:
            preferences["notifications"] = notifications
        if timezone is not None:
            preferences["timezone"] = timezone
        
        self.set("preferences", preferences)
        self.set("updated_at", datetime.utcnow().isoformat())
        
        return {
            "success": True,
            "preferences": preferences
        }
    
    @xAction(
        api_name="generate-api-key",
        roles=["user", "moderator", "admin", "super_admin"],
        description="Generate a new API key for the user",
        input_schemas={
            "name": {"type": "string", "minLength": 1, "maxLength": 50}
        }
    )
    def generate_api_key(self, name: str) -> Dict[str, Any]:
        """Generate a new API key."""
        import secrets
        
        # Generate API key
        api_key = f"xcb_{secrets.token_urlsafe(32)}"
        
        # Create API key record
        key_record = {
            "key": api_key,
            "name": name,
            "created": datetime.utcnow().isoformat(),
            "last_used": None
        }
        
        # Add to security.api_keys
        security = self.get("security", {})
        api_keys = security.get("api_keys", [])
        api_keys.append(key_record)
        security["api_keys"] = api_keys
        self.set("security", security)
        
        self.set("updated_at", datetime.utcnow().isoformat())
        
        return {
            "success": True,
            "api_key": api_key,  # Only returned once
            "name": name,
            "created": key_record["created"]
        }
    
    @xAction(
        api_name="revoke-api-key",
        roles=["user", "moderator", "admin", "super_admin"],
        description="Revoke an API key by name",
        input_schemas={
            "name": {"type": "string", "minLength": 1}
        }
    )
    def revoke_api_key(self, name: str) -> Dict[str, Any]:
        """Revoke an API key by name."""
        security = self.get("security", {})
        api_keys = security.get("api_keys", [])
        
        # Find and remove the key
        original_count = len(api_keys)
        api_keys = [key for key in api_keys if key["name"] != name]
        
        if len(api_keys) == original_count:
            return {
                "success": False,
                "error": f"API key '{name}' not found"
            }
        
        security["api_keys"] = api_keys
        self.set("security", security)
        self.set("updated_at", datetime.utcnow().isoformat())
        
        return {
            "success": True,
            "message": f"API key '{name}' revoked successfully"
        }
    
    @xAction(
        api_name="suspend-user",
        roles=["admin", "super_admin"],
        description="Suspend user account",
        input_schemas={
            "reason": {"type": "string", "minLength": 10, "maxLength": 500}
        }
    )
    def suspend_user(self, reason: str) -> Dict[str, Any]:
        """Suspend user account."""
        self.set("status", "suspended")
        self.set("updated_at", datetime.utcnow().isoformat())
        
        # Add suspension metadata
        if not self.get("metadata"):
            self.set("metadata", {})
        
        metadata = self.get("metadata")
        metadata["suspension"] = {
            "reason": reason,
            "suspended_at": datetime.utcnow().isoformat(),
            "suspended_by": "admin"  # In real app, get from context
        }
        self.set("metadata", metadata)
        
        return {
            "success": True,
            "user_id": self.id,
            "status": "suspended",
            "reason": reason
        }
    
    @xAction(
        api_name="activate-user",
        roles=["admin", "super_admin"],
        description="Activate suspended user account"
    )
    def activate_user(self) -> Dict[str, Any]:
        """Activate suspended user account."""
        if self.get("status") != "suspended":
            return {
                "success": False,
                "error": "User is not suspended"
            }
        
        self.set("status", "active")
        self.set("updated_at", datetime.utcnow().isoformat())
        
        # Clear suspension metadata
        metadata = self.get("metadata", {})
        if "suspension" in metadata:
            del metadata["suspension"]
            self.set("metadata", metadata)
        
        return {
            "success": True,
            "user_id": self.id,
            "status": "active"
        }
    
    @xAction(
        api_name="change-password",
        roles=["user", "moderator", "admin", "super_admin"],
        description="Change user password",
        input_schemas={
            "current_password": {"type": "string", "minLength": 1},
            "new_password": {"type": "string", "minLength": 8}
        }
    )
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        # Verify current password
        if not self._verify_password(current_password):
            return {
                "success": False,
                "error": "Current password is incorrect"
            }
        
        # Hash new password
        hash_result = self._hash_password(new_password)
        self.set("password_hash", hash_result["password_hash"])
        self.set("salt", hash_result["salt"])
        self.set("updated_at", datetime.utcnow().isoformat())
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
    
    def get_public_profile(self) -> Dict[str, Any]:
        """Get public profile information (excluding confidential data)."""
        return {
            "id": self.id,
            "username": self.get("username"),
            "profile": self.get("profile"),
            "status": self.get("status"),
            "created_at": self.get("created_at"),
            "updated_at": self.get("updated_at")
        }
    
    def get_confidential_fields(self) -> List[str]:
        """Get list of confidential fields in the schema."""
        schema_data = self.schema.to_native()
        confidential_fields = []
        
        def find_confidential_fields(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    if isinstance(value, dict) and value.get("confidential"):
                        confidential_fields.append(current_path)
                    elif isinstance(value, dict):
                        find_confidential_fields(value, current_path)
                    elif isinstance(value, list):
                        for i, item in enumerate(value):
                            find_confidential_fields(item, f"{current_path}[{i}]")
        
        find_confidential_fields(schema_data.get("properties", {}))
        return confidential_fields


def run_advanced_example():
    """Run the advanced xEntity example."""
    print("🏢 Advanced xEntity Example with xAction and xSchema")
    print("=" * 60)
    
    # Create user entity
    print("\n1. Creating User Entity...")
    user = UserEntity(
        username="john_doe",
        email="john.doe@example.com",
        password="SecurePass123!"
    )
    
    print(f"✅ User created: {user.id}")
    print(f"📋 Schema validation: {user.validate()}")
    print(f"🔒 Confidential fields: {user.get_confidential_fields()}")
    
    # Complete registration
    print("\n2. Completing Registration...")
    result = user.execute_action("complete-registration", 
                               first_name="John", 
                               last_name="Doe",
                               age=30,
                               bio="Software developer and tech enthusiast")
    
    print(f"✅ Registration result: {result}")
    print(f"📊 User status: {user.get('status')}")
    
    # Test authentication
    print("\n3. Testing Authentication...")
    auth_result = user.execute_action("authenticate", password="SecurePass123!")
    print(f"✅ Authentication result: {auth_result}")
    
    # Update preferences
    print("\n4. Updating Preferences...")
    pref_result = user.execute_action("update-preferences", 
                                    theme="dark", 
                                    language="en",
                                    notifications=False)
    print(f"✅ Preferences updated: {pref_result}")
    
    # Generate API key
    print("\n5. Generating API Key...")
    api_result = user.execute_action("generate-api-key", name="Development Key")
    print(f"✅ API key generated: {api_result}")
    
    # Show available actions
    print("\n6. Available Actions:")
    actions = user.list_actions()
    for action_name, action_info in actions.items():
        print(f"  🔧 {action_name}: {action_info.get('description', 'No description')}")
    
    # Show public profile
    print("\n7. Public Profile:")
    public_profile = user.get_public_profile()
    print(f"📋 Public profile: {public_profile}")
    
    # Test schema validation
    print("\n8. Schema Validation Test:")
    print(f"✅ Valid data: {user.validate()}")
    
    # Test invalid data
    print("\n9. Testing Invalid Data...")
    try:
        user.set("email", "invalid-email")
        print(f"❌ Should fail validation: {user.validate()}")
    except Exception as e:
        print(f"✅ Validation caught error: {e}")
    
    # Export entity
    print("\n10. Entity Export:")
    export_data = user.to_native()
    print(f"📦 Exported keys: {list(export_data.keys())}")
    print(f"📊 Entity type: {export_data.get('entity_type')}")
    print(f"🆔 Entity ID: {export_data.get('id')}")
    
    print("\n✅ Advanced xEntity example completed successfully!")
    return user


if __name__ == "__main__":
    run_advanced_example()
