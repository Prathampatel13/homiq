"""Static scanner to verify all internal app.* imports resolve to existing modules."""
import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
APP = ROOT / "app"

errors = []
files_scanned = 0


def module_exists(module_name: str) -> bool:
    """Check whether a dotted module path exists under the app package."""
    parts = module_name.split(".")
    if parts[0] != "app":
        return True  # third-party, skip
    current = APP
    for part in parts[1:]:
        candidate_dir = current / part
        if candidate_dir.is_dir() and (candidate_dir / "__init__.py").exists():
            current = candidate_dir
            continue
        candidate_file = current / f"{part}.py"
        if candidate_file.exists():
            current = candidate_file
            continue
        return False
    return True


for file in sorted(APP.rglob("*.py")):
    files_scanned += 1
    try:
        tree = ast.parse(file.read_text(encoding="utf-8"))
    except SyntaxError as e:
        errors.append(f"SYNTAX {file}: {e}")
        continue
    rel = file.relative_to(ROOT)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not module_exists(alias.name):
                    errors.append(f"IMPORT {rel}: import {alias.name} -> module not found")
        elif isinstance(node, ast.ImportFrom):
            if node.level:  # relative import
                continue
            mod = node.module or ""
            if not module_exists(mod):
                errors.append(f"IMPORT {rel}: from {mod} import ... -> module not found")

print(f"Scanned {files_scanned} Python files.")
if errors:
    print(f"FAILED: {len(errors)} errors")
    for e in errors:
        print("  " + e)
    sys.exit(1)
else:
    print("ALL INTERNAL IMPORTS RESOLVE OK")

