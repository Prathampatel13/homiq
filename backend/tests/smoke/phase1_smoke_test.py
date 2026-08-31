"""
Phase 1 End-to-End Smoke Test for HomiQ backend.

Covers:
- POST /auth/register
- POST /auth/login
- GET  /customer/profile
- PUT  /customer/profile
- GET  /customer/addresses
- POST /customer/addresses
- PUT  /customer/addresses/{id}
- DELETE /customer/addresses/{id}
- GET  /customer/dashboard

Also verifies User <-> Customer mapping is created during registration.
"""
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def generate_email() -> str:
    return f"phase1_{uuid.uuid4().hex[:10]}@example.com"


def step(name: str):
    print(f"\n{'='*70}\n▶ {name}\n{'='*70}")


def main():
    results = []
    email = generate_email()
    password = "Test@1234"

    # ── 1. REGISTER ────────────────────────────────────────────────────
    step("1. POST /auth/register")
    r = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Phase One Tester",
        "phone": "9876543210",
        "role": "customer",
    })
    print(r.status_code, r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text)
    assert r.status_code == 201, f"Register failed: {r.text}"
    tokens = r.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    results.append(("register", r.status_code))
    print(f"registered {email}")
    headers = {"Authorization": f"Bearer {access_token}"}

    # ── 2. LOGIN ───────────────────────────────────────────────────────
    step("2. POST /auth/login")
    r = client.post("/auth/login", json={"identifier": email, "password": password})
    print(r.status_code, r.json())
    assert r.status_code == 200
    access_token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    results.append(("login", r.status_code))

    # ── 3. GET /customer/profile ───────────────────────────────────────
    step("3. GET /customer/profile")
    r = client.get("/customer/profile", headers=headers)
    print(r.status_code, r.json())
    assert r.status_code == 200, f"Profile failed: {r.text}"
    profile = r.json()
    assert profile["user_id"] is not None
    assert profile["email"] == email
    assert profile["full_name"] == "Phase One Tester"
    assert profile["addresses"] == [], "New customer should have no addresses"
    customer_id = profile["id"]
    results.append(("customer_profile_get", r.status_code))
    print(f"customer.id={customer_id} user_id={profile['user_id']}")

    # ── 4. PUT /customer/profile ───────────────────────────────────────
    step("4. PUT /customer/profile")
    r = client.put("/customer/profile", headers=headers, json={
        "full_name": "Phase One Updated",
        "phone": "9876500000",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560001",
        "preferred_language": "en",
    })
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["full_name"] == "Phase One Updated"
    assert r.json()["city"] == "Bengaluru"
    results.append(("customer_profile_put", r.status_code))

    # ── 5. POST /customer/addresses ────────────────────────────────────
    step("5. POST /customer/addresses")
    r = client.post("/customer/addresses", headers=headers, json={
        "full_name": "Phase One Tester",
        "phone": "9876543210",
        "house_no": "42",
        "building": "Sunrise Tower",
        "landmark": "Near Central Park",
        "area": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "latitude": 12.9716,
        "longitude": 77.5946,
        "is_default": True,
    })
    print(r.status_code, r.json())
    assert r.status_code == 201, f"Create address failed: {r.text}"
    addr1 = r.json()
    assert addr1["is_default"] is True, "First address should be default"
    addr1_id = addr1["id"]
    results.append(("address_create", r.status_code))

    # ── 6. GET /customer/addresses ─────────────────────────────────────
    step("6. GET /customer/addresses")
    r = client.get("/customer/addresses", headers=headers)
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert len(r.json()) == 1
    results.append(("address_list", r.status_code))

    # ── 7. POST second address (not default) ───────────────────────────
    step("7. POST /customer/addresses (second, non-default)")
    r = client.post("/customer/addresses", headers=headers, json={
        "full_name": "Phase One Tester",
        "phone": "9876543210",
        "house_no": "7",
        "building": "Green Villa",
        "area": "Koramangala",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560034",
    })
    print(r.status_code, r.json())
    assert r.status_code == 201
    addr2_id = r.json()["id"]
    results.append(("address_create_2", r.status_code))

    # ── 8. PUT /customer/addresses/{id} ────────────────────────────────
    step("8. PUT /customer/addresses/{id}")
    r = client.put(f"/customer/addresses/{addr1_id}", headers=headers, json={
        "is_default": True,
        "landmark": "Near Metro Station",
    })
    print(r.status_code, r.json())
    assert r.status_code == 200
    assert r.json()["landmark"] == "Near Metro Station"
    assert r.json()["is_default"] is True
    results.append(("address_update", r.status_code))

    # ── 9. Verify only one default after second address ────────────────
    step("9. Verify default isolation")
    r = client.get("/customer/addresses", headers=headers)
    assert r.status_code == 200
    defaults = [a for a in r.json() if a["is_default"]]
    assert len(defaults) == 1, f"Expected exactly 1 default, got {len(defaults)}"
    results.append(("default_isolation", r.status_code))

    # ── 10. DELETE /customer/addresses/{id} ────────────────────────────
    step("10. DELETE /customer/addresses/{id}")
    r = client.delete(f"/customer/addresses/{addr2_id}", headers=headers)
    print(r.status_code, r.json())
    assert r.status_code == 200
    results.append(("address_delete", r.status_code))

    # ── 11. GET /customer/dashboard ────────────────────────────────────
    step("11. GET /customer/dashboard")
    r = client.get("/customer/dashboard", headers=headers)
    print(r.status_code, r.json())
    assert r.status_code == 200
    results.append(("customer_dashboard", r.status_code))

    # ── 12. Role enforcement: technician cannot access customer ────────
    step("12. Role enforcement (register technician, try /customer/profile)")
    tech_email = generate_email()
    r = client.post("/auth/register", json={
        "email": tech_email,
        "password": password,
        "full_name": "Tech User",
        "role": "technician",
    })
    assert r.status_code == 201
    tech_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.get("/customer/profile", headers=tech_headers)
    print("technician on /customer/profile →", r.status_code)
    assert r.status_code == 403, "Technician should be forbidden from customer endpoints"
    results.append(("role_enforcement", r.status_code))

    print("\n" + "=" * 70)
    print("PHASE 1 SMOKE TEST SUMMARY")
    print("=" * 70)
    all_ok = True
    for name, code in results:
        ok = 200 <= code < 300 if code not in (400, 401, 403, 404, 422) else code == 403 and name == "role_enforcement"
        if name == "role_enforcement":
            ok = code == 403
        status_str = "OK" if ok else f"UNEXPECTED ({code})"
        if not ok:
            all_ok = False
        print(f"  {name:<28} {code}  {status_str}")
    print(f"\n→ {'ALL TESTS PASSED' if all_ok else 'SOME TESTS FAILED'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())

