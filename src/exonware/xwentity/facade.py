#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/facade.py
XWEntity — Public API facade.
Single entry point for public API per GUIDE_13_ARCH and GUIDE_32_DEV_PY.
Re-exports contracts, base, entity, errors, config, and defs.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 29-Jan-2026
"""

from __future__ import annotations
from exonware.xwentity.version import __version__
from exonware.xwentity.contracts import (
    IEntity,
    IEntityState,
    IEntitySerialization,
)
from exonware.xwentity.base import (
    XWEntityMetadata,
    AEntity,
    get_entity_cache,
    clear_entity_cache,
)
from exonware.xwentity.entity import XWEntity
from exonware.xwentity.collection import XWCollection
from exonware.xwentity.group import XWGroup
from exonware.xwentity.errors import (
    XWEntityError,
    XWEntityValidationError,
    XWEntityStateError,
    XWEntityActionError,
    XWEntityDataError,
    XWEntityNotFoundError,
)
from exonware.xwentity.defs import (
    EntityType,
    EntityID,
    EntityData,
    EntityState,
    PerformanceMode,
)
from exonware.xwentity.config import (
    XWEntityConfig,
    get_config,
    set_config,
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
