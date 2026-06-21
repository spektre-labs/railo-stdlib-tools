"""Tests for module_validator — AST-only static checks, no imports, tmp packages."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import module_validator as mv  # noqa: E402


def _w(p: Path, src: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src)
    return p


def test_clean_package(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "a.py", "def f():\n    return 1\n")
    r = mv.validate_package(tmp_path)
    assert r["ok"] is True and r["n_issues"] == 0


def test_syntax_error_caught(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "bad.py", "def f(:\n  pass\n")
    r = mv.validate_package(tmp_path)
    assert not r["ok"] and any(i["kind"] == "syntax_error" for i in r["issues"])


def test_missing_init_flagged(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "sub" / "m.py", "x = 1\n")     # sub/ has .py but no __init__.py
    r = mv.validate_package(tmp_path)
    assert any(i["kind"] == "missing_init" for i in r["issues"])


def test_all_missing_export(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "m.py", "__all__ = ['f', 'ghost']\n\ndef f():\n    pass\n")
    r = mv.validate_package(tmp_path)
    assert any(i["kind"] == "all_missing" and "ghost" in i["detail"] for i in r["issues"])


def test_all_present_export_ok(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "m.py", "__all__ = ['f']\n\ndef f():\n    pass\n")
    r = mv.validate_package(tmp_path)
    assert not any(i["kind"] == "all_missing" for i in r["issues"])


def test_todo_density(tmp_path):
    _w(tmp_path / "__init__.py", "")
    _w(tmp_path / "m.py", "\n".join(f"# TODO {i}" for i in range(6)) + "\nx=1\n")
    r = mv.validate_package(tmp_path)
    assert any(i["kind"] == "todo_density" for i in r["issues"])


def test_no_python_files(tmp_path):
    (tmp_path / "readme.txt").write_text("hi")
    r = mv.validate_package(tmp_path)
    assert not r["ok"] and r["issues"][0]["kind"] == "no_python"


def test_single_file_target(tmp_path):
    f = _w(tmp_path / "solo.py", "def g():\n    return 2\n")
    r = mv.validate_package(f)
    assert r["ok"] is True


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
