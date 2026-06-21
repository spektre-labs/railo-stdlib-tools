# todo_audit

Scan a source tree for TODO/FIXME/HACK/XXX/BUG/OPTIMIZE markers → structured, prioritized Markdown/JSON report.
Parses `TAG(owner)[priority]: note`, ranks by priority, groups by tag, skips vendored/build dirs. Stdlib, 0 deps.

```bash
python3 todo_audit.py                 # scan . → markdown
python3 todo_audit.py --dir src --json
python3 todo_audit.py -o TODO_AUDIT.md
```
Test: `python3 -m pytest test_todo_audit.py -q` (7 tests, tmp trees).
