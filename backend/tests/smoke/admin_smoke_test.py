"""
Admin dashboard + payment verify smoke test.

Creates/uses a dedicated test admin account so we can validate
admin-only endpoints without depending on the pre-seeded admin password.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from fastapi.testclient import TestClient

from app.database.session import SessionLocal
from app.main import app
from app.models.auth import Role, User
from app.models.payments import Payment
from app.security.passwords import hash_password

client = TestClient(app)

ADMIN_EMAIL = "smoke_admin@homiq.com"
ADMIN_PASSWORD = "Admin@12345"

# ── Ensure a known test admin exists in DB ─────────────────────────────
db = SessionLocal()
try:
    role = db.query(Role).filter(Role.name == "admin").first()
    if not role:
        role = Role(name="admin", description="Admin role")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    pwd_hash = hash_password(ADMIN_PASSWORD)
    if user:
        user.password_hash = pwd_hash
        user.is_superuser = True
        user.is_active = True
        user.role_id = role.id
    else:
        user = User(
            email=ADMIN_EMAIL,
            phone="0000000000",
            full_name="Smoke Admin",
            password_hash=pwd_hash,
            is_active=True,
            is_verified=True,
            is_superuser=True,
            role_id=role.id,
        )
        db.add(user)
    db.commit()
finally:
    db.close()

print(f"▶ Admin login ({ADMIN_EMAIL})")
r = client.post("/auth/login", json={"identifier": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
print(r.status_code)
assert r.status_code == 200, f"Admin login failed: {r.text}"
headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

print("\n▶ GET /admin/dashboard")
d = client.get("/admin/dashboard", headers=headers)
print(d.status_code, str(d.text)[:500])
assert d.status_code == 200, f"Admin dashboard failed: {d.text}"
print("  stats keys:", list(d.json().get("stats", {}).keys()))

print("\n▶ GET /dashboard (role-aware admin)")
dd = client.get("/dashboard", headers=headers)
print(dd.status_code)
assert dd.status_code == 200

print("\n▶ POST /payments/verify (invalid signature → expect 400)")
db = SessionLocal()
try:
    payment = (
        db.query(Payment)
        .filter(Payment.razorpay_order_id.isnot(None))
        .order_by(Payment.id.desc())
        .first()
    )
    order_id = payment.razorpay_order_id if payment else None
finally:
    db.close()

if order_id:
    r = client.post("/payments/verify", json={
        "razorpay_order_id": order_id,
        "razorpay_payment_id": "pay_invalid_test",
        "razorpay_signature": "invalid_signature_value_0000",
    }, headers=headers)
    print(r.status_code, r.text[:300])
    assert r.status_code == 400, f"Invalid signature should be 400, got {r.status_code}"
    print("  ✓ invalid signature rejected correctly")
else:
    print("  no payment orders found — skipping verify-negative test")

print("\n▶ GET /admin/analytics/overview")
a = client.get("/admin/analytics/overview", headers=headers)
print(a.status_code, str(a.text)[:300])
assert a.status_code == 200, f"Analytics overview failed: {a.text}"

print("\nALL ADMIN/POLICY TESTS PASSED")

