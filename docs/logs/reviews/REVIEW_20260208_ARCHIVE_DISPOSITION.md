# Review: Archive disposition — xwentity

**Date:** 20260208  
**Artifact type:** Archive review  
**Scope:** `docs/_archive/` and any legacy content; value extracted to REFs or logs per GUIDE_41_DOCS.

---

## Summary

**Pass.** Archive reviewed systematically. No substantive files were present in `_archive`; all added value is already in REFs or logs. Disposition documented below.

---

## What was in `docs/_archive/`

| Item | Type | Disposition |
|------|------|-------------|
| `.gitkeep` | Placeholder | Retained so directory exists for future use. |

**No other files.** The folder contained only the placeholder.

---

## Value already outside _archive (no duplication)

- **Migration / refactor:** Value from any previously archived repo-root or legacy docs was already captured in `docs/changes/MIGRATION_XWENTITY_REFACTOR.md` (see note there: *"Value captured from repo-root docs; original archived in docs/_archive/."*). That document is the single source for XWObject merge, xwentity→xwmodels rename, and migration steps. REF_22_PROJECT now references it under "Related documentation" so the migration plan is traceable from the requirements doc.

---

## Actions taken

1. **Review log:** This file (`REVIEW_20260208_ARCHIVE_DISPOSITION.md`) created in `docs/logs/reviews/` to record the archive review and outcome.
2. **REF_22:** Added pointer to `docs/changes/MIGRATION_XWENTITY_REFACTOR.md` for planned merge/rename so migration lives in the requirements view.
3. **SUMMARY_PROJECT:** Corrected link from `REF_PROJECT.md` to `REF_22_PROJECT.md`.
4. **`_archive/README.md`:** Added so the archive has a clear purpose and process: content placed here must be reviewed, value extracted into REFs or logs, then the file removed; do not leave substantive content in _archive.

---

## Convention going forward

- **Best location for “archived” content:** Do not keep substantive docs in `_archive`. Use _archive only as a temporary holding area: review each file, extract value into the appropriate REF (REF_12, REF_22, REF_13, etc.) or into logs (reviews, changes, plans, benchmarks, tests), then **delete** the file from _archive. Keep only `.gitkeep` (and this README) when the folder is empty of content.

---

*See REF_35_REVIEW.md for project review summary. Archive purpose: docs/_archive/README.md.*
