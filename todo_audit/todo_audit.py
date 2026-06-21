#!/usr/bin/env python3
"""
todo_audit — scan a source tree for TODO/FIXME/HACK/XXX markers → a structured, prioritized report.

Walks files, extracts each marker with file:line, tag, optional `(owner)` and `[priority]`, and the note.
Groups by tag, ranks by priority, and emits Markdown or JSON. Honors .gitignore-style skip dirs. Stdlib only.

Marker grammar (flexible):  TODO(owner)[p1]: finish the thing   ·   # FIXME: broken on empty input

Usage:
  python3 todo_audit.py                       # scan . → markdown to stdout
  python3 todo_audit.py --dir src --json
  python3 todo_audit.py -o TODO_AUDIT.md
"""
from __future__ import annotations
import argparse, json, re, sys
from pathlib import Path
from collections import Counter, defaultdict

TAGS = ("TODO", "FIXME", "HACK", "XXX", "BUG", "OPTIMIZE")
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build", ".mypy_cache", ".pytest_cache"}
TEXT_EXT = {".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java", ".c", ".h", ".cpp", ".rb", ".sh",
            ".md", ".txt", ".yaml", ".yml", ".toml", ".sql"}
_RX = re.compile(
    r"\b(?P<tag>" + "|".join(TAGS) + r")\b"
    r"(?:\((?P<owner>[^)]+)\))?"
    r"(?:\[(?P<prio>[pP]?\d|high|med|low)\])?"
    r"\s*:?\s*(?P<note>.*)")
_PRIO_RANK = {"p0": 0, "0": 0, "high": 0, "p1": 1, "1": 1, "med": 2, "p2": 2, "2": 2, "low": 3, "p3": 3, "3": 3}


def scan(root: Path) -> list[dict]:
    found: list[dict] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix not in TEXT_EXT:
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        try:
            lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception:
            continue
        for n, line in enumerate(lines, 1):
            m = _RX.search(line)
            if m:
                prio = (m.group("prio") or "").lower()
                found.append({"file": str(p), "line": n, "tag": m.group("tag"),
                              "owner": m.group("owner"), "priority": prio or None,
                              "rank": _PRIO_RANK.get(prio, 4), "note": m.group("note").strip()[:200]})
    found.sort(key=lambda x: (x["rank"], x["file"], x["line"]))
    return found


def report(root: Path) -> dict:
    items = scan(root)
    by_tag = Counter(i["tag"] for i in items)
    by_owner = Counter(i["owner"] for i in items if i["owner"])
    prioritized = [i for i in items if i["rank"] < 4]
    return {"dir": str(root), "total": len(items), "by_tag": dict(by_tag),
            "by_owner": dict(by_owner), "n_prioritized": len(prioritized), "items": items}


def render_md(r: dict) -> str:
    L = [f"# TODO audit — {r['dir']}", "",
         f"**{r['total']} markers** · " + " · ".join(f"{k} {v}" for k, v in sorted(r["by_tag"].items())), ""]
    if r["n_prioritized"]:
        L += ["## Prioritized", ""]
        for i in r["items"]:
            if i["rank"] < 4:
                tag = f"{i['tag']}" + (f"({i['owner']})" if i["owner"] else "") + (f"[{i['priority']}]" if i["priority"] else "")
                L.append(f"- **{tag}** `{i['file']}:{i['line']}` — {i['note']}")
        L.append("")
    L += ["## All markers by tag", ""]
    by_file = defaultdict(list)
    for i in r["items"]:
        by_file[i["tag"]].append(i)
    for tag in sorted(by_file):
        L.append(f"### {tag} ({len(by_file[tag])})")
        for i in by_file[tag]:
            L.append(f"- `{i['file']}:{i['line']}` — {i['note']}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Audit TODO/FIXME markers into a structured report.")
    ap.add_argument("--dir", default=".")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-o", "--output", default=None)
    a = ap.parse_args(argv)
    r = report(Path(a.dir))
    out = json.dumps(r, indent=2) if a.json else render_md(r)
    if a.output:
        Path(a.output).write_text(out); print(f"wrote {a.output} ({r['total']} markers)")
    else:
        sys.stdout.write(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
