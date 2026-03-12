# Benchmark Reference — xwentity

**Library:** exonware-xwentity  
**Last Updated:** 08-Feb-2026

Performance SLAs and NFR targets (output of GUIDE_54_BENCH).

---

## Scope

- Entity creation and validation throughput.
- Serialization/deserialization (XWJSON, etc.).
- Cache hit/miss and memory footprint (when enabled).

---

## Baselines

*(To be populated from benchmark runs.)*

When benchmark runs exist: add result files (e.g. `BENCH_*.md`) under `docs/logs/benchmarks/` and summarize key numbers here per GUIDE_54_BENCH. Until then, this section remains empty.

---

## Commands

```bash
# Run tests including performance-related
pytest tests/0.core/ -v -k performance
```

---

*See GUIDE_54_BENCH.md for benchmarking standards. Logs: docs/logs/benchmarks/.*
