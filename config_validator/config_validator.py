#!/usr/bin/env python3
"""
config_validator — validate a generated config against a lightweight schema, with clear errors.

For a config-generator: after producing a config (JSON/dict), validate it BEFORE writing/using it, so
bad configs fail fast with a precise, human-readable reason instead of a runtime crash later. Stdlib only,
zero deps. The schema is a plain dict — no external schema library.

Schema fields (per key):
  type      — "str"|"int"|"float"|"bool"|"list"|"dict"  (or a tuple of allowed types)
  required  — bool (default True)
  default   — value to fill when missing+optional
  min/max   — numeric bounds (ints/floats) or length bounds (str/list)
  choices   — allowed values
  pattern   — regex the string must fully match
  items     — schema for each list element (recursion)

Usage:
  from config_validator import validate
  ok, errors, normalized = validate(cfg, SCHEMA)
  python3 config_validator.py config.json schema.json    # CLI: exit 0 valid, 1 invalid
"""
from __future__ import annotations
import json, re, sys

_TYPES = {"str": str, "int": int, "float": (int, float), "bool": bool, "list": list, "dict": dict}


def _check(key: str, val, rule: dict, errors: list):
    types = rule.get("type")
    if types:
        py = tuple(t for name in ([types] if isinstance(types, str) else types) for t in
                   ((_TYPES[name],) if isinstance(_TYPES.get(name), type) else _TYPES.get(name, ())))
        # bool is a subclass of int — guard against silent acceptance
        if "int" in ([types] if isinstance(types, str) else types) and isinstance(val, bool):
            errors.append(f"{key}: expected int, got bool"); return
        if py and not isinstance(val, py):
            errors.append(f"{key}: expected {types}, got {type(val).__name__}"); return
    if "choices" in rule and val not in rule["choices"]:
        errors.append(f"{key}: {val!r} not in {rule['choices']}")
    if isinstance(val, (int, float)) and not isinstance(val, bool):
        if "min" in rule and val < rule["min"]:
            errors.append(f"{key}: {val} < min {rule['min']}")
        if "max" in rule and val > rule["max"]:
            errors.append(f"{key}: {val} > max {rule['max']}")
    if isinstance(val, (str, list)):
        if "min" in rule and len(val) < rule["min"]:
            errors.append(f"{key}: length {len(val)} < min {rule['min']}")
        if "max" in rule and len(val) > rule["max"]:
            errors.append(f"{key}: length {len(val)} > max {rule['max']}")
    if isinstance(val, str) and "pattern" in rule and not re.fullmatch(rule["pattern"], val):
        errors.append(f"{key}: {val!r} does not match /{rule['pattern']}/")
    if isinstance(val, list) and "items" in rule:
        for i, el in enumerate(val):
            _check(f"{key}[{i}]", el, rule["items"], errors)


def validate(cfg: dict, schema: dict) -> tuple[bool, list, dict]:
    """Return (ok, errors, normalized). normalized fills optional defaults. Unknown keys are flagged."""
    errors: list = []
    if not isinstance(cfg, dict):
        return False, [f"config must be an object, got {type(cfg).__name__}"], {}
    out = dict(cfg)
    for key, rule in schema.items():
        if key not in cfg:
            if rule.get("required", True):
                errors.append(f"{key}: required field missing")
            elif "default" in rule:
                out[key] = rule["default"]
            continue
        _check(key, cfg[key], rule, errors)
    for key in cfg:
        if key not in schema:
            errors.append(f"{key}: unknown field (not in schema)")
    return (not errors), errors, out


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print("usage: config_validator.py <config.json> <schema.json>"); return 2
    cfg = json.load(open(argv[0]))
    schema = json.load(open(argv[1]))
    ok, errors, _ = validate(cfg, schema)
    if ok:
        print("✓ config valid")
        return 0
    print("✗ config invalid:")
    for e in errors:
        print(f"  - {e}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
