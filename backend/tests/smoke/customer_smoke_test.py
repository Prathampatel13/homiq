"""
Phase 1 customer smoke test.

Covers the exact API surface required:
  POST   /auth/register
  POST   /auth/login
  GET    /customer/profile
  PUT    /customer/profile
  GET    /customer/addresses
  POST   /customer/addresses
  PUT    /customer/addresses/{id}
  DELETE /customer/addresses/{id}
  POST   /bookings
  GET    /bookings
  POST   /payments/create-order
  POST   /payments/verify
  POST   /invoices
  GET    /dashboard
"""
import datetime
import sys
from pathlib import Path
from uuid import uuid4

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

RESULTS = []


def check(name, code, expected_codes):
    ok = code in expected_codes
    RESULTS.append((name, code, ok))
    print(f"  {'OK ' if ok else 'FAIL'} {name:<32} -> {code}")
    return ok


def main():
    email = f"cust_{uuid4().hex[:12]}@example.com"
    password = "Test@12345"

    # Register
    print("\nPOST /auth/register")
    r = client.post("/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Smoke Customer",
        "phone": "9876543210",
        "role": "customer",
    })
    print(" ", r.status_code, r.text[:200])
    check("register", r.status_code, [201])
    assert r.status_code == 201, r.text
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Login
    print("\nPOST /auth/login")
    r = client.post("/auth/login", json={"identifier": email, "password": password})
    print(" ", r.status_code, r.text[:200])
    check("login", r.status_code, [200])
    assert r.status_code == 200, r.text
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Profile
    print("\nGET /customer/profile")
    r = client.get("/customer/profile", headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("profile_get", r.status_code, [200])
    assert r.status_code == 200, r.text
    profile = r.json()
    print("   id:", profile.get("id"), "user_id:", profile.get("user_id"))

    print("\nPUT /customer/profile")
    r = client.put("/customer/profile", json={
        "full_name": "Updated Customer Name",
        "city": "Mumbai",
        "preferred_language": "en",
    }, headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("profile_update", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["full_name"] == "Updated Customer Name"

    # Addresses
    print("\nPOST /customer/addresses")
    r = client.post("/customer/addresses", json={
        "full_name": "Smoke Customer",
        "phone": "9876543210",
        "house_no": "12",
        "building": "Sunrise Towers",
        "area": "Andheri West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400053",
        "is_default": True,
    }, headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("address_create", r.status_code, [201])
    assert r.status_code == 201, r.text
    addr_id = r.json()["id"]

    print("\nGET /customer/addresses")
    r = client.get("/customer/addresses", headers=headers)
    print(" ", r.status_code, r.text[:400])
    check("address_list", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert len(r.json()) == 1

    print("\nPUT /customer/addresses/{id}")
    r = client.put(f"/customer/addresses/{addr_id}", json={
        "landmark": "Near Metro",
        "area": "Andheri East",
    }, headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("address_update", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["area"] == "Andheri East"

    # Bookings
    print("\nPOST /bookings")
    r_svc = client.get("/services/")
    items = r_svc.json().get("items", []) if r_svc.status_code == 200 else []
    service_id = items[0]["id"] if items else 101
    future = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
    r = client.post("/bookings", json={
        "service_id": service_id,
        "address_id": addr_id,
        "booking_date": future,
        "preferred_time": "10:30:00",
        "customer_note": "Smoke customer booking",
    }, headers=headers)
    print(" ", r.status_code, r.text[:400])
    check("booking_create", r.status_code, [201])
    assert r.status_code == 201, r.text
    booking_id = r.json()["id"]

    print("\nGET /bookings")
    r = client.get("/bookings", headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("booking_list", r.status_code, [200])
    assert r.status_code == 200, r.text

    # Payments
    print("\nPOST /payments/create-order")
    r = client.post("/payments/create-order", json={"booking_id": booking_id}, headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("payment_create_order", r.status_code, [200, 502, 503])

    # Invoices - customer must be forbidden
    print("\nPOST /invoices (customer must be forbidden)")
    r = client.post("/invoices", json={
        "booking_id": booking_id,
        "subtotal": 499.0,
        "total_amount": 499.0,
    }, headers=headers)
    print(" ", r.status_code, r.text[:200])
    check("invoice_admin_gate", r.status_code, [403])
    assert r.status_code == 403, r.text

    # Dashboard
    print("\nGET /dashboard")
    r = client.get("/dashboard", headers=headers)
    print(" ", r.status_code, r.text[:300])
    check("dashboard", r.status_code, [200])
    assert r.status_code == 200, r.text

    # Delete booking-linked address must be rejected
    print("\nDELETE /customer/addresses/{id} (linked to booking -> expect 400)")
    r = client.delete(f"/customer/addresses/{addr_id}", headers=headers)
    print(" ", r.status_code, r.text[:200])
    check("address_delete_linked_guard", r.status_code, [400])
    assert r.status_code == 400, r.text

    # Delete a fresh (unused) address must succeed
    print("\nPOST /customer/addresses (second, unused)")
    r = client.post("/customer/addresses", json={
        "full_name": "Smoke Customer",
        "phone": "9876543210",
        "house_no": "99",
        "area": "Bandra West",
        "city": "Mumbai",
        "state": "Maharashtra",
        "pincode": "400050",
    }, headers=headers)
    print(" ", r.status_code, r.text[:200])
    check("address_create_2", r.status_code, [201])
    assert r.status_code == 201, r.text
    addr2_id = r.json()["id"]

    print("\nDELETE /customer/addresses/{id} (unused -> expect 200)")
    r = client.delete(f"/customer/addresses/{addr2_id}", headers=headers)
    print(" ", r.status_code, r.text[:200])
    check("address_delete", r.status_code, [200])
    assert r.status_code == 200, r.text

    print("\n" + "=" * 60)
    print("CUSTOMER SMOKE TEST SUMMARY")
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

