# Usage Guide — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 29-Jan-2026

How to use xwentity with examples (per GUIDE_41_DOCS, GUIDE_14_DX).

---

## Installation

```bash
# Lite (default)
pip install exonware-xwentity

# With lazy install support
pip install exonware-xwentity[lazy]

# Full optional deps
pip install exonware-xwentity[full]
```

---

## Quick Start

```python
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema

schema = XWSchema({
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "age": {"type": "integer"}
    }
})
entity = XWEntity(schema=schema, data={"name": "Alice", "age": 30})
print(entity.get("name"))  # Alice
assert entity.validate()
```

---

## Actions

```python
entity.register_action("greet", lambda e: f"Hello, {e.get('name')}")
result = entity.execute_action("greet")  # "Hello, Alice"
```

---

## Serialization

```python
d = entity.to_dict()
restored = XWEntity.from_dict(d)
```

---

## Configuration & Caching

```python
from exonware.xwentity import get_config, set_config, get_entity_cache, clear_entity_cache

# Configure global defaults if needed
# get_config() / set_config()
# get_entity_cache() / clear_entity_cache()
```

---

## More Examples

See `examples/simple_example/` in the repo and REF_14_DX.md for happy paths.

---

*See REF_15_API.md for full API; GUIDE_14_DX.md for DX standards.*
