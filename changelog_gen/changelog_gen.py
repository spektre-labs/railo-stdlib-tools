#!/usr/bin/env python3
"""
changelog_gen — generate a structured CHANGELOG.md from git history. Stdlib only, zero deps.

Groups commits by Conventional-Commit type (feat/fix/perf/refactor/docs/test/chore/...), under the
tag (or `Unreleased`) they belong to, in Keep-a-Changelog form. Deterministic, offline, fast.

Usage:
  python3 changelog_gen.py                      # whole history → stdout
  python3 changelog_gen.py --since v1.2.0       # only commits after a ref
  python3 changelog_gen.py --repo /path -o CHANGELOG.md
  python3 changelog_gen.py --unreleased-name "Unreleased"
"""
from __future__ import annotations
import argparse, subprocess, re, sys
from collections import OrderedDict

# Conventional-Commit type → CHANGELOG section heading (Keep a Changelog flavored).
SECTIONS = OrderedDict([
    ("feat", "Added"), ("fix", "Fixed"), ("perf", "Performance"),
    ("refactor", "Changed"), ("revert", "Reverted"), ("docs", "Documentation"),
    ("test", "Tests"), ("build", "Build"), ("ci", "CI"), ("chore", "Chores"),
])
_CC = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<bang>!)?:\s*(?P<desc>.+)$")
SEP = "\x1f"   # unit separator — safe field delimiter for git format


def _git(args: list[str], repo: str) -> str:
    out = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise RuntimeError(out.stderr.strip() or f"git {' '.join(args)} failed")
    return out.stdout


def _tag_at(repo: str) -> dict:
    """Map commit-hash → tag name, for commits that are tag targets."""
    m = {}
    try:
        for line in _git(["tag", "--format=%(objectname)%(if)%(*objectname)%(then) %(*objectname)%(end)" + SEP + "%(refname:short)"], repo).splitlines():
            if SEP not in line:
                continue
            objs, name = line.split(SEP, 1)
            for h in objs.split():
                m[h] = name.strip()
    except Exception:
        pass
    return m


def parse_commits(repo: str, since: str | None) -> list[dict]:
    rng = [f"{since}..HEAD"] if since else []
    fmt = SEP.join(["%H", "%h", "%s", "%an", "%ad"])
    raw = _git(["log", "--no-merges", f"--pretty=format:{fmt}", "--date=short", *rng], repo)
    commits = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        h, short, subject, author, date = (line.split(SEP) + [""] * 5)[:5]
        m = _CC.match(subject)
        if m:
            typ = m.group("type").lower()
            entry = {"type": typ, "scope": m.group("scope"), "breaking": bool(m.group("bang")),
                     "desc": m.group("desc").strip()}
        else:
            entry = {"type": "other", "scope": None, "breaking": False, "desc": subject.strip()}
        entry.update({"hash": h, "short": short, "author": author, "date": date})
        commits.append(entry)
    return commits


def build_changelog(commits: list[dict], repo: str, unreleased="Unreleased") -> str:
    tags = _tag_at(repo)
    # walk commits (newest→oldest); open a release block whenever we hit a tagged commit
    releases: "OrderedDict[str, list]" = OrderedDict()
    cur = unreleased
    releases[cur] = []
    for c in commits:
        if c["hash"] in tags:
            cur = tags[c["hash"]]
            releases.setdefault(cur, [])
        releases[cur].append(c)
    lines = ["# Changelog", "",
             "All notable changes to this project, generated from git history.",
             "Format: [Keep a Changelog](https://keepachangelog.com); types: [Conventional Commits](https://www.conventionalcommits.org).",
             ""]
    for rel, items in releases.items():
        if not items:
            continue
        date = items[0]["date"]
        lines.append(f"## {rel}" + (f" — {date}" if rel != unreleased and date else ""))
        breaking = [c for c in items if c["breaking"]]
        if breaking:
            lines.append("\n### ⚠ BREAKING CHANGES")
            for c in breaking:
                lines.append(f"- {_fmt(c)}")
        for typ, heading in SECTIONS.items():
            group = [c for c in items if c["type"] == typ and not c["breaking"]]
            if group:
                lines.append(f"\n### {heading}")
                for c in group:
                    lines.append(f"- {_fmt(c)}")
        other = [c for c in items if c["type"] == "other" and not c["breaking"]]
        if other:
            lines.append("\n### Other")
            for c in other:
                lines.append(f"- {_fmt(c)}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _fmt(c: dict) -> str:
    scope = f"**{c['scope']}:** " if c["scope"] else ""
    return f"{scope}{c['desc']} (`{c['short']}`)"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Generate a structured CHANGELOG.md from git history.")
    ap.add_argument("--repo", default=".")
    ap.add_argument("--since", default=None, help="only commits after this ref/tag")
    ap.add_argument("--unreleased-name", default="Unreleased")
    ap.add_argument("-o", "--output", default=None, help="write to file instead of stdout")
    a = ap.parse_args(argv)
    commits = parse_commits(a.repo, a.since)
    md = build_changelog(commits, a.repo, a.unreleased_name)
    if a.output:
        with open(a.output, "w") as f:
            f.write(md)
        print(f"wrote {a.output} ({len(commits)} commits)")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
