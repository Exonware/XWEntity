# DX Reference — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 29-Jan-2026

Developer experience contract: happy paths, errors, ergonomics (output of GUIDE_14_DX).

---

## Happy Paths (1–3 lines)

**Create entity with schema and data:**

```python
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema

schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}}})
entity = XWEntity(schema=schema, data={"name": "Alice"})
entity.get("name")  # "Alice"
```

**Validate and run actions:**

```python
entity.validate()  # True
entity.register_action("greet", lambda e: f"Hello, {e.get('name')}")
entity.execute_action("greet")  # "Hello, Alice"
```

---

## Defaults

- Safe by default: validation on, no silent ignores.
- Sane defaults: config via `XWEntityConfig` / `get_config()`.

---

## Errors

- `XWEntityValidationError` — validation failures  
- `XWEntityStateError` — invalid state transitions  
- `XWEntityActionError` — action execution errors  
- `XWEntityDataError` — data access errors  
- `XWEntityNotFoundError` — missing entity/item  

All are documented in REF_15_API.md with causes and next steps.

---

## Entry Points

- `from exonware.xwentity import XWEntity, ...` (primary)
- `from exonware.xwentity.facade import XWEntity, ...` (explicit facade)

---

*See GUIDE_14_DX.md for DX standards.*
