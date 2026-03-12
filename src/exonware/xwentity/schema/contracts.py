"""
Schema integration contracts for xwentity.
Company: eXonware.com
"""

from typing import Any, Protocol, runtime_checkable
@runtime_checkable


class IEntitySchemaGenerator(Protocol):
    """Interface for generating schemas from entity definitions."""

    async def generate_from_entity(
        self,
        entity: Any,
        format: str | None = None,
        **opts
    ) -> dict[str, Any]:
        """Generate schema from entity. Returns schema definition dict."""
        ...
@runtime_checkable


class IEntitySchemaValidator(Protocol):
    """Interface for validating entities against schemas."""

    async def validate_entity(
        self,
        entity: Any,
        schema: dict[str, Any],
        **opts
    ) -> dict[str, Any]:
        """Validate entity against schema. Returns dict with 'valid' (bool) and 'errors' (list)."""
        ...
