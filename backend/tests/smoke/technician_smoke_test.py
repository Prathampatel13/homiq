"""
Technician module smoke test.

Covers the exact technician API surface:
  POST   /auth/register (technician)
  GET    /technician/profile
  PUT    /technician/profile
  GET    /technician/jobs
  GET    /technician/earnings
  PUT    /technician/availability
  GET    /technician/dashboard
  GET    /technician/ (list)

Also verifies role enforcement: a customer cannot access technician-scoped
endpoints (should get 403).
"""
import sys
from pathlib import Path
import uuid

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PASSWORD = "Test@12345"

RESULTS = []


def check(name, code, expected_codes):
    ok = code in expected_codes
    RESULTS.append((name, code, ok))
    print(f"  {'OK ' if ok else 'FAIL'} {name:<32} -> {code}")


def gen_email(role: str) -> str:
    return f"{role}_{uuid.uuid4().hex[:10]}@example.com"


def register(role: str = "technician"):
    r = client.post("/auth/register", json={
        "email": gen_email(role),
        "password": PASSWORD,
        "full_name": f"Smoke {role.capitalize()}",
        "phone": "9876512345",
        "role": role,
    })
    assert r.status_code == 201, f"Register failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def main():
    tech_headers = register("technician")

    # ── Profile ────────────────────────────────────────────────────
    print("\n▶ GET /technician/profile")
    r = client.get("/technician/profile", headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("profile_get", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["user_id"] > 0

    print("\n▶ PUT /technician/profile")
    r = client.put("/technician/profile", json={
        "full_name": "Updated Technician",
        "specialization": "Plumbing",
        "experience_years": 5,
        "skills": ["Pipe fitting", "Leak repair"],
        "availability": True,
        "is_online": True,
    }, headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("profile_update", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["specialization"] == "Plumbing"

    # ── Jobs ───────────────────────────────────────────────────────
    print("\n▶ GET /technician/jobs")
    r = client.get("/technician/jobs", headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("jobs_list", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert "items" in r.json() and "total" in r.json()

    # ── Earnings ───────────────────────────────────────────────────
    print("\n▶ GET /technician/earnings")
    r = client.get("/technician/earnings", headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("earnings", r.status_code, [200])
    assert r.status_code == 200, r.text
    data = r.json()
    assert "total_earnings" in data and "pending_earnings" in data

    # ── Availability ───────────────────────────────────────────────
    print("\n▶ PUT /technician/availability")
    r = client.put("/technician/availability", json={
        "availability": False,
        "is_online": False,
    }, headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("availability_update", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["availability"] is False
    assert r.json()["is_online"] is False

    # ── Dashboard ──────────────────────────────────────────────────
    print("\n▶ GET /technician/dashboard")
    r = client.get("/technician/dashboard", headers=tech_headers)
    print(" ", r.status_code, r.text[:300])
    check("dashboard", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert "stats" in r.json()

    # ── List ───────────────────────────────────────────────────────
    print("\n▶ GET /technician/")
    r = client.get("/technician/")
    print(" ", r.status_code, r.text[:200])
    check("list_technicians", r.status_code, [200])
    assert r.status_code == 200, r.text

    # ── Role enforcement: customer blocked ─────────────────────────
    print("\n▶ Customer accessing /technician/profile (expect 403)")
    cust_headers = register("customer")
    r = client.get("/technician/profile", headers=cust_headers)
    print(" ", r.status_code, r.text[:200])
    check("role_gate_customer_blocked", r.status_code, [403])
    assert r.status_code == 403, r.text

    print("\n" + "=" * 60)
    print("TECHNICIAN SMOKE TEST SUMMARY")
    print("=" * 60)
    all_ok = True
    for name, code, ok in RESULTS:
        print(f"  {name:<32} {code}  {'OK' if ok else 'FAIL'}")
        if not ok:
            all_ok = False
    print()
    print("-> ALL TESTS PASSED" if all_ok else "-> SOME TESTS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
