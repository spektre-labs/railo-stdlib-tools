# config_validator

Validate a generated config against a lightweight dict-schema, with precise human errors. Stdlib, zero deps.

```python
from config_validator import validate
ok, errors, normalized = validate(cfg, SCHEMA)   # normalized fills optional defaults
```

Schema per key: `type` (str/int/float/bool/list/dict or tuple), `required`, `default`, `min`/`max`
(numeric bound or str/list length), `choices`, `pattern` (full-match regex), `items` (per-list-element schema).
Flags unknown keys; rejects `bool` smuggled in as `int`.

CLI: `python3 config_validator.py config.json schema.json` → exit 0 valid / 1 invalid.
Test: `python3 -m pytest test_config_validator.py -q` (11 tests, offline).
