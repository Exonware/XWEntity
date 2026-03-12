"""
Entity schema generation for xwentity.
Uses xwschema for schema generation from entity data.
"""

from typing import Any
from exonware.xwsystem import get_logger
from exonware.xwschema import XWSchema
from exonware.xwschema.defs import SchemaGenerationMode
from .contracts import IEntitySchemaGenerator
from ..errors import XWEntityError
logger = get_logger(__name__)


class EntitySchemaGenerator(IEntitySchemaGenerator):
    """Generate schemas from entity definitions using xwschema."""

    async def generate_from_entity(
        self,
        entity: Any,
        format: str | None = None,
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
            mode = opts.pop('mode', SchemaGenerationMode.INFER)
            config = opts.pop('config', None)
            schema_obj = await XWSchema.from_data(entity_data, mode=mode, config=config)
            schema = schema_obj.to_native()
            logger.debug(f"Schema generated from entity: {type(entity).__name__}")
            return schema
        except Exception as e:
            logger.error(f"Failed to generate schema from entity: {e}")
            raise XWEntityError(f"Failed to generate schema from entity: {str(e)}") from e
