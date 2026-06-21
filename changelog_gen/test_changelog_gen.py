"""Tests for changelog_gen — deterministic, offline (synthetic commit dicts, no real git needed)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import changelog_gen as cg  # noqa: E402


def _c(typ, desc, hash="abc1234", scope=None, breaking=False, date="2026-01-01"):
    return {"type": typ, "scope": scope, "breaking": breaking, "desc": desc,
            "hash": hash, "short": hash[:7], "author": "t", "date": date}


def test_conventional_commit_parsing(monkeypatch):
    monkeypatch.setattr(cg, "_git", lambda a, r: "\x1f".join(
        ["H1", "h1", "feat(api): add x", "t", "2026-01-01"]))
    monkeypatch.setattr(cg, "_tag_at", lambda r: {})
    c = cg.parse_commits(".", None)[0]
    assert c["type"] == "feat" and c["scope"] == "api" and c["desc"] == "add x"


def test_breaking_change_detected(monkeypatch):
    monkeypatch.setattr(cg, "_git", lambda a, r: "\x1f".join(["H", "h", "feat!: drop v1", "t", "2026-01-01"]))
    monkeypatch.setattr(cg, "_tag_at", lambda r: {})
    assert cg.parse_commits(".", None)[0]["breaking"] is True


def test_unstructured_commit_falls_to_other(monkeypatch):
    monkeypatch.setattr(cg, "_git", lambda a, r: "\x1f".join(["H", "h", "just did stuff", "t", "2026-01-01"]))
    monkeypatch.setattr(cg, "_tag_at", lambda r: {})
    assert cg.parse_commits(".", None)[0]["type"] == "other"


def test_build_groups_by_type_and_release(monkeypatch):
    commits = [_c("perf", "cache", "p1"), _c("feat", "ep", "f1", scope="api"),
               _c("fix", "bug", "x1"), _c("feat", "old", "b1", breaking=True)]
    # tag b1 → splits a release block
    monkeypatch.setattr(cg, "_tag_at", lambda r: {"b1": "v1.0.0"})
    md = cg.build_changelog(commits, ".")
    assert "## Unreleased" in md and "## v1.0.0" in md
    assert "### Performance" in md and "### Added" in md and "### Fixed" in md
    assert "⚠ BREAKING CHANGES" in md
    assert "**api:** ep" in md          # scope rendered
    assert "(`f1`)" in md               # short hash rendered


def test_empty_history_still_valid(monkeypatch):
    monkeypatch.setattr(cg, "_tag_at", lambda r: {})
    md = cg.build_changelog([], ".")
    assert md.startswith("# Changelog")


def test_section_order_is_stable():
    # Added before Fixed before Performance, etc. — deterministic heading order
    keys = list(cg.SECTIONS.values())
    assert keys.index("Added") < keys.index("Fixed") < keys.index("Performance")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
