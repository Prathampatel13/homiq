"""
Master Systematic Endpoint & Workflow Verification Suite for HomiQ.

Tests every API across all roles (Customer, Technician, Company, Admin)
following strict dependency order and authentic lifecycle flows.
Captures detailed diagnostic results for report generation.
"""

from __future__ import annotations

import base64
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import select, text

from app.database.session import SessionLocal
from app.main import app
from app.models.addresses import CustomerAddress
from app.models.auth import Role, User
from app.models.bookings import Booking, BookingStatus
from app.models.coupons import Coupon
from app.models.invoices import Invoice
from app.models.jobs import JobApplication, JobPost
from app.models.media import MediaAsset, MediaAssetType
from app.models.payments import Payment
from app.models.reviews import Review
from app.models.services import Category, Service
from app.models.users import Company, Customer, Technician
from app.security.passwords import hash_password
from app.security.tokens import create_access_token

# ── Test Results Repository ──────────────────────────────────────────────────
TEST_RESULTS = []


def record_result(
    endpoint: str,
    method: str,
    request_data: Any,
    expected_status: int,
    actual_status: int,
    failure_reason: str = "None",
    code_changed: str = "None",
    final_result: str = "PASSED",
):
    TEST_RESULTS.append({
        "endpoint": endpoint,
        "method": method,
        "request_data": request_data,
        "expected_status": expected_status,
        "actual_status": actual_status,
        "failure_reason": failure_reason,
        "code_changed": code_changed,
        "final_result": final_result,
    })


VALID_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
VALID_PDF = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000098 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF\n"


def provision_actor(
    db,
    email: str,
    full_name: str,
    role_name: str,
    is_superuser: bool = False,
) -> tuple[User, str]:
    """Provisions an isolated actor and generates a valid JWT token."""
    role = db.scalar(select(Role).where(Role.name == role_name))
    if not role:
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        db.commit()
        db.refresh(role)

    user = db.scalar(select(User).where(User.email == email))
    if not user:
        user = User(
            email=email,
            phone="+919999999999",
            full_name=full_name,
            password_hash=hash_password("Pass@1234!"),
            is_active=True,
            is_verified=True,
            is_superuser=is_superuser,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        user.is_superuser = is_superuser
        user.is_active = True
        user.is_verified = True
        user.role_id = role.id
    from app.crud.user import UserCRUD
    crud = UserCRUD(db)
    tokens = crud.create_tokens(user)
    return user, tokens["access_token"], tokens["refresh_token"]


def run_all_systematic_tests():
    print("=" * 80)
    print("HOMIQ COMPREHENSIVE ENDPOINT & WORKFLOW VERIFICATION SUITE")
    print("=" * 80)

    client = TestClient(app)
    db = SessionLocal()

    try:
        # Provision actors
        cust_user, cust_tok, cust_ref = provision_actor(db, "systest_cust@homiq.test", "Customer Tester", "customer")
        tech_user, tech_tok, tech_ref = provision_actor(db, "systest_tech@homiq.test", "Technician Tester", "technician")
        comp_user, comp_tok, comp_ref = provision_actor(db, "systest_comp@homiq.test", "Company Tester", "company")
        admin_user, admin_tok, admin_ref = provision_actor(db, "systest_admin@homiq.test", "Admin Tester", "admin", is_superuser=True)

        cust_h = {"Authorization": f"Bearer {cust_tok}"}
        tech_h = {"Authorization": f"Bearer {tech_tok}"}
        comp_h = {"Authorization": f"Bearer {comp_tok}"}
        admin_h = {"Authorization": f"Bearer {admin_tok}"}

        # Ensure profiles exist
        cust_profile = db.scalar(select(Customer).where(Customer.user_id == cust_user.id))
        if not cust_profile:
            cust_profile = Customer(user_id=cust_user.id, phone="+919999999999", city="Bengaluru")
            db.add(cust_profile)
            db.commit()
            db.refresh(cust_profile)

        tech_profile = db.scalar(select(Technician).where(Technician.user_id == tech_user.id))
        if not tech_profile:
            tech_profile = Technician(user_id=tech_user.id, specialization="AC Specialist", experience_years=4, availability=True, is_online=True)
            db.add(tech_profile)
            db.commit()
            db.refresh(tech_profile)

        comp_profile = db.scalar(select(Company).where(Company.user_id == comp_user.id))
        if not comp_profile:
            comp_profile = Company(
                user_id=comp_user.id,
                company_name="HomiQ Pro Services Ltd",
                industry="Home Services",
                website="https://homiq.com",
            )
            db.add(comp_profile)
            db.commit()
            db.refresh(comp_profile)

        # ── 1. AUTHENTICATION & SESSION WORKFLOW ──────────────────────────────
        print("\n[1/14] Testing Authentication & Session APIs...")
        
        # 1a. /auth/me
        r = client.get("/auth/me", headers=cust_h)
        record_result("/auth/me", "GET", None, 200, r.status_code)
        assert r.status_code == 200, f"/auth/me failed: {r.text}"
        print("  [OK] GET /auth/me")

        # 1b. /users/me
        r = client.get("/users/me", headers=cust_h)
        record_result("/users/me", "GET", None, 200, r.status_code)
        assert r.status_code == 200, f"/users/me failed: {r.text}"
        print("  [OK] GET /users/me")

        # 1c. /auth/refresh
        r = client.post(f"/auth/refresh?refresh_token={cust_ref}")
        record_result("/auth/refresh", "POST", {"refresh_token": "..."}, 200, r.status_code)
        assert r.status_code == 200, f"/auth/refresh failed: {r.text}"
        print("  [OK] POST /auth/refresh")

        # ── 2. SERVICES & CATEGORIES LIFECYCLE ───────────────────────────────
        print("\n[2/14] Testing Services & Categories APIs...")
        
        # 2a. Admin Create Category
        cat_payload = {"name": f"Testing Cat {uuid4().hex[:4]}", "description": "Automated test category"}
        r = client.post("/services/categories", headers=admin_h, json=cat_payload)
        record_result("/services/categories", "POST", cat_payload, 200, r.status_code)
        assert r.status_code in [200, 201], f"Create category failed: {r.text}"
        category_id = r.json()["id"]
        print(f"  [OK] POST /services/categories (ID: {category_id})")

        # 2b. List Categories
        r = client.get("/services/categories")
        record_result("/services/categories", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /services/categories")

        # 2c. Admin Create Service
        srv_payload = {
            "name": f"Comprehensive AC Checkup {uuid4().hex[:4]}",
            "category_id": category_id,
            "base_price": 599.0,
            "duration_minutes": 45,
            "description": "Thorough inspection of coils, filter, and gas pressure.",
        }
        r = client.post("/services/", headers=admin_h, json=srv_payload)
        record_result("/services/", "POST", srv_payload, 200, r.status_code)
        assert r.status_code in [200, 201], f"Create service failed: {r.text}"
        service_id = r.json()["id"]
        print(f"  [OK] POST /services/ (ID: {service_id})")

        # 2d. Get Service by ID
        r = client.get(f"/services/{service_id}")
        record_result(f"/services/{service_id}", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /services/{service_id}")

        # 2e. List Services (Public with filter)
        r = client.get(f"/services/?category_id={category_id}")
        record_result("/services/?category_id=...", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /services/?category_id=...")

        # ── 3. CUSTOMER PROFILE & ADDRESSES WORKFLOW ─────────────────────────
        print("\n[3/14] Testing Customer Profile & Address APIs...")

        # 3a. Add Customer Address
        addr_payload = {
            "full_name": "Customer Tester",
            "phone": "+919999999999",
            "house_no": "Flat 304, Palm Heights",
            "area": "Koramangala",
            "city": "Bengaluru",
            "state": "Karnataka",
            "pincode": "560034",
            "is_default": True,
        }
        r = client.post("/customer/addresses", headers=cust_h, json=addr_payload)
        record_result("/customer/addresses", "POST", addr_payload, 200, r.status_code)
        assert r.status_code in [200, 201], f"Add address failed: {r.text}"
        address_id = r.json()["id"]
        print(f"  [OK] POST /customer/addresses (ID: {address_id})")

        # 3b. List Customer Addresses
        r = client.get("/customer/addresses", headers=cust_h)
        record_result("/customer/addresses", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /customer/addresses")

        # 3c. Get Customer Profile
        r = client.get("/customer/profile", headers=cust_h)
        record_result("/customer/profile", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /customer/profile")

        # ── 4. TECHNICIAN PROFILE & DASHBOARD WORKFLOW ───────────────────────
        print("\n[4/14] Testing Technician Profile & Dashboard APIs...")

        # 4a. Get Technician Profile
        r = client.get("/technician/profile", headers=tech_h)
        record_result("/technician/profile", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /technician/profile")

        # 4b. Update Availability
        avail_payload = {"availability": True, "is_online": True}
        r = client.put("/technician/availability", headers=tech_h, json=avail_payload)
        record_result("/technician/availability", "PUT", avail_payload, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] PUT /technician/availability")

        # 4c. Technician Dashboard
        r = client.get("/technician/dashboard", headers=tech_h)
        record_result("/technician/dashboard", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /technician/dashboard")

        # 4d. Technician Earnings
        r = client.get("/technician/earnings", headers=tech_h)
        record_result("/technician/earnings", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /technician/earnings")

        # ── 5. COMPANY PROFILE & RECRUITMENT WORKFLOW ────────────────────────
        print("\n[5/14] Testing Company & Job Recruitment APIs...")

        # 5a. Get Company Profile
        r = client.get("/company/profile", headers=comp_h)
        record_result("/company/profile", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /company/profile")

        # 5b. Company Post a Job
        job_payload = {
            "title": f"Master Electrician {uuid4().hex[:4]}",
            "description": "Seeking expert residential wiring technician.",
            "job_type": "full_time",
            "location": "Bengaluru",
            "salary_min": 30000,
            "salary_max": 45000,
            "experience_required_years": 3,
        }
        r = client.post("/jobs/", headers=comp_h, json=job_payload)
        record_result("/jobs/", "POST", job_payload, 201, r.status_code)
        assert r.status_code == 201, f"Post job failed: {r.text}"
        job_id = r.json()["id"]
        print(f"  [OK] POST /jobs/ (ID: {job_id})")

        # 5c. List Jobs (Technician discovering jobs)
        r = client.get("/jobs/", headers=tech_h)
        record_result("/jobs/", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /jobs/")

        # 5d. Technician Apply for Job
        app_payload = {"cover_letter": "I have 4 years experience in residential wiring."}
        r = client.post(f"/jobs/{job_id}/apply", headers=tech_h, json=app_payload)
        record_result(f"/jobs/{job_id}/apply", "POST", app_payload, 201, r.status_code)
        assert r.status_code == 201, f"Apply job failed: {r.text}"
        application_id = r.json()["id"]
        print(f"  [OK] POST /jobs/{job_id}/apply (App ID: {application_id})")

        # 5e. Company List Applications
        r = client.get(f"/jobs/{job_id}/applications", headers=comp_h)
        record_result(f"/jobs/{job_id}/applications", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /jobs/{job_id}/applications")

        # 5f. Company Update Application Status
        status_payload = {"status": "shortlisted"}
        r = client.put(f"/jobs/applications/{application_id}/status", headers=comp_h, json=status_payload)
        record_result(f"/jobs/applications/{application_id}/status", "PUT", status_payload, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] PUT /jobs/applications/{application_id}/status")

        # ── 6. BOOKING & SMARTVERIFY LIFECYCLE ────────────────────────────────
        print("\n[6/14] Testing Booking Lifecycle & SmartVerify Handshake...")

        # 6a. Customer Create Booking
        b_payload = {
            "service_id": service_id,
            "address_id": address_id,
            "booking_date": (datetime.now(timezone.utc) + timedelta(days=1)).date().isoformat(),
            "preferred_time": "14:00:00",
            "estimated_price": 599.0,
            "customer_note": "Please call 10 mins before arrival.",
        }
        r = client.post("/bookings/", headers=cust_h, json=b_payload)
        record_result("/bookings/", "POST", b_payload, 201, r.status_code)
        assert r.status_code == 201, f"Create booking failed: {r.text}"
        booking_data = r.json()
        booking_id = booking_data["id"]
        print(f"  [OK] POST /bookings/ (Booking ID: {booking_id})")

        # Assign technician to booking in DB for lifecycle progression
        booking_record = db.get(Booking, booking_id)
        booking_record.technician_id = tech_profile.id
        booking_record.status = BookingStatus.ASSIGNED
        db.commit()

        # 6b. Technician Accept Booking
        r = client.post(f"/bookings/{booking_id}/accept", headers=tech_h)
        record_result(f"/bookings/{booking_id}/accept", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /bookings/{booking_id}/accept")

        # 6c. Technician Start Trip
        r = client.post(f"/bookings/{booking_id}/start-trip", headers=tech_h)
        record_result(f"/bookings/{booking_id}/start-trip", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /bookings/{booking_id}/start-trip")

        # 6d. Technician Broadcast Live Location & Customer Track
        loc_payload = {
            "booking_id": booking_id,
            "latitude": 12.9352,
            "longitude": 77.6245,
            "status": "en_route",
        }
        r = client.post("/location/update", headers=tech_h, json=loc_payload)
        record_result("/location/update", "POST", loc_payload, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] POST /location/update")

        r = client.get(f"/location/booking/{booking_id}", headers=cust_h)
        record_result(f"/location/booking/{booking_id}", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /location/booking/{booking_id}")

        # 6e. Technician Arrive at Customer Site
        r = client.post(f"/bookings/{booking_id}/arrived", headers=tech_h)
        record_result(f"/bookings/{booking_id}/arrived", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /bookings/{booking_id}/arrived")

        # 6e. Customer Generate OTP for SmartVerify
        r = client.post(f"/bookings/{booking_id}/generate-otp", headers=cust_h)
        record_result(f"/bookings/{booking_id}/generate-otp", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        otp_code = r.json()["otp_code"]
        print(f"  [OK] POST /bookings/{booking_id}/generate-otp (OTP: {otp_code})")

        # 6f. Technician Verify OTP & Start Service
        r = client.post(f"/bookings/{booking_id}/verify-otp", headers=cust_h, json={"otp_code": otp_code})
        record_result(f"/bookings/{booking_id}/verify-otp", "POST", {"otp_code": otp_code}, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /bookings/{booking_id}/verify-otp")

        # 6g. Technician Complete Booking
        r = client.post(f"/bookings/{booking_id}/complete", headers=tech_h)
        record_result(f"/bookings/{booking_id}/complete", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /bookings/{booking_id}/complete")

        # 6h. Get Booking Status Logs / History
        r = client.get(f"/bookings/{booking_id}/history", headers=cust_h)
        record_result(f"/bookings/{booking_id}/history", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /bookings/{booking_id}/history")

        # ── 7. COUPONS, PAYMENTS & INVOICES WORKFLOW ─────────────────────────
        print("\n[7/14] Testing Coupons, Payments & Invoices APIs...")

        # 7a. Admin Create Coupon
        coupon_code = f"DISC{uuid4().hex[:6].upper()}"
        coupon_payload = {
            "code": coupon_code,
            "discount_type": "percentage",
            "discount_value": 15.0,
            "min_order_value": 300.0,
            "max_discount": 100.0,
            "valid_from": datetime.now(timezone.utc).date().isoformat(),
            "valid_until": "2029-12-31",
            "usage_limit": 100,
        }
        r = client.post("/coupons/", headers=admin_h, json=coupon_payload)
        record_result("/coupons/", "POST", coupon_payload, 201, r.status_code)
        assert r.status_code == 201, f"Create coupon failed: {r.text}"
        print(f"  [OK] POST /coupons/ (Code: {coupon_code})")

        # 7b. Validate Coupon
        r = client.post("/coupons/validate", headers=cust_h, json={"code": coupon_code, "booking_id": booking_id})
        record_result("/coupons/validate", "POST", {"code": coupon_code, "booking_id": booking_id}, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] POST /coupons/validate")

        # 7c. Create Razorpay Order
        pay_order_payload = {
            "booking_id": booking_id,
            "amount": 509.0,
            "currency": "INR",
            "payment_method": "card",
        }
        r = client.post("/payments/create-order", headers=cust_h, json=pay_order_payload)
        record_result("/payments/create-order", "POST", pay_order_payload, 200, r.status_code)
        assert r.status_code == 200, f"Create order failed: {r.text}"
        payment_order_id = r.json().get("order_id") or "order_test_123"
        print(f"  [OK] POST /payments/create-order (Order ID: {payment_order_id})")

        # 7d. Generate Invoice
        inv_payload = {
            "booking_id": booking_id,
            "customer_id": cust_profile.id,
            "technician_id": tech_profile.id,
            "subtotal": 599.0,
            "tax_amount": 0.0,
            "discount_amount": 90.0,
            "total_amount": 509.0,
        }
        r = client.post("/invoices/", headers=admin_h, json=inv_payload)
        record_result("/invoices/", "POST", inv_payload, 201, r.status_code)
        assert r.status_code == 201, f"Create invoice failed: {r.text}"
        invoice_id = r.json()["id"]
        print(f"  [OK] POST /invoices/ (Invoice ID: {invoice_id})")

        # 7e. Get Invoice by ID
        r = client.get(f"/invoices/{invoice_id}", headers=cust_h)
        record_result(f"/invoices/{invoice_id}", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /invoices/{invoice_id}")

        # ── 8. REVIEWS & RATINGS WORKFLOW ─────────────────────────────────────
        print("\n[8/14] Testing Reviews & Rating APIs...")

        # 8a. Customer Submit Review
        review_payload = {
            "booking_id": booking_id,
            "technician_id": tech_profile.id,
            "rating": 5,
            "comment": "Outstanding service! Arrived on time and resolved AC cooling perfectly.",
        }
        r = client.post("/reviews/", headers=cust_h, json=review_payload)
        record_result("/reviews/", "POST", review_payload, 201, r.status_code)
        assert r.status_code == 201, f"Submit review failed: {r.text}"
        review_id = r.json()["id"]
        print(f"  [OK] POST /reviews/ (Review ID: {review_id})")

        # 8b. Get Technician Reviews
        r = client.get(f"/reviews/technician/{tech_profile.id}")
        record_result(f"/reviews/technician/{tech_profile.id}", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /reviews/technician/{tech_profile.id}")

        # 8c. Get Rating Summary
        r = client.get(f"/reviews/technician/{tech_profile.id}/summary")
        record_result(f"/reviews/technician/{tech_profile.id}/summary", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /reviews/technician/{tech_profile.id}/summary")

        # ── 9. NOTIFICATIONS WORKFLOW ─────────────────────────────────────────
        print("\n[9/14] Testing Notifications APIs...")

        # 9a. List Customer Notifications
        r = client.get("/notifications/", headers=cust_h)
        record_result("/notifications/", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /notifications/")

        # 9b. Get Unread Notifications
        r = client.get("/notifications/unread", headers=cust_h)
        record_result("/notifications/unread", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /notifications/unread")

        # 9c. Mark All as Read
        r = client.put("/notifications/read-all", headers=cust_h)
        record_result("/notifications/read-all", "PUT", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] PUT /notifications/read-all")

        # ── 10. CLOUDINARY MEDIA & DOCUMENTS WORKFLOW ─────────────────────────
        print("\n[10/14] Testing Cloudinary Media & Document APIs...")

        # 10a. User Avatar
        avatar_file = {"file": ("avatar.png", io.BytesIO(VALID_PNG), "image/png")}
        r = client.post("/users/me/avatar", headers=cust_h, files=avatar_file)
        record_result("/users/me/avatar", "POST", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] POST /users/me/avatar")

        # 10b. Technician Portfolio
        port_file = {"file": ("port.png", io.BytesIO(VALID_PNG), "image/png")}
        r = client.post("/technicians/me/portfolio", headers=tech_h, files=port_file)
        record_result("/technicians/me/portfolio", "POST", None, 201, r.status_code)
        assert r.status_code == 201
        port_id = r.json()["data"]["id"]
        print(f"  [OK] POST /technicians/me/portfolio (ID: {port_id})")

        # 10c. Booking Before Photo
        before_file = {"file": ("before.png", io.BytesIO(VALID_PNG), "image/png")}
        r = client.post(f"/bookings/{booking_id}/before-images", headers=tech_h, files=before_file)
        record_result(f"/bookings/{booking_id}/before-images", "POST", None, 201, r.status_code)
        assert r.status_code == 201
        print(f"  [OK] POST /bookings/{booking_id}/before-images")

        # 10d. Booking Attachment
        doc_file = {"file": ("spec.pdf", io.BytesIO(VALID_PDF), "application/pdf")}
        r = client.post(f"/bookings/{booking_id}/attachments", headers=cust_h, files=doc_file)
        record_result(f"/bookings/{booking_id}/attachments", "POST", None, 201, r.status_code)
        assert r.status_code == 201
        print(f"  [OK] POST /bookings/{booking_id}/attachments")

        # 10e. List Booking Media
        r = client.get(f"/bookings/{booking_id}/media", headers=cust_h)
        record_result(f"/bookings/{booking_id}/media", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print(f"  [OK] GET /bookings/{booking_id}/media")

        # 10f. Admin List Media Assets
        r = client.get("/admin/media", headers=admin_h)
        record_result("/admin/media", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /admin/media")

        # ── 11. SEARCH & GLOBAL DISCOVERY ─────────────────────────────────────
        print("\n[11/14] Testing Search & Discovery APIs...")

        # 11a. Global Search
        r = client.get("/search/?q=AC")
        record_result("/search/?q=AC", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /search/?q=AC")

        # 11b. Search Suggestions
        r = client.get("/search/suggestions?q=AC")
        record_result("/search/suggestions?q=AC", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /search/suggestions?q=AC")

        # ── 12. ADMIN ANALYTICS & REPORTS ─────────────────────────────────────
        print("\n[12/14] Testing Admin Reports & Analytics APIs...")

        # 12a. Admin Analytics Overview
        r = client.get("/analytics/admin", headers=admin_h)
        record_result("/analytics/admin", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /analytics/admin")

        # 12b. Admin Monthly Business Report
        r = client.get("/reports/monthly", headers=admin_h)
        record_result("/reports/monthly", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /reports/monthly")

        # 12c. Admin Export Report
        r = client.get("/reports/export?format=csv&period=monthly", headers=admin_h)
        record_result("/reports/export", "GET", {"format": "csv"}, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /reports/export?format=csv&period=monthly")

        # ── 13. SECURITY, AUDIT LOGS & HEALTH MONITORING ───────────────────────
        print("\n[13/14] Testing Security, Audit Logs & Health Monitoring APIs...")

        # 13a. System Health Check
        r = client.get("/health/detail")
        record_result("/health/detail", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /health/detail")

        # 13b. System Prometheus Metrics
        r = client.get("/metrics")
        record_result("/metrics", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /metrics")

        # 13c. Security Sessions
        r = client.get("/security/sessions", headers=cust_h)
        record_result("/security/sessions", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /security/sessions")

        # 13d. Security Audit Logs
        r = client.get("/security/audit-logs", headers=admin_h)
        record_result("/security/audit-logs", "GET", None, 200, r.status_code)
        assert r.status_code == 200
        print("  [OK] GET /security/audit-logs")

        # ── 14. AUTHORIZATION RBAC GUARD CHECKS (Negative Tests) ──────────────
        print("\n[14/14] Testing RBAC Security Guard Enforcements (Negative Tests)...")

        # 14a. Customer trying to access Admin Analytics -> 403 Forbidden
        r = client.get("/analytics/admin", headers=cust_h)
        record_result("/analytics/admin (Customer)", "GET", None, 403, r.status_code)
        assert r.status_code == 403, f"Expected 403 Forbidden, got {r.status_code}"
        print("  [OK] Negative Check: Customer blocked from /analytics/admin (403 Forbidden)")

        # 14b. Anonymous user trying to access /users/me -> 401/403 Blocked
        r = client.get("/users/me")
        record_result("/users/me (Anonymous)", "GET", None, 403, r.status_code)
        assert r.status_code in [401, 403], f"Expected 401/403, got {r.status_code}"
        print("  [OK] Negative Check: Anonymous blocked from /users/me (401/403 Blocked)")

        print("\n" + "=" * 80)
        print(f"ALL {len(TEST_RESULTS)} SYSTEMATIC API ENDPOINTS PASSED WITH 100% SUCCESS!")
        print("=" * 80)

    finally:
        db.close()


if __name__ == "__main__":
    run_all_systematic_tests()
    # Save structured results JSON for report generation
    with open("systematic_test_results.json", "w") as f:
        json.dump(TEST_RESULTS, f, indent=2)
    print("\nSaved detailed test execution report to systematic_test_results.json")
