"""Verify the Jobs module: AST parse + app import + route registration."""

import ast
import sys

sys.path.insert(0, r"c:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend")

FILES = [
    "app/crud/jobs.py",
    "app/schemas/jobs.py",
    "app/services/jobs.py",
    "app/api/jobs/__init__.py",
    "app/api/jobs/router.py",
    "app/models/jobs.py",
    "app/models/users.py",
    "app/main.py",
    "app/services/__init__.py",
]


def ast_check() -> bool:
    ok = True
    print("-- AST SYNTAX CHECK --")
    for f in FILES:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                ast.parse(fh.read())
            print(f"  OK  {f}")
        except SyntaxError as e:
            print(f"FAIL  {f}: {e}")
            ok = False
    return ok


def import_check() -> bool:
    print("\n-- APP IMPORT + ROUTE CHECK --")
    try:
        from app.main import app
    except Exception:
        import traceback
        traceback.print_exc()
        return False

    route_paths = sorted({r.path for r in app.routes if hasattr(r, "path")})
    job_routes = [p for p in route_paths if p.startswith("/jobs")]
    print("Jobs routes registered:")
    for p in job_routes:
        print(f"  {p}")
    expected = {
        "/jobs/",
        "/jobs/my",
        "/jobs/{job_post_id}",
        "/jobs/{job_post_id}/applications",
        "/jobs/{job_post_id}/apply",
        "/jobs/applications/my",
        "/jobs/applications/{application_id}/status",
        "/jobs/applications/{application_id}",
    }
    missing = expected - set(job_routes)
    if missing:
        print(f"FAIL  missing routes: {missing}")
        return False
    unknown = set(job_routes) - expected
    if unknown:
        print(f"INFO  extra routes: {unknown}")
    print("  All expected job routes present OK")
    return True


def service_export_check() -> bool:
    print("\n-- SERVICE EXPORT CHECK --")
    try:
        from app.services import JobService
        print(f"  OK  JobService exported: {JobService}")
        return True
    except Exception as e:
        print(f"FAIL  JobService export: {e}")
        return False


if __name__ == "__main__":
    results = []
    results.append(("ast_parse", ast_check()))
    results.append(("app_import_routes", import_check()))
    results.append(("service_export", service_export_check()))

    print("\n" + "=" * 50)
    ok_all = True
    for name, ok in results:
        print(f"  {name:<24} {'OK' if ok else 'FAIL'}")
        if not ok:
            ok_all = False
    print(f"\n-> {'ALL CHECKS PASSED' if ok_all else 'SOME CHECKS FAILED'}")
    sys.exit(0 if ok_all else 1)
