# API Reference — xwentity

**Library:** exonware-xwentity  
**Version:** 0.0.1.0  
**Last Updated:** 29-Jan-2026

Canonical API reference (output of GUIDE_15_API). Complete, stable, navigable, example-driven.

---

## Overview

- **Provides:** Unified entity class (XWEntity) with schema, actions, data, metadata, caching, state.
- **For:** Downstream libs (xwmodels, xwbase) and app developers.
- **Modes:** lite (default), `[lazy]`, `[full]` per pyproject.toml.

---

## Quick Start

```python
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema

schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}}})
entity = XWEntity(schema=schema, data={"name": "Alice"})
entity.get("name")  # "Alice"
entity.validate()  # True
```

---

## Public Facades

### XWEntity

- **Purpose:** Unified entity: schema, actions, data, metadata, caching, state.
- **Constructor:** `XWEntity(schema=..., data=..., actions=..., config=..., **kwargs)`
- **Key methods:** `get`, `set`, `validate`, `register_action`, `execute_action`, `to_dict`, `from_dict`, state methods, cache helpers.
- **Errors:** See Errors section below.
- **Examples:** See REF_14_DX.md and GUIDE_01_USAGE.md.

### AEntity

- Abstract base implementing IEntity. Subclass for custom entities.

### XWEntityMetadata

- Metadata container (identity, state, versioning, timestamps).

---

## Configuration

- **XWEntityConfig** — config object for entity behavior.
- **get_config**, **set_config** — global config access.
- **get_entity_cache**, **clear_entity_cache** — cache control.

---

## Data Models & Contracts

- **IEntity**, **IEntityState**, **IEntitySerialization** — contracts (contracts.py).
- **EntityType**, **EntityID**, **EntityData**, **EntityState**, **PerformanceMode** — defs.

---

## Errors

| Exception | Meaning | Next step |
|-----------|---------|-----------|
| XWEntityError | Base for all entity errors | Check subclass message |
| XWEntityValidationError | Schema/data validation failed | Fix input or schema |
| XWEntityStateError | Invalid state transition | Ensure valid state flow |
| XWEntityActionError | Action execution failed | Check action logic/inputs |
| XWEntityDataError | Data access error | Check key/exists |
| XWEntityNotFoundError | Entity/item not found | Check id/path |

---

## Compatibility & Deprecations

- **Version:** 0.0.1.x — Alpha; API may evolve before 1.0.
- **Python:** >=3.12.

---

## Links

- [GUIDE_14_DX.md](REF_14_DX.md) — DX contract  
- [GUIDE_41_DOCS.md](guides/GUIDE_41_DOCS.md) — Doc standards  
- [REF_13_ARCH.md](REF_13_ARCH.md) — Architecture  
