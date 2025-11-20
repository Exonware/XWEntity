
"""
🏗️ xEntity: Object-Oriented Data Modeling Layer

This module provides a sophisticated, schema-driven entity modeling system built on top of xData.
The design follows composition over inheritance principles and provides a clean, secure API
for creating data models with validation, policies, and metadata.

Key Features:
- 🏗️ **Composition over Inheritance**: xEntity contains xData, doesn't inherit from it
- 📋 **Schema-driven Behavior**: Runtime behavior dictated by schema definitions
- 🔒 **Explicit and Controlled API**: Clean, hard-to-misuse interface
- 🎯 **Headless by Design**: Framework-agnostic data payload provider

Usage:
    ```python
    from xlib.xentity import xEntity, xlive, xlink, xatt
    
    class User(xEntity):
        username: str = xlive(
            default="guest",
            validation={'required': True, 'min_length': 3},
            policy={'copy': 'deep'}
        )
        team: 'Team' = xlink(policy={'copy': 'link'})
    
    user = User(username="lex_volkov", team="team_alpha")
    user_clone = user.copy()  # Schema-driven copying
    ```
"""

from .core.xentity import (
    xEntity,
    xlive,
    xlink,
    xatt,
    BaseDescriptor,
    ReadOnlyProxy,
    EntityError,
    EntityValidationError,
    ReadOnlyError
)

__version__ = "1.0.0"

__all__ = [
    'xEntity',
    'xlive',
    'xlink', 
    'xatt',
    'BaseDescriptor',
    'ReadOnlyProxy',
    'EntityError',
    'EntityValidationError',
    'ReadOnlyError'
]
