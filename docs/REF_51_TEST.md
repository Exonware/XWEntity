# Test Status — xwentity

**Library:** exonware-xwentity  
**Last Test Run:** 29-Jan-2026  
**Test Framework:** pytest + hierarchical runners (0.core, 1.unit, 2.integration)  
**Overall Status:** See latest run in docs/logs/tests/

---

## Test Summary

| Layer | Description | Status |
|-------|-------------|--------|
| **0.core** | Fast, high-value checks | Implemented |
| **1.unit** | Component isolation tests | Implemented |
| **2.integration** | Cross-module scenarios | Implemented |
| **3.advance** | Excellence validation | Optional until v1.0 |

Test evidence: [docs/logs/tests/](logs/tests/) (TEST_*.md, INDEX.md).  
Test execution log: [docs/logs/SUMMARY_TEST.md](logs/SUMMARY_TEST.md).

---

## Running Tests

**Recommended:** use the hierarchical runner (single entry point per GUIDE_51_TEST):

```bash
# Run all layers (0.core → 1.unit → 2.integration)
python tests/runner.py

# Run a single layer via runner
python tests/runner.py --core         # Layer 0 only
python tests/runner.py --unit         # Layer 1 only
python tests/runner.py --integration  # Layer 2 only
```

**Alternative:** run layers directly with pytest:

```bash
pytest tests/0.core/ -v
pytest tests/1.unit/ -v
pytest tests/2.integration/ -v
```

Layer **3.advance** is optional until v1.0; no `tests/3.advance/` directory yet. When added, document in this REF and in the runner.

---

*See GUIDE_51_TEST.md for test standards. Last Updated: 08-Feb-2026*
