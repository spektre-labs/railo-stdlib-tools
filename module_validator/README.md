# module_validator

Static health check for a Python package — **no imports, no side effects** (pure AST + filesystem).
Stdlib, zero deps. Flags: syntax errors, package dirs missing `__init__.py`, `__all__` entries that
aren't defined, and high TODO/FIXME density.

```bash
python3 module_validator.py path/to/package          # report (exit 0 clean, 1 issues)
python3 module_validator.py path/to/package --json
```
Test: `python3 -m pytest test_module_validator.py -q` (8 tests, tmp packages).
Why AST not import: importing runs side effects and needs the deps installed; validation must be safe & offline.
