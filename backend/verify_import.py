import sys
import os
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

errors = []

# Phase 1: Check all Python files for syntax errors
print("=" * 60)
print("PHASE 1: SYNTAX CHECK")
print("=" * 60)

import ast
import pathlib

py_files = list(pathlib.Path(ROOT, "app").rglob("*.py"))
for file in py_files:
    try:
        ast.parse(file.read_text(encoding="utf-8"))
    except SyntaxError as e:
        errors.append(f"SYNTAX ERROR in {file}: {e}")
        print(f"  [FAIL] {file}: {e}")
    except Exception as e:
        errors.append(f"ERROR reading {file}: {e}")
        print(f"  [FAIL] {file}: {e}")

print(f"\nSyntax check complete. {len(py_files)} files scanned.")

# Phase 2: Import the app main module
print("\n" + "=" * 60)
print("PHASE 2: IMPORT CHECK")
print("=" * 60)

try:
    import app.main
    print("[OK] app.main imported successfully")
    print(f"[OK] App: {app.main.app}")
except Exception as e:
    errors.append(f"IMPORT ERROR: {e}")
    print(f"[FAIL] app.main import failed: {e}")
    traceback.print_exc()

# Phase 3: List all routes
print("\n" + "=" * 60)
print("PHASE 3: ROUTE LISTING")
print("=" * 60)

try:
    from app.main import app
    for route in app.routes:
        methods = ",".join(sorted(getattr(route, "methods", []) or []))
        print(f"  {methods:20s} {getattr(route, 'path', '')}")
except Exception as e:
    errors.append(f"ROUTE LISTING ERROR: {e}")
    print(f"[FAIL] Route listing failed: {e}")

print("\n" + "=" * 60)
print("RESULT")
print("=" * 60)
if errors:
    print(f"FAILED: {len(errors)} errors found")
    for err in errors:
        print(f"  - {err}")
else:
    print("ALL CHECKS PASSED")

