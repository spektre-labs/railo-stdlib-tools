# changelog_gen

Generate a structured `CHANGELOG.md` from git history. **Stdlib only, zero dependencies, deterministic, offline.**

Groups commits by [Conventional Commit](https://www.conventionalcommits.org) type into
[Keep a Changelog](https://keepachangelog.com) sections, split into release blocks by git tag,
with `⚠ BREAKING CHANGES` surfaced first.

## Usage
```bash
python3 changelog_gen.py                      # whole history → stdout
python3 changelog_gen.py --since v1.2.0       # only commits after a ref
python3 changelog_gen.py --repo /path -o CHANGELOG.md
```

## Mapping
| commit type | section |
|---|---|
| feat | Added |
| fix | Fixed |
| perf | Performance |
| refactor / revert | Changed / Reverted |
| docs / test / build / ci / chore | Documentation / Tests / Build / CI / Chores |
| `type!:` or `BREAKING` | ⚠ BREAKING CHANGES |
| unstructured | Other |

Untyped commits are never dropped — they land under **Other**.

## Test
```bash
python3 -m pytest test_changelog_gen.py -q   # 6 tests, offline (synthetic commits)
```

## Why
No Node toolchain, no `conventional-changelog` 40-dep tree, no network. One stdlib file,
copy-paste into any repo's `tools/`. Output is byte-stable for the same history → reviewable in CI.
