#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/__init__.py
XWEntity - Entity System
This library provides a unified entity system that combines:
- Schema: XWSchema for validation and structure definition
- Actions: List of XWAction for operations and behaviors
- Data: XWData for data representation and management
- Metadata: Entity identity, state, versioning, and timestamps
- Caching: Performance optimization with caching
- State Management: Entity lifecycle state transitions
- Property Discovery: Automatic property discovery via decorators
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 28-Jan-2026
"""

from __future__ import annotations

# Public API from facade (GUIDE_13_ARCH, GUIDE_32_DEV_PY)
from exonware.xwentity.facade import (
    __version__,
    IEntity,
    IEntityState,
    IEntitySerialization,
    XWEntityMetadata,
    AEntity,
    XWEntity,
    XWCollection,
    XWGroup,
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityDataError,
    XWEntityNotFoundError,
    EntityType,
    EntityID,
    EntityData,
    EntityState,
    PerformanceMode,
    XWEntityConfig,
    get_config,
    set_config,
    get_entity_cache,
    clear_entity_cache,
)
__all__ = [
    "__version__",
    "IEntity",
    "IEntityState",
    "IEntitySerialization",
    "XWEntityMetadata",
    "AEntity",
    "XWEntity",
    "XWCollection",
    "XWGroup",
    "XWEntityError",
    "XWEntityValidationError",
    "XWEntityStateError",
    "XWEntityActionError",
    "XWEntityDataError",
    "XWEntityNotFoundError",
    "EntityType",
    "EntityID",
    "EntityData",
    "EntityState",
    "PerformanceMode",
    "XWEntityConfig",
    "get_config",
    "set_config",
    "get_entity_cache",
    "clear_entity_cache",
]
