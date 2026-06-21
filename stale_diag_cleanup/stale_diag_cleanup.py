#!/usr/bin/env python3
"""
stale_diag_cleanup — report (and optionally remove) stale diagnostic chunks. DRY-RUN by default.

Spec (bounty): diagnostic bundles live under `diagnostic/`; interrupted runs leave stale partial
`.logd` chunks + orphan metadata that make review dirs noisy. This adds a dry-run cleanup mode that
REPORTS stale chunks/metadata without deleting anything — deletion happens only with an explicit
`--apply`, and even then archives rather than hard-deletes (reversible). Stdlib only.

"Stale" = a chunk whose run is no longer active:
  · a `.logd` chunk older than --max-age-hours with no matching `.done` marker, OR
  · `.part` / `.tmp` partials from an interrupted write, OR
  · metadata (`*.meta.json`) with no surviving `.logd` sibling (orphan).

Usage:
  python3 stale_diag_cleanup.py                       # dry-run report on ./diagnostic
  python3 stale_diag_cleanup.py --dir diagnostic --max-age-hours 6
  python3 stale_diag_cleanup.py --apply               # archive stale files (reversible), prints what moved
  python3 stale_diag_cleanup.py --json
"""
from __future__ import annotations
import argparse, json, sys, time, shutil
from pathlib import Path


def find_stale(root: Path, max_age_hours: float, now: float | None = None) -> list[dict]:
    now = now if now is not None else time.time()
    cutoff = now - max_age_hours * 3600
    stale: list[dict] = []
    if not root.exists():
        return stale
    logds = {p.with_suffix("").name: p for p in root.rglob("*.logd")}
    done = {p.with_suffix("").name for p in root.rglob("*.done")}
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        name, suf = p.name, p.suffix
        age_h = round((now - p.stat().st_mtime) / 3600, 2)
        reason = None
        if suf in (".part", ".tmp"):
            reason = "interrupted partial write"
        elif suf == ".logd" and p.stat().st_mtime < cutoff and p.with_suffix("").name not in done:
            reason = f"stale chunk {age_h}h old, no .done marker"
        elif name.endswith(".meta.json"):
            base = name[: -len(".meta.json")]
            if base not in logds:
                reason = "orphan metadata (no .logd sibling)"
        if reason:
            stale.append({"path": str(p), "size": p.stat().st_size, "age_hours": age_h, "reason": reason})
    return stale


def report(root: Path, max_age_hours: float, apply: bool, now: float | None = None) -> dict:
    stale = find_stale(root, max_age_hours, now)
    total = sum(s["size"] for s in stale)
    moved: list[str] = []
    if apply and stale:
        archive = root / ".stale_archive" / time.strftime("%Y%m%d-%H%M%S", time.gmtime(now or time.time()))
        archive.mkdir(parents=True, exist_ok=True)
        for s in stale:
            src = Path(s["path"])
            try:
                dest = archive / src.name
                shutil.move(str(src), str(dest))   # ARCHIVE, not delete — reversible
                moved.append(str(dest))
            except Exception as e:
                s["error"] = str(e)[:80]
    return {"dir": str(root), "max_age_hours": max_age_hours, "dry_run": not apply,
            "n_stale": len(stale), "bytes": total, "stale": stale,
            "archived_to": moved or None,
            "note": ("DRY-RUN — nothing changed. Re-run with --apply to ARCHIVE (not delete) these."
                     if not apply else f"archived {len(moved)} files (reversible; under .stale_archive/)")}


def render(r: dict) -> str:
    head = "DRY-RUN (no changes)" if r["dry_run"] else f"APPLIED — archived {r['n_stale']}"
    L = [f"🧹 stale-diag cleanup · {r['dir']} · {head} · {r['n_stale']} stale · {r['bytes']} bytes"]
    for s in r["stale"][:40]:
        L.append(f"  · {s['path']}  [{s['reason']}]")
    L.append(f"  → {r['note']}")
    return "\n".join(L)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Report/clean stale diagnostic chunks (dry-run by default).")
    ap.add_argument("--dir", default="diagnostic")
    ap.add_argument("--max-age-hours", type=float, default=6.0)
    ap.add_argument("--apply", action="store_true", help="archive stale files (default: dry-run report only)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    r = report(Path(a.dir), a.max_age_hours, a.apply)
    print(json.dumps(r, indent=2) if a.json else render(r))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
