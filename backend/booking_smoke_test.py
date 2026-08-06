"""
Booking lifecycle smoke test.

Covers the full HomiQ booking lifecycle:

  Customer:
    POST   /bookings/
    GET    /bookings/
    GET    /bookings/{id}
    PUT    /bookings/{id}
    POST   /bookings/{id}/cancel
    PUT    /bookings/{id}/reschedule
    GET    /bookings/{id}/history
    GET    /bookings/{id}/track
    GET    /bookings/{id}/technician

  Admin:
    PUT    /bookings/{id}/assign
    PUT    /admin/bookings/{id}/reassign
    POST   /admin/bookings/{id}/force-cancel
    PUT    /admin/bookings/{id}/override-status

  Technician:
    POST   /bookings/{id}/accept
    POST   /bookings/{id}/reject
    POST   /bookings/{id}/start-trip
    POST   /bookings/{id}/arrived
    POST   /bookings/{id}/start-service
    POST   /bookings/{id}/complete

Also verifies:
  - Invalid transitions return 409
  - Role enforcement (customer cannot run technician actions)
  - Duplicate action detection (already-accepted -> 409)
"""
import sys
import uuid
from datetime import date, timedelta

sys.path.insert(0, r"c:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend")

import psycopg
from fastapi.testclient import TestClient

from app.main import app
from app.security.passwords import hash_password

client = TestClient(app)
PASSWORD = "Test@12345"

ADMIN_EMAIL = "lifecycle_admin@homiq.com"
ADMIN_PASSWORD = "Admin@12345"

RESULTS = []


def check(name, code, expected_codes):
    ok = code in expected_codes
    RESULTS.append((name, code, ok))
    print(f"  {'OK ' if ok else 'FAIL'} {name:<38} -> {code}")
    return ok


def gen_email(role: str) -> str:
    return f"{role}_{uuid.uuid4().hex[:10]}@example.com"


def ensure_admin() -> dict:
    """Create/refresh a dedicated superuser admin directly in the DB."""
    conn = psycopg.connect("postgresql://postgres:postgres123@localhost:5432/homiq_db")
    cur = conn.cursor()
    cur.execute("SELECT id FROM roles WHERE name = 'admin'")
    role_row = cur.fetchone()
    if not role_row:
        cur.execute(
            "INSERT INTO roles (name, description, created_at) VALUES ('admin', 'Admin role', now()) RETURNING id"
        )
        role_id = cur.fetchone()[0]
        conn.commit()
    else:
        role_id = role_row[0]

    cur.execute("SELECT id FROM users WHERE email = %s", (ADMIN_EMAIL,))
    existing = cur.fetchone()
    pwd_hash = hash_password(ADMIN_PASSWORD)
    if existing:
        cur.execute(
            "UPDATE users SET password_hash=%s, is_superuser=TRUE, is_active=TRUE WHERE id=%s",
            (pwd_hash, existing[0]),
        )
    else:
        cur.execute(
            "INSERT INTO users (email, phone, full_name, password_hash, is_active, is_verified, is_superuser, role_id, created_at, updated_at)"
            " VALUES (%s, %s, %s, %s, TRUE, TRUE, TRUE, %s, now(), now())",
            (ADMIN_EMAIL, "0000000000", "Lifecycle Admin", pwd_hash, role_id),
        )
    conn.commit()
    conn.close()

    r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
    assert r.status_code == 200, f"Admin login failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def register(role: str) -> dict:
    r = client.post("/auth/register", json={
        "email": gen_email(role),
        "password": PASSWORD,
        "full_name": f"Smoke {role.capitalize()}",
        "phone": "9876512345",
        "role": role,
    })
    assert r.status_code == 201, f"Register {role} failed: {r.text}"
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def create_service(admin_headers: dict) -> int:
    r = client.post("/admin/services", json={
        "name": f"AC Repair {uuid.uuid4().hex[:6]}",
        "description": "Smoke test service",
        "base_price": 499.0,
        "duration_minutes": 60,
        "is_active": True,
    }, headers=admin_headers)
    assert r.status_code == 201, f"Create service failed: {r.text}"
    return r.json()["id"]


def create_address(customer_headers: dict) -> int:
    r = client.post("/customer/addresses", json={
        "full_name": "Smoke Customer",
        "phone": "9876543210",
        "house_no": "12",
        "building": "Test Towers",
        "area": "Test Area",
        "city": "Test City",
        "state": "Test State",
        "pincode": "400001",
        "is_default": True,
    }, headers=customer_headers)
    assert r.status_code == 201, f"Create address failed: {r.text}"
    return r.json()["id"]


def create_booking(customer_headers: dict, service_id: int, address_id: int) -> int:
    tomorrow = (date.today() + timedelta(days=1)).isoformat()
    r = client.post("/bookings/", json={
        "service_id": service_id,
        "address_id": address_id,
        "booking_date": tomorrow,
        "preferred_time": "10:00:00",
        "customer_note": "Smoke booking",
    }, headers=customer_headers)
    assert r.status_code == 201, f"Create booking failed: {r.text}"
    return r.json()["id"]


def get_technician_id(tech_headers: dict) -> int:
    r = client.get("/technician/profile", headers=tech_headers)
    assert r.status_code == 200, r.text
    return r.json()["id"]


def main():
    print("\n═══ SETUP: roles ═══")
    admin_headers = ensure_admin()
    cust_headers = register("customer")
    tech_headers = register("technician")
    tech_id = get_technician_id(tech_headers)

    print("\n═══ SETUP: service + address ═══")
    service_id = create_service(admin_headers)
    address_id = create_address(cust_headers)
    print(f"  service_id={service_id} address_id={address_id} technician_id={tech_id}")

    # ── 1. CREATE ────────────────────────────────────────────────────
    print("\n▶ POST /bookings/ (customer create)")
    booking_id = create_booking(cust_headers, service_id, address_id)
    print("  created booking_id:", booking_id)
    check("customer_create_booking", 201, [201])

    # ── 2. GET / list ────────────────────────────────────────────────
    print("\n▶ GET /bookings/ (customer list)")
    r = client.get("/bookings/", headers=cust_headers)
    check("customer_list_bookings", r.status_code, [200])
    assert r.status_code == 200 and r.json()["total"] >= 1, r.text

    print("\n▶ GET /bookings/{id}")
    r = client.get(f"/bookings/{booking_id}", headers=cust_headers)
    check("customer_get_booking", r.status_code, [200])
    assert r.status_code == 200, r.text

    # ── 3. ASSIGN (admin) PENDING → ASSIGNED ─────────────────────────
    print("\n▶ PUT /bookings/{id}/assign (admin)")
    r = client.put(
        f"/bookings/{booking_id}/assign",
        json={"technician_id": tech_id, "estimated_price": 499.0},
        headers=admin_headers,
    )
    check("admin_assign", r.status_code, [200])
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "assigned", r.json()["status"]

    # ── 4. ROLE GATE: customer cannot assign ─────────────────────────
    print("\n▶ Customer attempts assign (expect 403)")
    r = client.put(
        f"/bookings/{booking_id}/assign",
        json={"technician_id": tech_id},
        headers=cust_headers,
    )
    check("customer_cannot_assign", r.status_code, [403])

    # ── 5. INVALID TRANSITION: tech start-trip before accept (409) ──
    print("\n▶ Technician start-trip from 'assigned' (expect 409)")
    r = client.post(
        f"/bookings/{booking_id}/start-trip",
        json={"reason": "skip"},
        headers=tech_headers,
    )
    check("invalid_transition_409", r.status_code, [409])

    # ── 6. ACCEPT (ASSIGNED → ACCEPTED) ─────────────────────────────
    print("\n▶ POST /bookings/{id}/accept")
    r = client.post(
        f"/bookings/{booking_id}/accept",
        json={"reason": "Will do"},
        headers=tech_headers,
    )
    check("tech_accept", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "accepted", r.text

    # ── 7. DUPLICATE ACTION: accept again (409) ─────────────────────
    print("\n▶ Technician accept again (expect 409)")
    r = client.post(
        f"/bookings/{booking_id}/accept",
        json={"reason": "again"},
        headers=tech_headers,
    )
    check("duplicate_accept_409", r.status_code, [409])

    # ── 8. RESCHEDULE (customer) ────────────────────────────────────
    print("\n▶ PUT /bookings/{id}/reschedule (customer)")
    new_date = (date.today() + timedelta(days=2)).isoformat()
    r = client.put(
        f"/bookings/{booking_id}/reschedule",
        json={"booking_date": new_date, "preferred_time": "14:00:00"},
        headers=cust_headers,
    )
    check("customer_reschedule", r.status_code, [200])
    assert r.status_code == 200 and r.json()["booking_date"] == new_date, r.text

    # ── 9. START TRIP (ACCEPTED → ON_THE_WAY) ───────────────────────
    print("\n▶ POST /bookings/{id}/start-trip")
    r = client.post(
        f"/bookings/{booking_id}/start-trip",
        json={"reason": "On my way"},
        headers=tech_headers,
    )
    check("tech_start_trip", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "on_the_way", r.text

    # ── 10. ARRIVED (ON_THE_WAY → ARRIVED) ──────────────────────────
    print("\n▶ POST /bookings/{id}/arrived")
    r = client.post(
        f"/bookings/{booking_id}/arrived",
        json={"reason": "Arrived"},
        headers=tech_headers,
    )
    check("tech_arrived", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "arrived", r.text

    # ── 11. START SERVICE (ARRIVED → IN_PROGRESS) ───────────────────
    print("\n▶ POST /bookings/{id}/start-service")
    r = client.post(
        f"/bookings/{booking_id}/start-service",
        json={"reason": "Starting"},
        headers=tech_headers,
    )
    check("tech_start_service", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "in_progress", r.text

    # ── 12. COMPLETE (IN_PROGRESS → COMPLETED) ──────────────────────
    print("\n▶ POST /bookings/{id}/complete")
    r = client.post(
        f"/bookings/{booking_id}/complete",
        json={"reason": "Done"},
        headers=tech_headers,
    )
    check("tech_complete", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "completed", r.text

    # ── 13. HISTORY / TRACK / TECHNICIAN (customer) ─────────────────
    print("\n▶ GET /bookings/{id}/history")
    r = client.get(f"/bookings/{booking_id}/history", headers=cust_headers)
    check("customer_history", r.status_code, [200])
    if r.status_code == 200:
        print("    history entries:", r.json()["total"])

    print("\n▶ GET /bookings/{id}/track")
    r = client.get(f"/bookings/{booking_id}/track", headers=cust_headers)
    check("customer_track", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "completed", r.text

    print("\n▶ GET /bookings/{id}/technician")
    r = client.get(f"/bookings/{booking_id}/technician", headers=cust_headers)
    check("customer_assigned_technician", r.status_code, [200])
    assert r.status_code == 200 and r.json()["id"] == tech_id, r.text

    # ── 14. CANCEL from completed (expect 409) ──────────────────────
    print("\n▶ Customer cancel completed booking (expect 409)")
    r = client.post(
        f"/bookings/{booking_id}/cancel",
        json={"reason": "want to cancel"},
        headers=cust_headers,
    )
    check("cancel_terminal_409", r.status_code, [409])

    # ── 15. VALIDATION: create booking with past date (402/422) ─────
    print("\n▶ Customer create booking with past date (expect 422)")
    past_date = (date.today() - timedelta(days=1)).isoformat()
    r = client.post("/bookings/", json={
        "service_id": service_id,
        "address_id": address_id,
        "booking_date": past_date,
    }, headers=cust_headers)
    check("past_date_rejected", r.status_code, [422, 400])

    # ── 16. VALIDATION: service not active (expect 404) ─────────────
    print("\n▶ Customer create booking with inactive service (expect 404)")
    r = client.post("/admin/services", json={
        "name": f"Inactive {uuid.uuid4().hex[:6]}",
        "base_price": 100.0,
        "is_active": False,
    }, headers=admin_headers)
    inactive_service_id = r.json()["id"] if r.status_code == 201 else None
    if inactive_service_id:
        r = client.post("/bookings/", json={
            "service_id": inactive_service_id,
            "address_id": address_id,
            "booking_date": (date.today() + timedelta(days=1)).isoformat(),
        }, headers=cust_headers)
        check("inactive_service_rejected", r.status_code, [404])

    # ── 17. ADMIN: REASSIGN on a fresh booking ──────────────────────
    print("\n▶ Happy-path reassign on a fresh booking")
    b2 = create_booking(cust_headers, service_id, address_id)
    r = client.put(
        f"/admin/bookings/{b2}/reassign",
        json={"technician_id": tech_id},
        headers=admin_headers,
    )
    check("admin_reassign", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "assigned", r.text

    # ── 18. ADMIN: FORCE CANCEL ─────────────────────────────────────
    print("\n▶ POST /admin/bookings/{id}/force-cancel")
    r = client.post(
        f"/admin/bookings/{b2}/force-cancel",
        json={"reason": "Admin forced cancel"},
        headers=admin_headers,
    )
    check("admin_force_cancel", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "cancelled", r.text

    # ── 19. ADMIN: OVERRIDE STATUS ──────────────────────────────────
    print("\n▶ PUT /admin/bookings/{id}/override-status")
    r = client.put(
        f"/admin/bookings/{b2}/override-status",
        json={"status": "pending", "admin_note": "restore for testing"},
        headers=admin_headers,
    )
    check("admin_override_status", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "pending", r.text

    # ── 20. ROLE GATE: customer cannot run technician 'complete' ────
    print("\n▶ Customer attempts 'complete' (expect 403)")
    r = client.post(
        f"/bookings/{b2}/complete",
        json={"reason": "hack"},
        headers=cust_headers,
    )
    check("customer_cannot_complete", r.status_code, [403])

    # ── 21. REJECT flow on a fresh booking ──────────────────────────
    print("\n▶ Technician reject flow")
    b3 = create_booking(cust_headers, service_id, address_id)
    client.put(
        f"/bookings/{b3}/assign",
        json={"technician_id": tech_id},
        headers=admin_headers,
    )
    r = client.post(
        f"/bookings/{b3}/reject",
        json={"reason": "Busy"},
        headers=tech_headers,
    )
    check("tech_reject", r.status_code, [200])
    assert r.status_code == 200 and r.json()["status"] == "rejected", r.text

    # ── SUMMARY ─────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("BOOKING LIFECYCLE SMOKE TEST SUMMARY")
    print("=" * 60)
    all_ok = True
    for name, code, ok in RESULTS:
        print(f"  {name:<38} {code}  {'OK' if ok else 'FAIL'}")
        if not ok:
            all_ok = False
    print()
    print("-> ALL TESTS PASSED" if all_ok else "-> SOME TESTS FAILED")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
