# Review: XWGroup / XWCollection Data Strategy – Scoring Matrix

**Company:** eXonware.com  
**Author:** eXonware Backend Team  
**Email:** [connect@exonware.com](mailto:connect@exonware.com)  

**Date:** 20260305  
**Artifact type:** Documentation / Architecture (design decision)  
**Scope:** xwentity — XWGroup/XWCollection data strategy options (extend entity vs data-under vs XWNode vs hybrid).  
**Owning guide:** GUIDE_35_REVIEW (review process); GUIDE_13_ARCH (architecture), GUIDE_41_DOCS (documentation).

---

## Summary

**Pass.** Strategy scoring document reviewed and relocated to xwentity LOG. Artifact defines **seven** design options (A–F plus **G: Data engine abstract**). **Option F** (B + first-class path API) and **Option G** (shared abstract data engine for entity/collection/group) both score **41** raw. F is best when path-based access is desired; G is best when centralizing XWData usage in one high-performance, reusable base. No critical issues; minor improvements and traceability actions below.

**Option G implemented (2026-03-05):** Shared base `ADataBackedObject` added in `base.py`; **AEntity**, **ACollection**, and **AGroup** now inherit it and use `_data_backed` (XWData) for serialization. Entity implements `_build_data_payload(**kwargs)` (metadata, data, optional schema, actions) and `_apply_data_from_dict()`; `to_dict(include_schema=True)` and `_from_dict()` delegate to the data engine. Collection and group already refactored to use the same pattern. See `ADataBackedObject` and the three subclass sites in `base.py`, `collection.py`, `group.py`, and entity serialization in `base.py` (AEntity) / `entity.py` (XWEntity).

---

## Artifact under review (relocated content)

### Purpose

Compare design options for how group/collection integrate with the data stack (XWEntity pattern, XWData, or XWNode).  
**Scale:** 1–5 per criterion (5 = best).  
**Date:** 2026-03-05.

---

### 1. Options Defined


| Id    | Option                                                           | Description                                                                                                                                                                                                                                                                                                                         |
| ----- | ---------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A** | **Extend XWEntity**                                              | XWGroup (and/or XWCollection) subclasses XWEntity. Group/collection *is* an entity; its `_data` holds the group structure (subgroup_ids, collection_ids, metadata). Full schema, actions, state, metadata, same as any entity.                                                                                                      |
| **B** | **Data under group/collection (XWData, same pattern as entity)** | XWGroup stays AGroup + XWObject. Add internal `_data: XWData` (or XWDataNode) holding serializable state (id, title, description, collection_ids, subgroup_ids). Use like XWEntity: path access, `to_dict()` = `_data.to_native()`, optional schema. Keep `_subgroups` / `_collections` as live object caches, synced with `_data`. |
| **C** | **XWNode directly for hierarchy**                                | Back the group *tree* with one XWNode (e.g. TREE_GRAPH_HYBRID) per root. Nodes hold metadata + refs (ids). Path-based access and serialization from the node. Live `_subgroups`/`_collections` stay as object cache, synced on load/mutate. No XWData layer.                                                                        |
| **D** | **Current (plain dicts, no node/data)**                          | Baseline: group = AGroup + XWObject + dicts for _subgroups, _collections; hand-written to_dict/from_dict. No XWNode or XWData.                                                                                                                                                                                                      |
| **E** | **Hybrid: XWData per group + XWNode for tree**                   | Each group has an XWData "document" (like B) for schema/validation and serialization; *and* the overall hierarchy is represented in an XWNode for path-based tree ops. Most capable, most moving parts.                                                                                                                             |
| **F** | **Data-under with path-as-API (B + first-class paths)**         | Same as B: one `_data: XWData` per group, live `_subgroups`/`_collections` as caches. In addition: the document shape is defined so every group/collection is path-addressable (e.g. `subgroups.team_a.collections.users`). Expose `get_at_path(path)` implemented as `_data.get(path)` (or XWDataNode path navigation). No second structure—path is a view over the same _data. |
| **G** | **Data engine abstract (shared base)**                          | Extract the _data (XWData) usage into a separate **abstract class** (e.g. `ADataBackedObject` or `ADataEngine`) that **AEntity, ACollection, and AGroup all use**. Single place for `_data` lifecycle, `to_dict()` = `_data.to_native()`, `from_dict()`, `_build_data()`, `_sync_data()` pattern. Same behavior as B but centralized: one implementation, fewer lines, consistent behavior across entity/collection/group. High-performance reuse—everybody uses the same thing. |


---

### 2. Criteria (1 = worst, 5 = best)


| Criterion               | Meaning                                                                                                                        |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------ |
| **Stack consistency**   | Aligns with how xwentity (XWEntity), xwstorage (HierarchicalDataModel), xwdata use XWNode/XWData. Same mental model and reuse. |
| **Serialization**       | Single source of truth for to_dict/from_dict; clean persistence (e.g. xwmodels); format support if needed.                     |
| **Path-based access**   | Ability to get group/collection by path (e.g. `get_at_path("org/teams/backend/collections/users")`) without manual walk.       |
| **Schema / validation** | Can validate group or collection shape/metadata with XWSchema (same as entity data).                                           |
| **Simplicity**          | Implementation and maintenance effort (5 = simplest, 1 = most complex).                                                        |
| **Lightweight**         | Runtime overhead: memory and CPU (5 = lightest).                                                                               |
| **API clarity**         | Public API stays clear; no confusion between "entity" and "group/collection"; easy to explain.                                 |
| **Extensibility**       | Easy to add later: queries, merge/diff, format conversion, tooling.                                                            |
| **Reuse**               | How much existing code (XWData, XWNode, XWEntity) is reused vs new code.                                                       |


---

### 3. Scoring Matrix


| Criterion           | A: Extend XWEntity | B: Data under (XWData) | C: XWNode direct | D: Current (dicts) | E: Hybrid (Data + Node) | F: Data + path-as-API | G: Data engine abstract |
| ------------------- | ------------------ | ---------------------- | ---------------- | ------------------ | ----------------------- | ----------------------- | ----------------------- |
| Stack consistency   | 5                  | 5                      | 4                | 2                  | 5                       | 5                       | 5                       |
| Serialization       | 5                  | 5                      | 4                | 2                  | 5                       | 5                       | 5                       |
| Path-based access   | 4                  | 4                      | 5                | 1                  | 5                       | **5**                   | 4                       |
| Schema / validation | 5                  | 5                      | 2                | 1                  | 5                       | 5                       | 5                       |
| Simplicity          | 2                  | 3                      | 3                | 5                  | 1                       | 3                       | **4**                   |
| Lightweight         | 1                  | 3                      | 4                | 5                  | 2                       | 3                       | 3                       |
| API clarity         | 2                  | 5                      | 5                | 5                  | 4                       | 5                       | 5                       |
| Extensibility       | 5                  | 5                      | 4                | 2                  | 5                       | 5                       | 5                       |
| Reuse               | 5                  | 5                      | 4                | 1                  | 4                       | 5                       | **5**                   |
| **Sum (raw)**       | **34**             | **40**                 | **35**           | **24**             | **36**                  | **41**                  | **41**                  |


---

### 4. Rationale (per option, per criterion)

**A: Extend XWEntity** — Stack consistency 5, Serialization 5, Path-based access 4, Schema/validation 5, Simplicity 2, Lightweight 1, API clarity 2, Extensibility 5, Reuse 5. MRO/semantics and “group vs entity” blur; full entity machinery per group.

**B: Data under (XWData)** — Stack consistency 5, Serialization 5, Path-based access 4, Schema/validation 5, Simplicity 3, Lightweight 3, API clarity 5, Extensibility 5, Reuse 5. Same “object has _data” pattern as XWEntity; clear type boundaries.

**C: XWNode direct** — Stack consistency 4, Serialization 4, Path-based access 5, Schema/validation 2, Simplicity 3, Lightweight 4, API clarity 5, Extensibility 4, Reuse 4. Best path-based fit; no XWData/schema.

**D: Current** — Baseline; lowest on consistency, serialization, path, validation, reuse; highest on simplicity and lightweight.

**E: Hybrid** — Best path + schema; Simplicity 1, Lightweight 2; two representations to sync.

**F: Data-under with path-as-API** — Same as B (single _data, sync to live caches) plus: document shape is path-addressable and API exposes `get_at_path(path)` via `_data.get(path)` (or XWDataNode). No second structure; path is a view over _data. Stack consistency 5, Serialization 5, Path-based access 5, Schema/validation 5, Simplicity 3, Lightweight 3, API clarity 5, Extensibility 5, Reuse 5. **Sum 41** — one point above B by making path access first-class on the same backing store.

**G: Data engine abstract (shared base)** — Extract _data (XWData) into an abstract class (e.g. ADataBackedObject) used by AEntity, ACollection, and AGroup. One place for _data lifecycle, to_dict/from_dict, _build_data/_sync_data. Same as B in behavior but centralized: fewer lines, one implementation, consistent high-performance reuse. Stack consistency 5, Serialization 5, Path-based access 4 (same as B unless path API added to base), Schema/validation 5, Simplicity 4 (one abstract to maintain), Lightweight 3, API clarity 5, Extensibility 5, Reuse 5. **Sum 41** — ties F; stronger on Simplicity (centralized), same Reuse; no path-as-API unless added to the shared base.

---

### 5. Weighted Score (optional)

Example weights: High (×1.5) Stack consistency, Serialization, API clarity; Medium (×1.0) Path-based access, Schema/validation, Simplicity, Reuse; Low (×0.7) Lightweight, Extensibility.  
Weighted sum: **F 42.0**, **G 41.5** (Simplicity 4), B 41.0, E 35.8, C 35.2, A 34.5, D 24.4.

---

### 6. Recommendation

- **Raw totals:** **F (41)** = **G (41)** > B (40) > E (36) > C (35) > A (34) > D (24).
- **Recommendation:** 
  - **F (Data-under with path-as-API)** when path-based access is desired: same as B with `get_at_path(path)` over _data (no second structure).
  - **G (Data engine abstract)** when centralizing XWData usage is the priority: extract _data into a shared abstract class (e.g. ADataBackedObject) used by AEntity, ACollection, and AGroup—one implementation, fewer lines, everybody uses the same thing in a high-performance way. Option B (already implemented) can be refactored toward G by introducing this base.
  - If neither path nor centralization is needed, **B** remains sufficient. Use **C (XWNode directly)** if path-oriented hierarchy is primary and schema on group document is not required. Consider **E** only when both document schema and a separate tree model are needed.

---

## Critical issues

- None. Options and criteria are well-defined; scoring is consistent and traceable to rationale.

---

## Improvements

- **New option F added:** Data-under with path-as-API (B + first-class paths) scores 41 raw / 42.0 weighted and is recommended when path-based access is desired; no second structure, path is a view over _data.
- **New option G added:** Data engine abstract (shared base for AEntity, ACollection, AGroup) scores 41 raw; similar to B but centralizes XWData usage in one abstract class for fewer lines and high-performance reuse—everybody uses the same thing.
- Add a one-line “Version” or “Last updated” in artifact header for future revisions (per GUIDE_41_DOCS).
- When a decision is implemented (e.g. Option B or F), add a short “Decision recorded” note and link to REF_13_ARCH or REF_22_PROJECT if the strategy is committed there.

---

## Optimizations

- Rationale section is summarized in this review log; full per-criterion bullets can remain in a separate REF or stay here if this file is the single source. No duplication of the matrix table.

---

## Missing features / alignment

- Optional: link to REF_13_ARCH (xwentity) or REF_22_PROJECT if XWGroup data strategy is captured there as a design decision or requirement.
- Optional: reference GUIDE_12_IDEA if this was explored as an idea before scoring.

---

## Compliance & standards

- **GUIDE_35_REVIEW:** Artifact type and scope identified; six categories applied; LOG evidence in `docs/logs/reviews/`.
- **GUIDE_41_DOCS:** Document placed under xwentity `docs/logs/reviews/` per REF/LOG ownership (project-level logs in package).
- **GUIDE_00_MASTER:** No contradiction with REF/LOG placement; review log is the canonical location for this scoring artifact.

---

## Traceability

- **From artifact:** Options A–G trace to existing code (XWGroup, XWCollection, XWEntity, xwstorage HierarchicalDataModel, xwdata). Option F extends B with no new backing structure—only API and data shape. Option G refactors B into a shared abstract data engine used by entity, collection, and group.
- **Decision recorded:** Option B implemented for both XWGroup and XWCollection (2026-03-05): internal `_data: XWData`, `to_dict()` = `_data.to_native()`, `from_dict(data)` restores `_data` and scalars; live `_subgroups`/`_collections` synced via `_sync_data()` on add/remove. See `xwentity/src/exonware/xwentity/group.py` and `collection.py`.
- **To REFs:** When option B (or other) is adopted, add traceability to REF_13_ARCH and/or REF_22_PROJECT.
- **Relocation:** Original location `docs/guides/XWGROUP_DATA_STRATEGY_SCORING.md` (repo root) removed; content moved here per GUIDE_35 and xwentity LOG ownership.

---

*Review performed per GUIDE_35_REVIEW. Artifact: XWGroup/XWCollection data strategy scoring. Canonical location: xwentity `docs/logs/reviews/`.*