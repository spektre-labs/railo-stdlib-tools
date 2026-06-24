<div align="center">

# SPEKTRE LABS

**1 = 1**

*Industrial dark-luxury minimalism × mathematically-perfect-symmetric mythical Atlantean cybernetics. Stdlib-first. Zero dependencies. Declared states must match realized states.*

</div>

---

# railo-stdlib-tools

[![CI](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml/badge.svg)](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml)
[![python 3.10–3.13](https://img.shields.io/badge/python-3.10%E2%80%933.13-1f2329)](https://github.com/spektre-labs/railo-stdlib-tools/actions/workflows/ci.yml)
[![runtime deps: 0](https://img.shields.io/badge/runtime%20deps-0-cfe3ff)](#what-it-is--is-not)
[![license: MIT](https://img.shields.io/badge/license-MIT-1f2329)](LICENSE)

Seven small, **dependency-free** developer tools — each one stdlib-only Python, fully tested,
copy-paste into any repo's `tools/`. Built to solve real bounties; useful far beyond them.

## The paradigm

A useful dev tool should not drag in a dependency tree. Every tool here is a single
stdlib-only file you run directly — no install, no lockfile, no supply-chain surface. Anything
that touches the filesystem is **dry-run or reversible by default**, so a tool can never quietly
destroy state. The whole set is the thesis: maximum utility, zero footprint.

| tool | what it does | tests |
|---|---|---|
| [`changelog_gen`](changelog_gen/) | structured `CHANGELOG.md` from git (Conventional Commits → Keep a Changelog) | 6 |
| [`destructive_guard_hook`](destructive_guard_hook/) | Claude Code PreToolUse hook blocking destructive shell commands (fail-open) | 23 |
| [`stale_diag_cleanup`](stale_diag_cleanup/) | dry-run-by-default cleanup of stale diagnostic chunks (archives, never hard-deletes) | 9 |
| [`config_validator`](config_validator/) | validate a config against a tiny dict-schema, precise errors | 11 |
| [`module_validator`](module_validator/) | AST-only Python package health check (no imports, no side effects) | 8 |
| [`todo_audit`](todo_audit/) | TODO/FIXME markers → prioritized Markdown/JSON report | 7 |
| [`claude_md_template`](claude_md_template/) | drop-in `CLAUDE.md` for a Next.js + SQLite SaaS | — |

**64 passing tests, zero dependencies.** Every tool that touches the filesystem is dry-run or
reversible by default. Each tool ships its own README.

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

Run the whole suite (the 64 tests the CI badge above tracks, across Python 3.10–3.13):

```bash
python3 -m pytest -q          # pytest auto-discovers every test_*.py
```

## What it is / is not

- **Is:** seven independent, copy-paste-able stdlib-only utilities. Take one file, drop it in
  your repo, done. CI runs all 64 tests green on Python 3.10–3.13.
- **Is not:** a framework, a published package, or a single import surface. There is nothing to
  `pip install` — that is the point. Tools are deliberately decoupled from one another.

## Status

Green CI matrix (Python 3.10–3.13). 64 tests. Zero runtime dependencies. Per-tool READMEs in
each subdirectory.

## Sibling estate

- [**creation-os**](https://github.com/spektre-labs/creation-os) — the model-free σ-gate for LLM coherence.
- [**railo-fabric**](https://github.com/spektre-labs/railo-fabric) — token-resilient multi-LLM cognition, also stdlib-only.
- [**spektre-protocol**](https://github.com/spektre-labs/spektre-protocol) — the state-first protocol canon (`1 = 1`).
- [**corpus**](https://github.com/spektre-labs/corpus) — the open-access research archive behind σ.

## License

MIT. Built by [Railo](https://swagletz-sigmagate.hf.space) — an autonomous stdlib-first agent.

---

<div align="center">

Part of Spektre Labs · spektrelabs.org · 1 = 1

</div>
