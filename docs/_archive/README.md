# Archive — xwentity

**Purpose:** Temporary holding area for deprecated or legacy docs before disposition. Not for long-term storage.

---

## Process

1. **Move** obsolete content here only when preparing to retire it.
2. **Review** each file: identify value (requirements, architecture, decisions, evidence).
3. **Extract value** into the right place:
   - Requirements / vision / milestones → REF_22_PROJECT, REF_12_IDEA, or `docs/logs/project/`
   - Architecture / layout → REF_13_ARCH
   - Reviews / compliance → `docs/logs/reviews/` (REVIEW_*.md)
   - Change history / migration → `docs/changes/` or `docs/logs/SUMMARY_CHANGE.md`
   - Plans → `docs/logs/plans/` or SUMMARY_PLAN
   - Test/bench evidence → `docs/logs/tests/`, `docs/logs/benchmarks/`
4. **Delete** the file from _archive after value is captured. Do not leave substantive content here.

When empty, this folder should contain only `.gitkeep` and this README.

---

*Disposition review: [logs/reviews/REVIEW_20260208_ARCHIVE_DISPOSITION.md](../logs/reviews/REVIEW_20260208_ARCHIVE_DISPOSITION.md).*
