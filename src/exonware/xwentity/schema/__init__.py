"""
Schema integration for xwentity.
Generate and validate entity data using xwschema.
"""

from .contracts import IEntitySchemaGenerator, IEntitySchemaValidator
from .generator import EntitySchemaGenerator
from .validator import EntitySchemaValidator
__all__ = [
    'IEntitySchemaGenerator',
    'IEntitySchemaValidator',
    'EntitySchemaGenerator',
    'EntitySchemaValidator',
]
