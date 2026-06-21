"""Tests for config_validator — types, bounds, choices, patterns, required, unknown keys, recursion."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config_validator as cv  # noqa: E402

SCHEMA = {
    "name": {"type": "str", "min": 1, "max": 32},
    "port": {"type": "int", "min": 1, "max": 65535},
    "env": {"type": "str", "choices": ["dev", "prod"]},
    "ratio": {"type": "float", "min": 0.0, "max": 1.0},
    "debug": {"type": "bool", "required": False, "default": False},
    "host": {"type": "str", "pattern": r"[\w.\-]+", "required": False, "default": "localhost"},
    "tags": {"type": "list", "items": {"type": "str"}, "required": False, "default": []},
}


def _ok(cfg):
    return cv.validate(cfg, SCHEMA)


def test_valid_config_passes_and_fills_defaults():
    ok, errs, norm = _ok({"name": "app", "port": 8080, "env": "dev", "ratio": 0.5})
    assert ok and errs == []
    assert norm["debug"] is False and norm["host"] == "localhost" and norm["tags"] == []


def test_required_missing_flagged():
    ok, errs, _ = _ok({"port": 80, "env": "dev", "ratio": 0.1})
    assert not ok and any("name" in e and "required" in e for e in errs)


def test_type_mismatch():
    ok, errs, _ = _ok({"name": "a", "port": "80", "env": "dev", "ratio": 0.1})
    assert not ok and any("port" in e and "expected int" in e for e in errs)


def test_bool_not_accepted_as_int():
    ok, errs, _ = _ok({"name": "a", "port": True, "env": "dev", "ratio": 0.1})
    assert not ok and any("port" in e and "bool" in e for e in errs)


def test_numeric_bounds():
    ok, errs, _ = _ok({"name": "a", "port": 70000, "env": "dev", "ratio": 0.1})
    assert not ok and any("max" in e for e in errs)


def test_string_length_bounds():
    ok, errs, _ = _ok({"name": "", "port": 80, "env": "dev", "ratio": 0.1})
    assert not ok and any("name" in e and "min" in e for e in errs)


def test_choices_enforced():
    ok, errs, _ = _ok({"name": "a", "port": 80, "env": "staging", "ratio": 0.1})
    assert not ok and any("env" in e and "not in" in e for e in errs)


def test_pattern_enforced():
    ok, errs, _ = _ok({"name": "a", "port": 80, "env": "dev", "ratio": 0.1, "host": "bad host!"})
    assert not ok and any("host" in e and "match" in e for e in errs)


def test_unknown_key_flagged():
    ok, errs, _ = _ok({"name": "a", "port": 80, "env": "dev", "ratio": 0.1, "extra": 1})
    assert not ok and any("extra" in e and "unknown" in e for e in errs)


def test_list_item_recursion():
    ok, errs, _ = _ok({"name": "a", "port": 80, "env": "dev", "ratio": 0.1, "tags": ["x", 5]})
    assert not ok and any("tags[1]" in e for e in errs)


def test_non_dict_config():
    ok, errs, _ = cv.validate([1, 2], SCHEMA)
    assert not ok and "object" in errs[0]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
