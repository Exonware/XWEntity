# xwentity tests

Run tests:

```bash
pytest
# or
python -m pytest tests -v --tb=short
```

## Let xwlazy auto-install optional deps

Tests import `exonware.xwentity`, which pulls in `exonware.xwsystem`. xwsystem uses **xwlazy** so that missing optional packages (e.g. `msgspec`, `orjson`, `json5`, `PyYAML`) can be **auto-installed on first import**.

If your venv is **PEP 668 externally-managed** (most `python -m venv` venvs are), xwlazy skips auto-install by default. To allow auto-install in that case (e.g. for dev/test), set:

```bash
set XWLAZY_ALLOW_EXTERNALLY_MANAGED=1
pytest
```

(On Unix/macOS use `export XWLAZY_ALLOW_EXTERNALLY_MANAGED=1`.)

Optional: set `XWLAZY_VERBOSE=1` to see when xwlazy installs a package.

If you prefer not to use auto-install, install the optional deps yourself (e.g. `pip install -e ".[test]"` or install the specific missing module when you see `ModuleNotFoundError`).
