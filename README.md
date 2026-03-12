# xwentity

**Unified entity system.** Schema (xwschema), actions (xwaction), data (xwdata); metadata, caching, state management; XWNode integration. Used by xwmodels, xwbase, and the eXonware stack. Per project docs.

**Company:** eXonware.com · **Author:** eXonware Backend Team · **Email:** connect@exonware.com  
**Version:** (see pyproject/version) · **Updated:** See [version.py](src/exonware/xwentity/version.py) (`__date__`)

[![Status](https://img.shields.io/badge/status-beta-blue.svg)](https://exonware.com)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Install

```bash
pip install exonware-xwentity
```

---

## Quick start

```python
from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema

schema = XWSchema({"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}})
entity = XWEntity(schema=schema, data={"name": "Alice", "age": 30})
print(entity.data["name"])
```

See [docs/](docs/) for metadata, state, and REF_* when present.

---

## What you get

| Area | What's in it |
|------|----------------|
| **Entity** | Unified class: schema, actions, data, metadata, caching. |
| **Integration** | xwschema, xwaction, xwdata, XWNode. |
| **Lifecycle** | State management, property discovery. |

---

## Docs and tests

- **Start:** [docs/INDEX.md](docs/INDEX.md) or [docs/](docs/).
- **Tests:** Run from project root per project layout.

---

## License and links

MIT — see [LICENSE](LICENSE). **Homepage:** https://exonware.com · **Repository:** https://github.com/exonware/xwentity  

Contributing → CONTRIBUTING.md · Security → SECURITY.md (when present).

*Built with ❤️ by eXonware.com - Revolutionizing Python Development Since 2025*
