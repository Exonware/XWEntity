# Requirements Reference (REF_01_REQ)

**Project:** xwentity  
**Sponsor:** eXonware.com / eXonware Backend Team  
**Version:** 0.0.1  
**Last Updated:** 11-Feb-2026 00:00:00.000  
**Produced by:** [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md)

---

## Purpose of This Document

This document is the **single source of raw and refined requirements** collected from the project sponsor and stakeholders. It is updated on every requirements-gathering run. When the **Clarity Checklist** (section 12) reaches the agreed threshold, use this content to fill REF_12_IDEA, REF_22_PROJECT, REF_13_ARCH, REF_14_DX, REF_15_API, and planning artifacts. Template structure: [GUIDE_01_REQ.md](../guides/GUIDE_01_REQ.md).

---

## 1. Vision and Goals

| Field | Content |
|-------|---------|
| One-sentence purpose | **xwEntity = Schema + list of Actions + Data.** An entity you can save to JSON and load from JSON, validate with schema, execute actions with, and pass to xwmodels, xwbase, xwstorage, xwauth, and others—a better version of xwObject, with a single XWData instance as the engine for import/export and storage. (Sponsor confirmed.) |
| **Design principle (sponsor)** | **Very easy to use, reusable, and heavily used.** xwentity must be trivial to create inline (dict/JSON), load/save in many formats, and plug into the rest of the stack so it becomes the default entity abstraction everywhere. (Sponsor confirmed.) |
| Primary users/beneficiaries | Downstream eXonware libraries (xwmodels, xwbase, xwapi, xwauth, xwstorage, xwdata, xwbots, xwai) and developers building on eXonware. **Heavily used:** required by 8+ packages; single facade (XWEntity), 30+ test files, examples (simple_object, simple_bluesmyth). (Sponsor confirmed; evidence from codebase.) |
| Success (6 mo / 1 yr) | 6 mo: Stable entity API, REF_* compliance. 1 yr: Production use, ecosystem integration (xwmodels, xwbase, xwstorage). (Refine per REF_22.) |
| Top 3–5 goals (ordered) | 1) **Schema + Actions + Data** — Schema validates data; one schema can be shared by many entities (same schema, different data), useful for xwmodels. 2) **Actions** — xwaction, xwquery, xwschema capabilities. 3) **Data** — One XWData class as the engine (easier import/export, future data manipulation, xwstorage). 4) Clear contracts (IEntity, etc.) and abstract bases (AEntity). 5) Metadata, caching, state are extras on top. (Sponsor confirmed.) |
| Problem statement | Need one entity model (better than xwObject) that combines schema validation, actions, and data so it can be saved/loaded as JSON and reused across xwmodels, xwbase, xwstorage, xwauth, etc., with a single XWData engine. (Sponsor confirmed.) |

## 2. Scope and Boundaries

| In scope | Out of scope | Dependencies | Anti-goals |
|----------|--------------|--------------|------------|
| **Core:** Schema (validate data; shared by many entities with different data) + list of Actions (xwaction, xwquery, xwschema) + Data (one XWData as engine). Save/load to JSON; pass to xwmodels, xwbase, xwstorage, xwauth. **Extras:** metadata, caching, state, serialization. Contracts (IEntity, IEntityState, IEntitySerialization); lite/lazy/full install. (Sponsor confirmed.) | Storage/backend implementation (xwstorage); UI (xwui); auth (xwauth). (Sponsor confirmed.) | xwsystem, xwschema, xwdata, xwaction, xwnode; optional xwlazy. (Sponsor confirmed.) | Re-implementing schema/action logic (delegate to xwschema/xwaction); exposing internal cache as public API; more than one data engine per entity (must use one XWData). (Sponsor confirmed.) |

## 3. Stakeholders and Sponsor

| Sponsor (name, role, final say) | Main stakeholders | External customers/partners | Doc consumers |
|----------------------------------|-------------------|-----------------------------|---------------|
| eXonware (company); eXonware Backend Team (author, maintainer, final say on scope and priorities). | Project sponsor / eXonware; downstream REF owners. | None currently. Future: open-source adopters. | Downstream REF_22/REF_13 owners; devs using xwentity; AI agents (Cursor). |

## 4. Compliance and Standards

| Regulatory/standards | Security & privacy | Certifications/evidence |
|----------------------|--------------------|--------------------------|
| Per GUIDE_00_MASTER, GUIDE_11_COMP. (inferred) | Input validation, no unsafe defaults (from REF_22 NFRs). | None currently. Per GUIDE_00_MASTER when required. |

## 5. Product and User Experience

| Main user journeys/use cases | Developer persona & 1–3 line tasks | Usability/accessibility | UX/DX benchmarks |
|-----------------------------|------------------------------------|--------------------------|------------------|
| Create entity inline (dict or JSON); load/save JSON, TOML, XML, YAML, BSON (from and to); execute actions via queries (SQL or any xwquery-supported script); expose as FastAPI (or other) API. (Sponsor confirmed.) | **Easy:** Create xwentity inline from dict or JSON (no extra imports). Load/save to JSON, TOML, XML, YAML, BSON. **DX showcase:** Run SQL or other xwquery scripts against entity/actions; build APIs (e.g. FastAPI) from entity. **Sponsor intent:** Very easy to use, reusable, and heavily used—the default entity abstraction across the stack. Limitless possibilities—entity fits into scripts, queries, APIs, storage, auth, etc. (Sponsor confirmed.) | Clear API, helpful errors, docs; DX examples for inline creation, multi-format I/O, query execution, API creation. (Sponsor confirmed.) | Inline creation; multi-format load/save; query-driven actions; API-from-entity. (Sponsor confirmed.) |

## 6. API and Surface Area

| Main entry points / "key code" | Easy (1–3 lines) vs advanced | Integration/existing APIs | Not in public API |
|--------------------------------|------------------------------|---------------------------|-------------------|
| XWEntity, IEntity, AEntity, XWEntityMetadata; XWEntityConfig, get_config, set_config; get_entity_cache, clear_entity_cache; errors; types (EntityType, EntityID, EntityData, EntityState, PerformanceMode). **DX must support:** create from dict/JSON inline; load/save to JSON, TOML, XML, YAML, BSON; execute actions via xwquery (SQL and other scripts); expose via FastAPI or similar. **Ease of use:** single import, schema/data/actions as dicts; `from_dict`, `from_json`/`to_json`, `from_yaml`/`to_yaml`, `from_toml`/`to_toml`, `from_xml`/`to_xml`, `from_format`/`to_format` in code. **Reusable:** shared schema, one XWData engine. **Heavily used:** dependency of 8+ packages. (Sponsor confirmed; reverse‑engineered.) | **Easy (1–3 lines):** Create entity from dict or JSON inline (`XWEntity(schema={...}, data={...}, actions={...})` — no XWSchema/XWData imports needed); load from / save to JSON, TOML, XML, YAML, BSON (`from_json`, `to_json`, `from_format`, `to_format` in code). **Advanced:** Run SQL or xwquery scripts on entity/actions; build FastAPI (or other) API from entity. **Reusable & heavily used:** one facade, shared schema across entities, one XWData engine; consumed by xwmodels, xwbase, xwstorage, xwapi, xwauth, xwdata, xwbots, xwai. Limitless—entity usable everywhere. (Sponsor confirmed; reverse‑engineered from entity.py, examples, pyproject deps.) | xwschema (XWSchema), xwdata (XWData), xwaction, xwnode, xwquery (script/query execution), xwformats/xwdata (multi-format I/O), FastAPI/xwapi (API exposure). (Sponsor confirmed.) | Internal cache structure, schema/ subpackage implementation details. (Sponsor confirmed.) |

## 7. Architecture and Technology

| Required/forbidden tech | Preferred patterns | Scale & performance | Multi-language/platform |
|-------------------------|--------------------|----------------------|-------------------------|
| Python 3.12+; xwsystem, xwschema, xwdata, xwaction, xwnode. (from pyproject.toml, REF_13) | Facade (facade.py + __init__.py); contracts (contracts.py); abstract bases (base.py); strategy (config-driven caching, performance mode). (from REF_13) | Caching, benchmarks (REF_54_BENCH); SLAs in REF_54. (from REF_22) | Python only. (inferred) |

## 8. Non-Functional Requirements (Five Priorities)

| Security | Usability | Maintainability | Performance | Extensibility |
|----------|-----------|-----------------|-------------|---------------|
| Input validation, no unsafe defaults. (from REF_22) | **Very easy to use** (inline dict/JSON, multi-format I/O); clear API, helpful errors, docs; **reusable** (shared schema, one engine); **heavily used** across stack. (Sponsor confirmed; REF_22.) | Contracts, base/facade structure, tests (0.core, 1.unit, 2.integration; 3.advance optional per review). (from REF_22, REF_13) | Caching, benchmarks, REF_54_BENCH. (from REF_22) | Interfaces (IEntity, etc.), strategies, plugin-ready. (from REF_22) |

## 9. Milestones and Timeline

| Major milestones | Definition of done (first) | Fixed vs flexible |
|------------------|----------------------------|-------------------|
| M1 — Core entity + schema + data (Done); M2 — Actions, state, serialization (Done); M3 — Docs & guide compliance (Done). (from REF_22) | M3: REF_* aligned with guides; REVIEW_*; INDEX and REF_35 current. (from REF_22) | TBD |

## 10. Risks and Assumptions

| Top risks | Assumptions | Kill/pivot criteria |
|-----------|-------------|----------------------|
| TBD | Schema/actions cache keyed by entity type ID; XWData as engine; ISchema/IAction extend IData. (from REF_12) | TBD |

## 11. Workshop / Session Log (Optional)

| Date | Type | Participants | Outcomes |
|------|------|---------------|----------|
| 11-Feb-2026 | Reverse‑engineer + Q&A | User + Agent | Draft from code/docs (REF_22, REF_12, REF_13, README, pyproject, src); user to confirm. |
| 11-Feb-2026 | Q&A Batch A | Sponsor + Agent | Vision and scope confirmed: xwEntity = Schema + Actions + Data; one XWData as engine; save/load JSON; better xwObject; shared schema for xwmodels; extras (metadata, caching, state). |
| 11-Feb-2026 | Q&A Batch B (DX) | Sponsor + Agent | DX: create entity inline (dict/JSON); load/save JSON, TOML, XML, YAML, BSON; query execution (SQL, xwquery scripts) on actions; expose as FastAPI or similar API; limitless possibilities. |
| 11-Feb-2026 | Reverse‑engineer + sponsor intent | Agent | Vision: xwentity very easy to use, reusable, heavily used. Evidence: single facade; constructor accepts dict/JSON (schema, data, actions); from_*/to_* (json, yaml, toml, xml, format); 8+ packages depend on xwentity; 30+ test files. |

## 12. Clarity Checklist

| # | Criterion | ☐ |
|---|-----------|---|
| 1 | Vision and one-sentence purpose filled and confirmed | ☑ |
| 2 | Primary users and success criteria defined | ☑ |
| 3 | Top 3–5 goals listed and ordered | ☑ |
| 4 | In-scope and out-of-scope clear | ☑ |
| 5 | Dependencies and anti-goals documented | ☑ |
| 6 | Sponsor and main stakeholders identified | ☑ |
| 7 | Compliance/standards stated or deferred | ☑ |
| 8 | Main user journeys / use cases listed | ☑ |
| 9 | API / "key code" expectations captured | ☑ |
| 10 | Architecture/technology constraints captured | ☑ |
| 11 | NFRs (Five Priorities) addressed | ☑ |
| 12 | Milestones and DoD for first milestone set | ☑ |
| 13 | Top risks and assumptions documented | ☑ |
| 14 | Sponsor confirmed vision, scope, priorities | ☑ |

**Clarity score:** 14 / 14. **Ready to fill downstream docs?** ☑ Yes

---

*Inferred content is marked; sponsor confirmation required. Per GUIDE_01_REQ.*
