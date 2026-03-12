# Idea Reference — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 29-Jan-2026

Active ideas and decisions (output of GUIDE_12_IDEA). Status: New / Exploring / Approved / Rejected / Deferred.

---

## Overview

Ideas that drive xwentity features and improvements are captured here. Approved ideas move to REF_22_PROJECT.md as requirements.

---

## Active Ideas

### IDEA-001 — xwEntity: Schema + Actions + Data (xw_data as engine)

| Field | Value |
|-------|--------|
| **Status** | Exploring |
| **Raised** | 29-Jan-2026 |

**Summary:** xwEntity is three things in one: **schema**, **list of actions**, and **data**. Schema and actions are fixed and cacheable across entities; data varies per entity. xwEntity should use **xw_data** (a type of XWData) as its engine, and extend xwObject while preferring xwData's behavior where the two differ.

**Three components**

1. **Schema** — Not repeated; shared across entities. Multiple entities can share the same schema and actions; only data changes per entity.
2. **List of actions** — Fixed per "shape"; cacheable together with schema.
3. **Data** — Always different per entity; the variable part.

**Caching:** Cache schema and actions (they are fixed). Do not treat data as cacheable in the same way; data is per-entity.

**In code:** Structure is: schema, actions, data (e.g. constructor or representation: schema, then actions, then data).

**Engine: XWData (xwdata library)**

- **xwdata** is the library; **XWData** is the class to use as the engine (same idea as using XWSchema as the engine elsewhere).
- xwEntity uses an instance of **XWData** as its engine → reuse of features, less code, feature-rich.

**Cache**

- Schema/actions cache lives as **static** on XWEntity (class-level).
- **Assumption:** `exonware.xwentity.cached["Entity Type ID"]` returns `(schema, list of actions)` — i.e. the cache is keyed by entity type ID and yields the fixed (schema, actions) pair for that type.

**XWData model: everything is IData**

- Do **not** add optional schema/actions to XWData's constructor. Instead:
  - **XWSchema as a sub-node** — schema is a child node inside XWData.
  - **ISchema extends IData** and **IAction extends IData** — so whatever is added to XWData is of type IData (unified under IData).
- **XWData accepts a child that is `list[IData]`** — schema, actions, and data are all represented as IData (or list[IData]).

**Implementation rule: do not re-implement**

- In **abstracts** (ASchema, AAction, and xwentity abstracts), use **`*._data`** of type **XWData** as the engine. All IData operations MUST delegate to `_data`; do **not** re-implement from scratch. xwschema and xwaction have been updated so that ISchema extends IData, IAction extends IData, and ASchema/AAction (and XWSchema concrete) use `_data` and delegate.

**Relationship to xwObject**

- **XWObject** is defined in **xwsystem.shared** (very basic).
- XWEntity **extends XWObject**.
- Where XWData overrides something in XWObject, **xwEntity follows XWData** (XWData is superior for that behavior).

**Consumers**

- xwentity will be used and reused in: **xwmodels**, **xwapi**, **xwauth**, **xwstorage**, **xwbase**, and others.

---

**Resolved (29-Jan-2026)**

| Question | Answer |
|----------|--------|
| xw_data / engine | xwdata = lib, XWData = class used as engine (like XWSchema). |
| Cache location | Static on XWEntity. |
| XWData API | No extra constructor params; XWSchema as sub-node; ISchema extends IData, IAction extends IData; XWData accepts child `list[IData]`. |
| xwObject source | xwsystem.shared, very basic. |
| Children type | XWData accepts a child that is `list[IData]`. |

**Implemented (29-Jan-2026)**

- **xwschema:** ISchema now extends IData (xwdata.contracts); ASchema has `_data: Optional[XWData]` and delegates all IData methods to `_data`; XWSchema sets `_data = _schema_data` (or from native). No re-implementation — full delegation.
- **xwaction:** IAction now extends IData; AAction has `_data: XWData` (from_native of action metadata) and delegates to_native, get_metadata, get_format, get/set/delete/exists/serialize/save/merge/transform/to_file/to_format to `_data`. No re-implementation.

**Follow-up questions (optional)**

- **Shape of `list[IData]`:** Is it one flat list (e.g. schema node, then action nodes, then data node), or nested (e.g. first child = schema IData, second = container for actions, third = data)? How many slots and in what order?
- **Static cache key:** What is the cache key — `(schema, tuple(actions))` or hashes? What is stored — a prebuilt XWData shape, or a reference to reuse?

---

## Idea Archive

*(Completed or rejected ideas with rationale.)*

---

*See GUIDE_12_IDEA.md for capture and evaluation process.*
