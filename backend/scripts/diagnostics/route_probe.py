"""
Route probe: registers users of each role and hits every registered route
to identify 500-level errors and other broken endpoints.
"""
import datetime
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
PASSWORD = "Test@1234"


def gen_email(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:10]}@example.com"


def register(role, prefix):
    r = client.post("/auth/register", json={
        "email": gen_email(prefix),
        "password": PASSWORD,
        "full_name": f"Probe {prefix} {role}",
        "phone": "9876500000",
        "role": role,
    })
    assert r.status_code == 201, f"register {role} failed: {r.text[:300]}"
    tok = r.json()["access_token"]
    return {"Authorization": f"Bearer {tok}"}


def future_date():
    return (datetime.date.today() + datetime.timedelta(days=5)).isoformat()


def probe(method, path, headers=None, json=None, ok_codes=(200, 201, 400, 401, 403, 404, 409, 422)):
    """Only reports 5xx errors (server bugs)."""
    kw = {}
    if headers:
        kw["headers"] = headers
    if json is not None:
        kw["json"] = json
    r = client.request(method, path, **kw)
    tag = f"{method} {path}"
    if r.status_code >= 500:
        print(f"  [500-ERROR] {tag} -> {r.status_code} {r.text[:300]}")
        return (tag, r.status_code)
    return None


def main():
    print("=" * 60)
    print("ROUTE PROBE (5xx hunt)")
    print("=" * 60)
    failures = []

    customer = register("customer", "rp")
    admin = register("admin", "rp")
    tech = register("technician", "rp")

    # Service + address needed for booking flows
    svc_r = client.get("/services/")
    service_id = svc_r.json()["items"][0]["id"] if svc_r.status_code == 200 and svc_r.json()["items"] else 1

    addr_r = client.post("/customer/addresses", headers=customer, json={
        "full_name": "Probe", "phone": "9876500000", "house_no": "1",
        "area": "Indiranagar", "city": "Bengaluru", "state": "Karnataka",
        "pincode": "560038", "is_default": True,
    })
    address_id = addr_r.json()["id"] if addr_r.status_code == 201 else 1

    b = client.post("/bookings/", headers=customer, json={
        "service_id": service_id, "address_id": address_id,
        "booking_date": future_date(), "preferred_time": "10:30:00",
        "estimated_price": 499.0,
    })
    booking_id = b.json()["id"] if b.status_code == 201 else 1

    pay = client.post("/payments/create-order", headers=customer, json={"booking_id": booking_id})
    payment_id = pay.json()["payment_id"] if pay.status_code == 200 else 1

    # ── auth ───────────────────────────────────────────────────────────
    probe("POST", "/auth/refresh", json={})
    probe("POST", "/auth/forgot-password", json={"email": gen_email("rp")})
    probe("POST", "/auth/reset-password", json={"email": gen_email("rp"), "otp": "123456", "new_password": PASSWORD})

    # ── bookings ───────────────────────────────────────────────────────
    probe("GET", "/bookings/", headers=customer)
    probe("GET", f"/bookings/{booking_id}", headers=customer)
    probe("PUT", f"/bookings/{booking_id}", headers=customer, json={"customer_note": "x"})
    probe("DELETE", f"/bookings/{booking_id}", headers=customer)
    probe("PUT", f"/bookings/{booking_id}/status", headers=admin, json={"status": "confirmed"})
    probe("PUT", f"/bookings/{booking_id}/assign", headers=admin, json={"technician_id": 1})

    # ── customer ───────────────────────────────────────────────────────
    probe("GET", "/customer/profile", headers=customer)
    probe("PUT", "/customer/profile", headers=customer, json={"full_name": "Probe Updated"})
    probe("GET", "/customer/addresses", headers=customer)
    probe("GET", f"/customer/addresses/{address_id}", headers=customer)
    probe("PUT", f"/customer/addresses/{address_id}", headers=customer, json={"landmark": "x"})
    probe("PUT", f"/customer/addresses/{address_id}/default", headers=customer)
    probe("DELETE", f"/customer/addresses/{address_id}", headers=customer)
    probe("GET", "/customer/dashboard", headers=customer)

    # ── technician ─────────────────────────────────────────────────────
    probe("GET", "/technician/profile", headers=tech)
    probe("PUT", "/technician/profile", headers=tech, json={"full_name": "Tech Probe"})
    probe("GET", "/technician/", headers=admin)
    probe("GET", "/technician/dashboard", headers=tech)

    # ── services ───────────────────────────────────────────────────────
    probe("GET", "/services/categories")
    probe("GET", "/services/categories/1")
    probe("POST", "/services/categories", headers=admin, json={"name": "ProbeCat", "description": "x"})
    probe("PUT", "/services/categories/1", headers=admin, json={"name": "ProbeCat2"})
    probe("DELETE", "/services/categories/1", headers=admin)
    probe("GET", "/services/")
    probe("GET", "/services/1")
    probe("POST", "/services/", headers=admin, json={
        "name": "ProbeSvc", "category_id": 1, "price": 100.0,
        "description": "x", "duration_minutes": 30,
    })
    probe("PUT", "/services/1", headers=admin, json={"name": "ProbeSvc2"})
    probe("DELETE", "/services/1", headers=admin)

    # ── payments ───────────────────────────────────────────────────────
    probe("GET", "/payments/", headers=customer)
    probe("GET", f"/payments/{payment_id}", headers=customer)
    probe("POST", f"/payments/{payment_id}/refund", headers=admin, json={})

    # ── coupons ────────────────────────────────────────────────────────
    probe("POST", "/coupons/", headers=admin, json={
        "code": f"PROBE{uuid.uuid4().hex[:6].upper()}", "discount_type": "percentage",
        "discount_value": 10.0, "min_order_amount": 100.0,
    })
    probe("GET", "/coupons/", headers=admin)
    probe("GET", "/coupons/1", headers=admin)
    probe("GET", "/coupons/code/PROBE", headers=customer)
    probe("PUT", "/coupons/1", headers=admin, json={"discount_value": 15.0})
    probe("DELETE", "/coupons/1", headers=admin)
    probe("POST", "/coupons/validate", headers=customer, json={"code": "PROBE", "amount": 200.0})
    probe("POST", "/coupons/apply", headers=customer, json={"code": "PROBE", "booking_id": booking_id})

    # ── invoices ───────────────────────────────────────────────────────
    probe("POST", "/invoices/", headers=admin, json={
        "booking_id": booking_id, "subtotal": 499.0, "discount_amount": 0,
        "tax_percentage": 18, "total_amount": 588.82, "amount_paid": 0,
    })
    probe("GET", "/invoices/", headers=customer)
    probe("GET", "/invoices/1", headers=admin)
    probe("GET", "/invoices/number/HMQ-1", headers=admin)
    probe("PUT", "/invoices/1", headers=admin, json={"notes": "x"})
    probe("POST", "/invoices/1/issue", headers=admin)
    probe("DELETE", "/invoices/1", headers=admin)

    # ── reviews ────────────────────────────────────────────────────────
    probe("POST", "/reviews/", headers=customer, json={
        "booking_id": booking_id, "rating": 5, "comment": "Great",
    })
    probe("GET", "/reviews/", headers=customer)
    probe("GET", "/reviews/1", headers=customer)
    probe("PUT", "/reviews/1", headers=customer, json={"rating": 4})
    probe("DELETE", "/reviews/1", headers=customer)
    probe("GET", "/reviews/technician/1", headers=customer)

    # ── notifications ──────────────────────────────────────────────────
    probe("GET", "/notifications/", headers=customer)
    probe("POST", "/notifications/", headers=admin, json={
        "user_id": 1, "title": "Probe", "message": "x", "notification_type": "general",
    })
    probe("PUT", "/notifications/1/read", headers=customer)
    probe("PUT", "/notifications/read-all", headers=customer)
    probe("POST", "/notifications/read-multiple", headers=customer, json={"ids": [1]})
    probe("DELETE", "/notifications/1", headers=customer)
    probe("DELETE", "/notifications/", headers=customer)

    # ── tracking ───────────────────────────────────────────────────────
    probe("PUT", f"/tracking/{booking_id}/location", headers=tech, json={"latitude": 12.97, "longitude": 77.59})
    probe("GET", f"/tracking/{booking_id}/location", headers=customer)
    probe("GET", f"/tracking/{booking_id}/history", headers=customer)
    probe("GET", "/tracking/me/location", headers=tech)

    # ── admin ──────────────────────────────────────────────────────────
    probe("GET", "/admin/dashboard", headers=admin)
    probe("GET", "/admin/bookings", headers=admin)
    probe("GET", f"/admin/bookings/{booking_id}", headers=admin)
    probe("PUT", f"/admin/bookings/{booking_id}/assign", headers=admin, json={"technician_id": 1})
    probe("PUT", f"/admin/bookings/{booking_id}/status", headers=admin, json={"status": "confirmed"})
    probe("POST", "/admin/services", headers=admin, json={"name": "AdminSvc", "category_id": 1, "price": 50.0})
    probe("PUT", "/admin/services/1", headers=admin, json={"name": "AdminSvc2"})
    probe("DELETE", "/admin/services/1", headers=admin)
    probe("POST", "/admin/categories", headers=admin, json={"name": "AdminCat"})
    probe("PUT", "/admin/categories/1", headers=admin, json={"name": "AdminCat2"})
    probe("DELETE", "/admin/categories/1", headers=admin)
    probe("POST", "/admin/coupons", headers=admin, json={
        "code": "ADMINC1", "discount_type": "percentage", "discount_value": 5.0,
    })
    probe("GET", "/admin/coupons", headers=admin)
    probe("PUT", "/admin/coupons/1", headers=admin, json={"discount_value": 6.0})
    probe("DELETE", "/admin/coupons/1", headers=admin)
    probe("POST", "/admin/invoices", headers=admin, json={"booking_id": booking_id, "total_amount": 100.0})
    probe("GET", "/admin/invoices", headers=admin)
    probe("PUT", "/admin/invoices/1", headers=admin, json={"notes": "x"})
    probe("DELETE", "/admin/invoices/1", headers=admin)
    probe("GET", "/admin/reviews", headers=admin)
    probe("DELETE", "/admin/reviews/1", headers=admin)
    probe("GET", "/admin/reports/revenue", headers=admin)
    probe("GET", "/admin/reports/bookings", headers=admin)
    probe("GET", "/admin/reports/technicians", headers=admin)
    probe("GET", "/admin/analytics/overview", headers=admin)
    probe("GET", "/admin/analytics/customers", headers=admin)
    probe("GET", "/admin/analytics/bookings", headers=admin)
    probe("GET", "/admin/analytics/revenue", headers=admin)

    # ── misc ───────────────────────────────────────────────────────────
    probe("GET", "/health")
    probe("GET", "/dashboard", headers=customer)

    print("\n" + "=" * 60)
    if failures:
        print(f"FAILURES: {len(failures)} 5xx responses")
        for tag, code in failures:
            print(f"  {tag} -> {code}")
    else:
        print("NO 5xx ERRORS FOUND — all routes responded without server errors")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

