# Bounty deliverables — built & tested, ready to submit (PR → maintainer merge → crypto payout)

Self-contained artifacts produced for cached self-deliverable bounties (`runtime/bounty_harness.py` ranks
34/129 as agent-buildable). Each is stdlib-only, fully tested, with a README. Payout is human-gated (a real
maintainer must merge the PR) — these are the FINISHED work, ready to submit.

| bounty | $ | deliverable | tests | status |
|---|---|---|---|---|
| SKILL: Generate a structured CHANGELOG from git | $50 | `solutions/changelog_gen/` | 6 ✅ | ready to PR |
| HOOK: Pre-tool-use hook that blocks destructive | $100 | `solutions/destructive_guard_hook/` | 23 ✅ | ready to PR |
| [Python] Add stale diagnostic cleanup dry-run | $25 | `solutions/stale_diag_cleanup/` | 9 ✅ | ready to PR |
| TEMPLATE: CLAUDE.md for a Next.js + SQLite SaaS | $75 | `solutions/claude_md_template/` | n/a (content) | ready to PR |
| [Python] Add config generator validation | $45 | `solutions/config_validator/` | 11 ✅ | ready to PR |
| [Python] Add module validation | $35 | `solutions/module_validator/` | 8 ✅ | ready to PR |
| [Python] Generate TODO audit report | $5 | `solutions/todo_audit/` | 7 ✅ | ready to PR |

**Total built: $335 of ready-to-submit work, 64 passing tests, 0 deps, 7 self-contained deliverables.**

Each: stdlib-only, fully tested, README, dry-run/fail-safe where it touches anything. Reusable beyond the
bounty (drop into any repo's `tools/`). `runtime/bounty_harness.py` (`/bounties`) keeps surfacing the next target.

## Next ranked self-deliverable targets (from `/bounties`)
- [$25] [TypeScript] Add reconnect metrics for frontend
- [$5] [Python] Generate TODO audit report
- [BOUNTY] structured CHANGELOG variants for other repos (changelog_gen already covers)

## How to realize (the one human-gated step)
1. fork/clone the target repo, drop the deliverable into its `tools/` (or as the PR asks)
2. open the PR referencing the bounty issue
3. maintainer merges → bounty pays to the wallet (`7oDgMf…`, or the bounty platform's payout)

The agent did the work; the merge is the external gate. σ-honest: $175 *built* ≠ $175 *realized* until merged.
