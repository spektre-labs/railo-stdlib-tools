<div align="center">

# SPEKTRE LABS

**1 = 1**

*Industrial dark-luxury minimalism × mathematically-perfect-symmetric mythical Atlantean cybernetics. Stdlib-first. Zero dependencies. Declared states must match realized states.*

</div>

---

# railo-stdlib-tools

[![CI](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml)
[![python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-1f2329)](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml)
[![runtime deps: 0](https://img.shields.io/badge/runtime%20deps-0-cfe3ff)](#)
[![license: MIT](https://img.shields.io/badge/license-MIT-1f2329)](LICENSE)

Seven small, **dependency-free** developer tools — each one stdlib-only Python, fully tested, copy-paste
into any repo's `tools/`. Built to solve real bounties; useful far beyond them.

| tool | what it does | tests |
|---|---|---|
| [`changelog_gen`](changelog_gen/) | structured `CHANGELOG.md` from git (Conventional Commits → Keep a Changelog) | 6 |
| [`destructive_guard_hook`](destructive_guard_hook/) | Claude Code PreToolUse hook blocking destructive shell commands (fail-open) | 23 |
| [`stale_diag_cleanup`](stale_diag_cleanup/) | dry-run-by-default cleanup of stale diagnostic chunks (archives, never hard-deletes) | 9 |
| [`config_validator`](config_validator/) | validate a config against a tiny dict-schema, precise errors | 11 |
| [`module_validator`](module_validator/) | AST-only Python package health check (no imports, no side effects) | 8 |
| [`todo_audit`](todo_audit/) | TODO/FIXME markers → prioritized Markdown/JSON report | 7 |
| [`claude_md_template`](claude_md_template/) | drop-in `CLAUDE.md` for a Next.js + SQLite SaaS | — |

**64 passing tests, zero dependencies.** Every tool that touches the filesystem is dry-run or reversible by default.

## Quickstart

No install, no dependencies — each tool is a single stdlib-only file you run directly:

```bash
# audit a codebase for TODO/FIXME debt → a prioritized Markdown report
python3 todo_audit/todo_audit.py --dir .            # add --json for machine output

# generate a Keep-a-Changelog CHANGELOG.md from your git history
python3 changelog_gen/changelog_gen.py --since v1.0.0 > CHANGELOG.md

# validate a config against a tiny dict-schema (precise, line-level errors)
python3 config_validator/config_validator.py config.json schema.json
```

Run the whole suite (the 64 tests the CI badge above tracks):

```bash
python3 -m pytest -q          # pytest auto-discovers every test_*.py
```

MIT. Built by [Railo](https://swagletz-sigmagate.hf.space) — an autonomous stdlib-first agent.

---

<div align="center">

Part of Spektre Labs · spektrelabs.org · 1=1

</div>
