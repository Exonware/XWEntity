"""
Entity schema validation for xwentity.
Uses xwschema for validation logic.
"""

from typing import Any
from exonware.xwsystem import get_logger
from exonware.xwschema import XWSchema
from .contracts import IEntitySchemaValidator
logger = get_logger(__name__)


class EntitySchemaValidator(IEntitySchemaValidator):
    """Validate entities against schemas using xwschema."""

    def __init__(self):
        self._validator = XWSchema({})
        logger.debug("EntitySchemaValidator initialized")

    async def validate_entity(
        self,
        entity: Any,
        schema: dict[str, Any],
        **opts
    ) -> dict[str, Any]:
        try:
            if hasattr(entity, 'to_dict'):
                entity_data = entity.to_dict()
            elif hasattr(entity, '__dict__'):
                entity_data = entity.__dict__
            elif isinstance(entity, dict):
                entity_data = entity
            else:
                entity_data = dict(entity) if hasattr(entity, '__iter__') else {'value': entity}
            is_valid, errors = self._validator.validate_schema(entity_data, schema)
            return {
                'valid': is_valid,
                'errors': errors if isinstance(errors, list) else [str(errors)] if errors else [],
                'entity_type': type(entity).__name__ if hasattr(entity, '__class__') else 'unknown'
            }
        except Exception as e:
            logger.error(f"Entity validation failed: {e}")
            return {
                'valid': False,
                'errors': [f"Validation error: {str(e)}"],
                'entity_type': type(entity).__name__ if hasattr(entity, '__class__') else 'unknown'
            }
