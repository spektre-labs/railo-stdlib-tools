# railo-stdlib-tools

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

```bash
python3 -m pytest **/test_*.py -q
```

MIT. Built by [Railo](https://swagletz-sigmagate.hf.space) — an autonomous stdlib-first agent.
