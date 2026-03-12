# Project Reference — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 08-Feb-2026

Requirements and project status (output of GUIDE_22_PROJECT).

---

## Vision

xwentity provides a **unified entity system** (schema, actions, data, metadata, caching, state) to downstream libraries (xwmodels, xwbase, etc.) with a single, consistent API.

---

## Goals

1. Single entity class (XWEntity) composing XWSchema, XWAction list, XWData (via XWNode), metadata, and caching.
2. Clear contracts (IEntity, etc.) and abstract bases (AEntity) for extensibility.
3. Support lite / lazy / full install modes per eXonware standards.

---

## Functional Requirements (Summary)

| ID | Requirement | Priority | Status |
|----|-------------|----------|--------|
| FR-001 | Unified entity with schema validation | High | Done |
| FR-002 | Actions (register/execute) | High | Done |
| FR-003 | Data via XWData/XWNode | High | Done |
| FR-004 | Metadata, state, versioning | High | Done |
| FR-005 | Caching and performance modes | Medium | Done |
| FR-006 | Serialization (XWJSON, etc.) | High | Done |

---

## Non-Functional Requirements (5 Priorities)

1. **Security:** Input validation, no unsafe defaults.
2. **Usability:** Clear API, helpful errors, docs.
3. **Maintainability:** Contracts, base/facade structure, tests.
4. **Performance:** Caching, benchmarks, SLAs in REF_54_BENCH.md.
5. **Extensibility:** Interfaces, strategies, plugin-ready.

---

## Project Status Overview

- **Current phase:** Alpha (0.x)
- **Features:** Core entity, schema, actions, data, metadata, caching, state, serialization implemented.
- **Docs:** REF_* and logs under `docs/` per guides.

---

## Milestones

| Milestone | Target | Status |
|-----------|--------|--------|
| M1 — Core entity + schema + data | v0.0.1 | Done |
| M2 — Actions, state, serialization | v0.0.1 | Done |
| M3 — Docs & guide compliance | v0.1.0 | Done |

**M3 completion criteria (met):** REF_* aligned with GUIDE_00_MASTER, GUIDE_41_DOCS, GUIDE_51_TEST, GUIDE_35_REVIEW; REVIEW_* in `docs/logs/reviews/` and linked from REF_35; REF_35 "Missing vs Guides" empty; INDEX and REF_35 current.

---

## Related documentation

- **Planned merge/rename (XWObject → XWEntity, xwentity → xwmodels):** [docs/changes/MIGRATION_XWENTITY_REFACTOR.md](changes/MIGRATION_XWENTITY_REFACTOR.md)

---

*See GUIDE_22_PROJECT.md for requirements process. Updates: docs/logs/SUMMARY_PROJECT.md.*
