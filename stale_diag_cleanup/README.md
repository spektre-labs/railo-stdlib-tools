# stale_diag_cleanup

Report (and optionally archive) stale diagnostic chunks under `diagnostic/`. **DRY-RUN by default** —
deletes nothing unless `--apply`, and even then archives (reversible) instead of hard-deleting. Stdlib only.

## Stale =
- `.logd` chunk older than `--max-age-hours` with no matching `.done` marker
- `.part` / `.tmp` partials from an interrupted write
- `*.meta.json` orphan with no `.logd` sibling

## Usage
```bash
python3 stale_diag_cleanup.py                      # dry-run report (./diagnostic)
python3 stale_diag_cleanup.py --max-age-hours 6
python3 stale_diag_cleanup.py --apply              # archive stale → .stale_archive/<ts>/ (reversible)
python3 stale_diag_cleanup.py --json
```

## Test
```bash
python3 -m pytest test_stale_diag_cleanup.py -q    # 9 tests, tmp dirs, offline
```

Safety: dry-run never touches the filesystem; `--apply` moves (not deletes) so a wrong call is recoverable.
