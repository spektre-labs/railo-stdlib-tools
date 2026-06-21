"""Tests for todo_audit — marker grammar, priority ranking, grouping. Tmp trees, offline."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import todo_audit as ta  # noqa: E402


def _w(p: Path, src: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(src)


def test_finds_basic_markers(tmp_path):
    _w(tmp_path / "a.py", "# TODO: do the thing\nx = 1  # FIXME broken\n")
    items = ta.scan(tmp_path)
    tags = {i["tag"] for i in items}
    assert "TODO" in tags and "FIXME" in tags


def test_parses_owner_and_priority(tmp_path):
    _w(tmp_path / "a.py", "# TODO(alice)[p1]: ship it\n")
    i = ta.scan(tmp_path)[0]
    assert i["owner"] == "alice" and i["priority"] == "p1" and i["rank"] == 1
    assert i["note"] == "ship it"


def test_priority_orders_report(tmp_path):
    _w(tmp_path / "a.py", "# TODO[low]: later\n# TODO[high]: now\n")
    items = ta.scan(tmp_path)
    assert items[0]["priority"] == "high" and items[-1]["priority"] == "low"


def test_skips_ignored_dirs(tmp_path):
    _w(tmp_path / "node_modules" / "x.js", "// TODO: ignore me\n")
    _w(tmp_path / "src.py", "# TODO: keep me\n")
    notes = [i["note"] for i in ta.scan(tmp_path)]
    assert "keep me" in notes and "ignore me" not in notes


def test_skips_binary_and_unknown_ext(tmp_path):
    _w(tmp_path / "data.bin", "TODO: not scanned (no text ext)\n")
    assert ta.scan(tmp_path) == []


def test_report_aggregates_by_tag(tmp_path):
    _w(tmp_path / "a.py", "# TODO: 1\n# TODO: 2\n# FIXME: 3\n")
    r = ta.report(tmp_path)
    assert r["total"] == 3 and r["by_tag"]["TODO"] == 2 and r["by_tag"]["FIXME"] == 1


def test_markdown_render(tmp_path):
    _w(tmp_path / "a.py", "# FIXME(bob)[p0]: urgent\n# TODO: someday\n")
    md = ta.render_md(ta.report(tmp_path))
    assert "# TODO audit" in md and "## Prioritized" in md and "FIXME(bob)[p0]" in md


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
