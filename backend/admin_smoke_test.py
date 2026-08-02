"""
Admin dashboard + payment verify smoke test.

Creates/uses a dedicated test admin account so we can validate
admin-only endpoints without depending on the pre-seeded admin password.
"""
import sys

sys.path.insert(0, r"c:/Users/prath/OneDrive/Desktop/HomiQ/homiq/backend")

import psycopg
from fastapi.testclient import TestClient

from app.main import app
from app.security.passwords import hash_password

client = TestClient(app)

ADMIN_EMAIL = "smoke_admin@homiq.com"
ADMIN_PASSWORD = "Admin@12345"

# ── Ensure a known test admin exists in DB ─────────────────────────────
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
    user_id = existing[0]
else:
    cur.execute(
        "INSERT INTO users (email, phone, full_name, password_hash, is_active, is_verified, is_superuser, role_id, created_at, updated_at)"
        " VALUES (%s, %s, %s, %s, TRUE, TRUE, TRUE, %s, now(), now()) RETURNING id",
        (ADMIN_EMAIL, "0000000000", "Smoke Admin", pwd_hash, role_id),
    )
    user_id = cur.fetchone()[0]
conn.commit()
conn.close()

print(f"▶ Admin login ({ADMIN_EMAIL})")
r = client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
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
conn = psycopg.connect("postgresql://postgres:postgres123@localhost:5432/homiq_db")
cur = conn.cursor()
cur.execute("SELECT razorpay_order_id FROM payments WHERE razorpay_order_id IS NOT NULL ORDER BY id DESC LIMIT 1")
row = cur.fetchone()
conn.close()
if row:
    order_id = row[0]
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

