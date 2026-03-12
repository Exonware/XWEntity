# Architecture Reference — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 08-Feb-2026

System design and structure (output of GUIDE_13_ARCH).

---

## Overview

xwentity is a **domain-entities** layer library: unified entity model across schema, actions, and data. It consumes xwschema, xwaction, xwdata ([docs](../../xwdata/docs/INDEX.md), [REF_01_REQ](../../xwdata/docs/REF_01_REQ.md)), xwnode, and xwsystem.

---

## Layout

```
src/exonware/xwentity/
  __init__.py    # Public exports
  version.py
  contracts.py   # IEntity, IEntityState, IEntitySerialization
  errors.py
  defs.py
  config.py
  base.py        # AEntity, XWEntityMetadata
  facade.py      # Public API (re-exports)
  entity.py      # XWEntity implementation
  metaclass.py   # Property/action discovery
  schema/        # Validation and generation (validator, generator); entity uses this subpackage
```

The entity implementation uses a **schema/** subpackage for validation and schema generation (delegating to xwschema); it does not implement schema logic itself.

---

## Patterns

- **Facade:** Public API via `facade.py` and `__init__.py`; implementation in `entity.py`.
- **Contracts:** Interfaces in `contracts.py`; abstract bases in `base.py`.
- **Strategy:** Config-driven behavior (performance mode, caching, node/edge modes).

---

## Dependencies

- **Upstream:** xwsystem, xwschema, xwdata ([docs](../../xwdata/docs/INDEX.md)), xwaction, xwnode.
- **Optional:** xwlazy (for lazy install mode).

---

## Layering (eXonware)

xwentity sits in **Domain Entities**: uses Graph/Data (xwnode, xwdata) and Schema & Action (xwschema, xwaction); consumed by applications (xwmodels, xwbase, etc.).

---

*See GUIDE_13_ARCH.md for architecture standards.*
