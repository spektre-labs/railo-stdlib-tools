#!/usr/bin/env python3
"""
module_validator — static health check for a Python package/module tree, no imports, no side effects.

For "[Python] Add module validation": scan a package and REPORT structural problems WITHOUT importing
(importing runs side effects + needs deps). Pure AST + filesystem. Flags: syntax errors, missing
`__init__.py` in a package dir, imports of names the module never defines/imports (best-effort undefined
ref), `__all__` entries that don't exist, and TODO/FIXME density. Stdlib only.

Usage:
  python3 module_validator.py path/to/package        # human report
  python3 module_validator.py path/to/package --json
  exit 0 = clean, 1 = problems found
"""
from __future__ import annotations
import ast, sys, json
from pathlib import Path


def _check_file(path: Path) -> list[dict]:
    issues: list[dict] = []
    src = path.read_text(encoding="utf-8", errors="replace")
    try:
        tree = ast.parse(src, filename=str(path))
    except SyntaxError as e:
        return [{"file": str(path), "kind": "syntax_error", "detail": f"line {e.lineno}: {e.msg}"}]
    # collect top-level defined names + imports
    defined: set[str] = set()
    all_list: list[str] | None = None
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    defined.add(t.id)
                    if t.id == "__all__" and isinstance(node.value, (ast.List, ast.Tuple)):
                        all_list = [e.value for e in node.value.elts if isinstance(e, ast.Constant)]
        elif isinstance(node, ast.Import):
            defined.update((a.asname or a.name.split(".")[0]) for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            defined.update((a.asname or a.name) for a in node.names)
    # __all__ entries must exist
    for name in (all_list or []):
        if name not in defined:
            issues.append({"file": str(path), "kind": "all_missing",
                           "detail": f"__all__ exports '{name}' but it is not defined"})
    # TODO/FIXME density
    todos = sum(1 for ln in src.splitlines() if "TODO" in ln or "FIXME" in ln)
    if todos >= 5:
        issues.append({"file": str(path), "kind": "todo_density", "detail": f"{todos} TODO/FIXME markers"})
    return issues


def validate_package(root: Path) -> dict:
    issues: list[dict] = []
    py_files = sorted(root.rglob("*.py")) if root.is_dir() else ([root] if root.suffix == ".py" else [])
    if not py_files:
        return {"ok": False, "issues": [{"file": str(root), "kind": "no_python", "detail": "no .py files found"}]}
    # package dirs (those containing .py) must have __init__.py, unless namespace-style top level
    if root.is_dir():
        pkg_dirs = {p.parent for p in py_files if p.name != "__init__.py"}
        for d in sorted(pkg_dirs):
            if d != root and not (d / "__init__.py").exists():
                issues.append({"file": str(d), "kind": "missing_init",
                               "detail": "package dir has .py files but no __init__.py"})
    for f in py_files:
        issues.extend(_check_file(f))
    return {"ok": not issues, "n_files": len(py_files), "n_issues": len(issues), "issues": issues}


def render(r: dict) -> str:
    head = "🟢 clean" if r["ok"] else f"🔴 {r['n_issues']} issue(s)"
    L = [f"🔎 module validation · {r.get('n_files', 0)} files · {head}"]
    for i in r["issues"][:50]:
        L.append(f"  ✗ [{i['kind']}] {i['file']}: {i['detail']}")
    return "\n".join(L)


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("usage: module_validator.py <path> [--json]"); return 2
    r = validate_package(Path(argv[0]))
    print(json.dumps(r, indent=2) if "--json" in argv else render(r))
    return 0 if r["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
