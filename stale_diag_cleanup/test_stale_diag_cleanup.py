"""Tests for stale_diag_cleanup — dry-run safety + correct stale detection. Uses tmp dirs, no network."""
import sys, time, json
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stale_diag_cleanup as sdc  # noqa: E402


def _mk(p: Path, age_hours=0.0, content="x"):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    t = time.time() - age_hours * 3600
    import os
    os.utime(p, (t, t))
    return p


def test_detects_stale_chunk_without_done(tmp_path):
    _mk(tmp_path / "run1.logd", age_hours=10)          # old, no .done → stale
    stale = sdc.find_stale(tmp_path, max_age_hours=6)
    assert any("run1.logd" in s["path"] for s in stale)


def test_fresh_chunk_is_not_stale(tmp_path):
    _mk(tmp_path / "run2.logd", age_hours=1)           # recent → keep
    assert sdc.find_stale(tmp_path, max_age_hours=6) == []


def test_done_marker_protects_chunk(tmp_path):
    _mk(tmp_path / "run3.logd", age_hours=10)
    _mk(tmp_path / "run3.done", age_hours=10)           # completed → keep even if old
    assert not any("run3.logd" in s["path"] for s in sdc.find_stale(tmp_path, 6))


def test_partial_writes_always_stale(tmp_path):
    _mk(tmp_path / "a.part", age_hours=0.1)
    _mk(tmp_path / "b.tmp", age_hours=0.1)
    reasons = {Path(s["path"]).name: s["reason"] for s in sdc.find_stale(tmp_path, 6)}
    assert "a.part" in reasons and "b.tmp" in reasons


def test_orphan_metadata_detected(tmp_path):
    _mk(tmp_path / "x.meta.json", age_hours=0.1)        # no x.logd → orphan
    assert any("orphan" in s["reason"] for s in sdc.find_stale(tmp_path, 6))


def test_metadata_with_sibling_is_kept(tmp_path):
    _mk(tmp_path / "y.logd", age_hours=0.1)
    _mk(tmp_path / "y.meta.json", age_hours=0.1)
    assert not any("y.meta.json" in s["path"] for s in sdc.find_stale(tmp_path, 6))


def test_dry_run_changes_nothing(tmp_path):
    f = _mk(tmp_path / "old.logd", age_hours=10)
    r = sdc.report(tmp_path, 6, apply=False)
    assert r["dry_run"] is True and r["n_stale"] == 1
    assert f.exists()                                    # untouched


def test_apply_archives_not_deletes(tmp_path):
    f = _mk(tmp_path / "old.logd", age_hours=10)
    r = sdc.report(tmp_path, 6, apply=True)
    assert not f.exists()                                # moved out of the review dir
    assert r["archived_to"] and Path(r["archived_to"][0]).exists()   # but recoverable in archive


def test_missing_dir_is_safe(tmp_path):
    assert sdc.find_stale(tmp_path / "nope", 6) == []


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
