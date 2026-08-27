"""
==============================================================================
HomiQ Backend - Master API Test Suite
Tests all registered API endpoints, methods, and role workflows across:
- Auth & Security (/auth, /security)
- Customer (/customer)
- Technician (/technician)
- Company (/company)
- Services & Categories (/services)
- Bookings & Lifecycle (/bookings)
- SmartVerify (QR & OTP) (/bookings/{id}/qr, otp)
- Payments & Webhooks (/payments)
- Coupons (/coupons)
- Invoices (/invoices)
- Reviews (/reviews)
- Notifications (/notifications)
- Tracking, Maps & GPS (/tracking, /location, /maps)
- Jobs & Applications (/jobs)
- Media & Cloudinary (/media)
- Reports & Analytics (/reports, /analytics, /admin/analytics)
- Search & Recommendations (/search, /recommendations)
- Background Tasks & Scheduler (/tasks, /scheduler)
- System Monitoring & Health (/health, /metrics)
- Admin Management (/admin)
- WebSockets & Chat History (/ws, /chat)
==============================================================================
"""

from __future__ import annotations

import datetime
import io
import json
import os
import sys
import time
import uuid
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test run tracker
PASSED_TESTS: List[Tuple[str, str, int]] = []
FAILED_TESTS: List[Tuple[str, str, int, str]] = []
SKIPPED_TESTS: List[Tuple[str, str, str]] = []
START_TIME = time.time()
PASSWORD = "TestPassword@1234"


def uid(prefix: str = "t") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def gen_email(role: str) -> str:
    return f"test_{role}_{uuid.uuid4().hex[:8]}@example.com"


def future_date(days: int = 3) -> str:
    return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()


def log_step(title: str):
    print(f"\n[{'='*72}]\n>>> {title}\n[{'='*72}]")


def check(name: str, method: str, path: str, response, expected_codes: tuple[int, ...] = (200, 201)):
    status_code = response.status_code
    if status_code in expected_codes:
        PASSED_TESTS.append((name, f"{method} {path}", status_code))
        print(f"  [PASS] {name:<40} {method:>6} {path:<42} -> {status_code}")
        return True
    else:
        err_snippet = response.text[:300].replace("\n", " ")
        FAILED_TESTS.append((name, f"{method} {path}", status_code, err_snippet))
        print(f"  [FAIL] {name:<40} {method:>6} {path:<42} -> Expected {expected_codes}, got {status_code}: {err_snippet}")
        return False


def register_user(role: str, custom_prefix: str = "") -> dict[str, Any]:
    prefix = custom_prefix or role
    email = gen_email(prefix)
    phone = f"98{uuid.uuid4().int % 100000000:08d}"
    r = client.post("/auth/register", json={
        "email": email,
        "password": PASSWORD,
        "full_name": f"Test {prefix.capitalize()} User",
        "phone": phone,
        "role": role,
    })
    assert r.status_code == 201, f"Failed to register user {email} (role {role}): {r.text}"
    data = r.json()
    token = data["access_token"]
    refresh_token = data["refresh_token"]
    user_info = data["user"]
    return {
        "email": email,
        "password": PASSWORD,
        "token": token,
        "refresh_token": refresh_token,
        "user": user_info,
        "user_id": user_info["id"],
        "headers": {"Authorization": f"Bearer {token}"},
    }


def login_admin() -> dict[str, Any]:
    # Check if existing admin can login or register a new admin
    email = "admin_master@homiq.com"
    r = client.post("/auth/login", json={"identifier": email, "password": PASSWORD})
    if r.status_code == 200:
        data = r.json()
        return {
            "email": email,
            "token": data["access_token"],
            "refresh_token": data["refresh_token"],
            "headers": {"Authorization": f"Bearer {data['access_token']}"},
            "user": data["user"],
        }
    
    # Register new admin
    return register_user("admin", "admin_master")


# ==============================================================================
# 1. AUTH API TESTS
# ==============================================================================
def test_auth_api(customer: dict, admin: dict):
    log_step("1. AUTHENTICATION & IDENTITY APIS (/auth)")

    # 1.1 Register duplicate email (should fail 400)
    r = client.post("/auth/register", json={
        "email": customer["email"],
        "password": PASSWORD,
        "full_name": "Duplicate User",
        "phone": "9812345678",
        "role": "customer",
    })
    check("Register Duplicate Email (400)", "POST", "/auth/register", r, (400,))

    # 1.2 Login with valid credentials
    r = client.post("/auth/login", json={
        "identifier": customer["email"],
        "password": PASSWORD,
    })
    check("Login Valid Credentials (200)", "POST", "/auth/login", r, (200,))

    # 1.3 Login with invalid credentials (401)
    r = client.post("/auth/login", json={
        "identifier": customer["email"],
        "password": "WrongPassword123",
    })
    check("Login Invalid Credentials (401)", "POST", "/auth/login", r, (401,))

    # 1.4 Refresh token
    r = client.post(f"/auth/refresh?refresh_token={customer['refresh_token']}")
    check("Refresh Access Token (200)", "POST", "/auth/refresh", r, (200,))

    # 1.5 Refresh with invalid token (401)
    r = client.post("/auth/refresh?refresh_token=invalid_refresh_token_123")
    check("Refresh Invalid Token (401)", "POST", "/auth/refresh", r, (401,))

    # 1.6 Forgot password request
    r = client.post("/auth/forgot-password", json={"email": customer["email"]})
    check("Forgot Password Request (200)", "POST", "/auth/forgot-password", r, (200,))

    # 1.7 Reset password request
    r = client.post("/auth/reset-password", json={
        "email": customer["email"],
        "otp": "123456",
        "new_password": PASSWORD,
    })
    check("Reset Password (200)", "POST", "/auth/reset-password", r, (200,))

    # 1.8 Get current user profile (/auth/me)
    r = client.get("/auth/me", headers=customer["headers"])
    check("Get Current User (/auth/me) (200)", "GET", "/auth/me", r, (200,))


# ==============================================================================
# 2. CUSTOMER & ADDRESS APIS
# ==============================================================================
def test_customer_api(customer: dict, technician: dict) -> dict[str, Any]:
    log_step("2. CUSTOMER PROFILE & ADDRESS APIS (/customer)")

    # 2.1 Get profile
    r = client.get("/customer/profile", headers=customer["headers"])
    check("Get Customer Profile (200)", "GET", "/customer/profile", r, (200,))

    # 2.2 Update profile
    r = client.put("/customer/profile", headers=customer["headers"], json={
        "full_name": "Updated Customer Name",
        "phone": "9898989898",
        "city": "Bengaluru",
        "state": "Karnataka",
        "postal_code": "560001",
        "preferred_language": "en",
    })
    check("Update Customer Profile (200)", "PUT", "/customer/profile", r, (200,))

    # 2.3 Upload profile image
    fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    r = client.post(
        "/customer/profile/image",
        headers=customer["headers"],
        files={"file": ("profile.png", fake_img, "image/png")}
    )
    check("Upload Profile Image (200)", "POST", "/customer/profile/image", r, (200,))

    # 2.4 Create Address 1 (Default)
    r = client.post("/customer/addresses", headers=customer["headers"], json={
        "full_name": "Customer Main Home",
        "phone": "9898989898",
        "house_no": "101",
        "building": "Palm Grove Apt",
        "landmark": "Near Metro",
        "area": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "latitude": 12.9784,
        "longitude": 77.6408,
        "is_default": True,
    })
    check("Create Default Address (201)", "POST", "/customer/addresses", r, (201,))
    addr_1 = r.json()
    addr_1_id = addr_1["id"]

    # 2.5 Create Address 2 (Secondary)
    r = client.post("/customer/addresses", headers=customer["headers"], json={
        "full_name": "Customer Office",
        "phone": "9898989898",
        "house_no": "404",
        "building": "Tech Park Tower B",
        "area": "Whitefield",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560066",
        "latitude": 12.9698,
        "longitude": 77.7499,
        "is_default": False,
    })
    check("Create Secondary Address (201)", "POST", "/customer/addresses", r, (201,))
    addr_2 = r.json()
    addr_2_id = addr_2["id"]

    # 2.6 List addresses
    r = client.get("/customer/addresses", headers=customer["headers"])
    check("List Customer Addresses (200)", "GET", "/customer/addresses", r, (200,))

    # 2.7 Get single address by ID
    r = client.get(f"/customer/addresses/{addr_1_id}", headers=customer["headers"])
    check("Get Address By ID (200)", "GET", f"/customer/addresses/{addr_1_id}", r, (200,))

    # 2.8 Update address
    r = client.put(f"/customer/addresses/{addr_1_id}", headers=customer["headers"], json={
        "landmark": "Opposite Metro Gate 2",
    })
    check("Update Address (200)", "PUT", f"/customer/addresses/{addr_1_id}", r, (200,))

    # 2.9 Set default address
    r = client.put(f"/customer/addresses/{addr_2_id}/default", headers=customer["headers"])
    check("Set Address Default (200)", "PUT", f"/customer/addresses/{addr_2_id}/default", r, (200,))

    # 2.10 Customer Dashboard
    r = client.get("/customer/dashboard", headers=customer["headers"])
    check("Customer Dashboard (200)", "GET", "/customer/dashboard", r, (200,))

    # 2.11 Role guard: Technician attempting customer profile (403)
    r = client.get("/customer/profile", headers=technician["headers"])
    check("Role Guard: Tech on Customer Profile (403)", "GET", "/customer/profile", r, (403,))

    return {"primary_address_id": addr_1_id, "secondary_address_id": addr_2_id}


# ==============================================================================
# 3. TECHNICIAN APIS
# ==============================================================================
def test_technician_api(technician: dict, customer: dict, admin: dict):
    log_step("3. TECHNICIAN PROFILE & JOBS APIS (/technician)")

    # 3.1 Get Profile
    r = client.get("/technician/profile", headers=technician["headers"])
    check("Get Technician Profile (200)", "GET", "/technician/profile", r, (200,))

    # 3.2 Update Profile
    r = client.put("/technician/profile", headers=technician["headers"], json={
        "specialization": "AC & Electrical",
        "experience_years": 6,
        "skills": ["Split AC Repair", "Wiring", "PCB Troubleshooting"],
        "languages": ["English", "Hindi", "Kannada"],
        "working_hours": "08:00 - 20:00",
        "service_radius_km": 25.0,
        "latitude": 12.9716,
        "longitude": 77.5946,
    })
    check("Update Technician Profile (200)", "PUT", "/technician/profile", r, (200,))

    # 3.3 Upload Technician Profile Image
    fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    r = client.post(
        "/technician/profile/image",
        headers=technician["headers"],
        files={"file": ("tech.png", fake_img, "image/png")}
    )
    check("Upload Tech Profile Image (200)", "POST", "/technician/profile/image", r, (200,))

    # 3.4 Upload Government ID
    fake_doc = io.BytesIO(b"%PDF-1.4 Mock Government ID Document")
    r = client.post(
        "/technician/profile/government-id",
        headers=technician["headers"],
        files={"file": ("govt_id.pdf", fake_doc, "application/pdf")}
    )
    check("Upload Government ID (200)", "POST", "/technician/profile/government-id", r, (200,))

    # 3.5 Set Online & Offline
    r = client.patch("/technician/online", headers=technician["headers"])
    check("Set Technician Online (200)", "PATCH", "/technician/online", r, (200,))

    r = client.patch("/technician/offline", headers=technician["headers"])
    check("Set Technician Offline (200)", "PATCH", "/technician/offline", r, (200,))

    # 3.6 Update Availability
    r = client.put("/technician/availability", headers=technician["headers"], json={
        "availability": True,
        "is_online": True,
    })
    check("Update Tech Availability (200)", "PUT", "/technician/availability", r, (200,))

    # 3.7 List technicians (Public/Search)
    r = client.get("/technician/?specialization=AC%20%26%20Electrical")
    check("List Technicians Public (200)", "GET", "/technician/", r, (200,))

    # 3.8 List jobs & bookings
    r = client.get("/technician/jobs", headers=technician["headers"])
    check("Get Technician My Jobs (200)", "GET", "/technician/jobs", r, (200,))

    r = client.get("/technician/bookings", headers=technician["headers"])
    check("Get Technician Bookings (200)", "GET", "/technician/bookings", r, (200,))

    r = client.get("/technician/bookings/active", headers=technician["headers"])
    check("Get Technician Active Bookings (200)", "GET", "/technician/bookings/active", r, (200,))

    r = client.get("/technician/history", headers=technician["headers"])
    check("Get Technician Booking History (200)", "GET", "/technician/history", r, (200,))

    # 3.9 Earnings
    r = client.get("/technician/earnings", headers=technician["headers"])
    check("Get Technician Earnings (200)", "GET", "/technician/earnings", r, (200,))

    # 3.10 Technician Dashboard
    r = client.get("/technician/dashboard", headers=technician["headers"])
    check("Technician Dashboard (200)", "GET", "/technician/dashboard", r, (200,))

    # 3.11 Documents
    fake_aadhaar = io.BytesIO(b"%PDF-1.4 Mock Aadhaar Document")
    r = client.post(
        "/technician/documents",
        headers=technician["headers"],
        data={"doc_type": "aadhaar"},
        files={"file": ("aadhaar.pdf", fake_aadhaar, "application/pdf")}
    )
    check("Upload Tech Document (201)", "POST", "/technician/documents", r, (201,))

    r = client.get("/technician/documents", headers=technician["headers"])
    check("Get Tech Documents (200)", "GET", "/technician/documents", r, (200,))


# ==============================================================================
# 4. COMPANY APIS
# ==============================================================================
def test_company_api(company: dict):
    log_step("4. COMPANY PROFILE APIS (/company)")

    # 4.1 Get Profile
    r = client.get("/company/profile", headers=company["headers"])
    check("Get Company Profile (200)", "GET", "/company/profile", r, (200,))

    # 4.2 Update Profile
    r = client.put("/company/profile", headers=company["headers"], json={
        "company_name": "Urban Elite Home Services Pvt Ltd",
        "industry": "Facility Management",
        "description": "Premium residential repairs and home installation services.",
        "website": "https://urbanelite.example.com",
    })
    check("Update Company Profile (200)", "PUT", "/company/profile", r, (200,))

    # 4.3 List Companies (Public)
    r = client.get("/company/?limit=10")
    check("List Companies Public (200)", "GET", "/company/", r, (200,))


# ==============================================================================
# 5. SERVICES & CATEGORIES APIS
# ==============================================================================
def test_services_api(admin: dict) -> dict[str, Any]:
    log_step("5. SERVICES & CATEGORIES APIS (/services)")

    cat_name = f"Category_{uid('cat')}"
    # 5.1 Create Category (Admin)
    r = client.post("/services/categories", headers=admin["headers"], json={
        "name": cat_name,
        "description": "Appliance repair and seasonal maintenance services.",
        "icon": "tools-icon",
        "is_active": True,
    })
    check("Create Service Category (201)", "POST", "/services/categories", r, (201,))
    category = r.json()
    cat_id = category["id"]

    # 5.2 List Categories (Public)
    r = client.get("/services/categories")
    check("List Categories Public (200)", "GET", "/services/categories", r, (200,))

    # 5.3 Get Category by ID
    r = client.get(f"/services/categories/{cat_id}")
    check("Get Category By ID (200)", "GET", f"/services/categories/{cat_id}", r, (200,))

    # 5.4 Update Category
    r = client.put(f"/services/categories/{cat_id}", headers=admin["headers"], json={
        "name": f"{cat_name}_Updated",
        "description": "Updated Category Description",
    })
    check("Update Category (200)", "PUT", f"/services/categories/{cat_id}", r, (200,))

    # 5.5 Create Service
    svc_name = f"Service_{uid('svc')}"
    r = client.post("/services/", headers=admin["headers"], json={
        "name": svc_name,
        "description": "Complete deep service inspection and coil cleaning.",
        "category_id": cat_id,
        "price": 649.0,
        "duration_minutes": 60,
        "is_active": True,
    })
    check("Create Service (201)", "POST", "/services/", r, (201,))
    service = r.json()
    service_id = service["id"]

    # 5.6 List Services (Public with filters)
    r = client.get(f"/services/?category_id={cat_id}&min_price=100&max_price=1000")
    check("List Services with Filters (200)", "GET", "/services/", r, (200,))

    # 5.7 Get Service by ID
    r = client.get(f"/services/{service_id}")
    check("Get Service By ID (200)", "GET", f"/services/{service_id}", r, (200,))

    # 5.8 Update Service
    r = client.put(f"/services/{service_id}", headers=admin["headers"], json={
        "price": 699.0,
        "duration_minutes": 75,
    })
    check("Update Service (200)", "PUT", f"/services/{service_id}", r, (200,))

    # 5.9 Upload Service Image
    fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    r = client.post(
        f"/services/{service_id}/image",
        headers=admin["headers"],
        files={"file": ("service.png", fake_img, "image/png")}
    )
    check("Upload Service Image (200)", "POST", f"/services/{service_id}/image", r, (200,))

    return {"category_id": cat_id, "service_id": service_id}


# ==============================================================================
# 6. BOOKINGS, LIFECYCLE & SMARTVERIFY APIS
# ==============================================================================
def test_bookings_and_lifecycle_api(
    customer: dict,
    technician: dict,
    admin: dict,
    service_id: int,
    address_id: int
) -> dict[str, Any]:
    log_step("6. BOOKING CREATION, LIFECYCLE & SMARTVERIFY APIS (/bookings)")

    # Fetch technician DB record ID for assignment
    r_techs = client.get("/technician/", headers=admin["headers"])
    tech_id_val = r_techs.json()[0]["id"] if r_techs.status_code == 200 and r_techs.json() else 1

    # 6.1 Create Booking (Customer)
    booking_date_val = future_date(4)
    r = client.post("/bookings/", headers=customer["headers"], json={
        "service_id": service_id,
        "address_id": address_id,
        "booking_date": booking_date_val,
        "preferred_time": "11:00:00",
        "estimated_price": 699.0,
        "customer_note": "Please bring ladder and spare parts.",
    })
    check("Create Booking (201)", "POST", "/bookings/", r, (201,))
    booking = r.json()
    booking_id = booking["id"]

    # 6.2 List Bookings (Customer & Admin)
    r = client.get("/bookings/", headers=customer["headers"])
    check("List Customer Bookings (200)", "GET", "/bookings/", r, (200,))

    r = client.get("/bookings/", headers=admin["headers"])
    check("List Admin Bookings (200)", "GET", "/bookings/", r, (200,))

    # 6.3 Get Booking by ID
    r = client.get(f"/bookings/{booking_id}", headers=customer["headers"])
    check("Get Booking Details (200)", "GET", f"/bookings/{booking_id}", r, (200,))

    # 6.4 Update Booking details (Customer)
    r = client.put(f"/bookings/{booking_id}", headers=customer["headers"], json={
        "customer_note": "Call before arriving.",
    })
    check("Update Booking (200)", "PUT", f"/bookings/{booking_id}", r, (200,))

    # 6.5 Admin Assign Technician (PUT)
    r = client.put(f"/bookings/{booking_id}/assign", headers=admin["headers"], json={
        "technician_id": tech_id_val,
    })
    check("Admin Assign Technician (200)", "PUT", f"/bookings/{booking_id}/assign", r, (200,))

    # 6.6 Reschedule Booking (Customer)
    new_date = future_date(6)
    r = client.put(f"/bookings/{booking_id}/reschedule", headers=customer["headers"], json={
        "booking_date": new_date,
        "preferred_time": "14:00:00",
    })
    check("Customer Reschedule Booking (200)", "PUT", f"/bookings/{booking_id}/reschedule", r, (200,))

    # 6.7 Technician Accept Booking
    r = client.post(f"/bookings/{booking_id}/accept", headers=technician["headers"], json={
        "reason": "Ready to service.",
    })
    check("Technician Accept Booking (200)", "POST", f"/bookings/{booking_id}/accept", r, (200,))

    # 6.8 Technician Start Trip
    r = client.post(f"/bookings/{booking_id}/start-trip", headers=technician["headers"], json={
        "reason": "On my way to location.",
    })
    check("Technician Start Trip (200)", "POST", f"/bookings/{booking_id}/start-trip", r, (200,))

    # 6.9 Technician Arrived
    r = client.post(f"/bookings/{booking_id}/arrived", headers=technician["headers"], json={
        "reason": "Arrived at doorstep.",
    })
    check("Technician Arrived (200)", "POST", f"/bookings/{booking_id}/arrived", r, (200,))

    # 6.10 SmartVerify: Generate QR Code (Customer)
    r = client.post(f"/bookings/{booking_id}/generate-qr", headers=customer["headers"])
    check("Generate SmartVerify QR (201)", "POST", f"/bookings/{booking_id}/generate-qr", r, (201, 200))
    qr_data = r.json() if r.status_code in (200, 201) else {}
    qr_token = qr_data.get("qr_token", "sample_qr_token")

    # 6.11 SmartVerify: Get Active QR Code
    r = client.get(f"/bookings/{booking_id}/qr", headers=customer["headers"])
    check("Get Active QR Code (200)", "GET", f"/bookings/{booking_id}/qr", r, (200,))

    # 6.12 SmartVerify: Scan QR Code (Technician)
    r = client.post(f"/bookings/{booking_id}/scan-qr", headers=technician["headers"], json={
        "qr_token": qr_token,
    })
    check("Technician Scan QR Code (200)", "POST", f"/bookings/{booking_id}/scan-qr", r, (200,))

    # 6.13 SmartVerify: Generate OTP
    r = client.post(f"/bookings/{booking_id}/generate-otp", headers=customer["headers"])
    check("Generate 6-digit OTP (200)", "POST", f"/bookings/{booking_id}/generate-otp", r, (200,))
    otp_code = r.json().get("otp_code", "123456") if r.status_code == 200 else "123456"

    # 6.14 SmartVerify: Verify OTP and start service (Customer)
    r = client.post(f"/bookings/{booking_id}/verify-otp", headers=customer["headers"], json={
        "otp": otp_code,
    })
    check("Customer Verify OTP (200)", "POST", f"/bookings/{booking_id}/verify-otp", r, (200,))

    # 6.15 SmartVerify: Get Verification Status
    r = client.get(f"/bookings/{booking_id}/verification-status", headers=customer["headers"])
    check("Get SmartVerify Status (200)", "GET", f"/bookings/{booking_id}/verification-status", r, (200,))

    # 6.16 Technician Complete Service
    r = client.post(f"/bookings/{booking_id}/complete", headers=technician["headers"], json={
        "reason": "Service completed successfully.",
    })
    check("Technician Complete Service (200)", "POST", f"/bookings/{booking_id}/complete", r, (200,))

    # 6.17 Customer Track Booking
    r = client.get(f"/bookings/{booking_id}/track", headers=customer["headers"])
    check("Customer Track Booking (200)", "GET", f"/bookings/{booking_id}/track", r, (200,))

    # 6.18 Customer Booking History
    r = client.get(f"/bookings/{booking_id}/history", headers=customer["headers"])
    check("Booking History Audit (200)", "GET", f"/bookings/{booking_id}/history", r, (200,))

    # 6.19 Get Assigned Technician Details
    r = client.get(f"/bookings/{booking_id}/technician", headers=customer["headers"])
    check("Get Assigned Technician Info (200)", "GET", f"/bookings/{booking_id}/technician", r, (200,))

    return {"booking_id": booking_id, "technician_id": tech_id_val}


# ==============================================================================
# 7. PAYMENTS & WEBHOOKS APIS
# ==============================================================================
def test_payments_api(customer: dict, admin: dict, booking_id: int) -> dict[str, Any]:
    log_step("7. PAYMENTS, ORDERS, REFUNDS & WEBHOOKS APIS (/payments)")

    # 7.1 Create Razorpay Order
    r = client.post("/payments/create-order", headers=customer["headers"], json={
        "booking_id": booking_id,
    })
    check("Create Payment Order (200)", "POST", "/payments/create-order", r, (200,))
    order_data = r.json() if r.status_code == 200 else {}
    payment_id = order_data.get("payment_id", 1)
    razorpay_order_id = order_data.get("id", "order_mock123")

    # 7.2 List Payments (Customer & Admin)
    r = client.get("/payments/", headers=customer["headers"])
    check("List Customer Payments (200)", "GET", "/payments/", r, (200,))

    r = client.get("/payments/", headers=admin["headers"])
    check("List Admin Payments (200)", "GET", "/payments/", r, (200,))

    # 7.3 Get Payment by ID
    r = client.get(f"/payments/{payment_id}", headers=customer["headers"])
    check("Get Payment by ID (200)", "GET", f"/payments/{payment_id}", r, (200,))

    # 7.4 Get Payment History
    r = client.get("/payments/history", headers=customer["headers"])
    check("Get Payment History (200)", "GET", "/payments/history", r, (200,))

    # 7.5 Verify Payment (Invalid signature test 400)
    r = client.post("/payments/verify", headers=customer["headers"], json={
        "razorpay_order_id": razorpay_order_id,
        "razorpay_payment_id": "pay_mock_123456",
        "razorpay_signature": "invalid_signature_mock",
    })
    check("Verify Payment Signature Guard (400)", "POST", "/payments/verify", r, (400,))

    # 7.6 Razorpay Webhook Handler
    r = client.post("/payments/webhook", json={
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test_webhook",
                    "order_id": razorpay_order_id,
                    "status": "captured",
                    "amount": 69900,
                    "currency": "INR",
                    "method": "upi",
                }
            }
        }
    })
    check("Razorpay Webhook Handler (200)", "POST", "/payments/webhook", r, (200,))

    # 7.7 Payment Invoice
    r = client.get(f"/payments/invoice/{payment_id}", headers=customer["headers"])
    check("Get Payment Invoice (200)", "GET", f"/payments/invoice/{payment_id}", r, (200,))

    # 7.8 Admin Refund Payment by ID
    r = client.post(f"/payments/{payment_id}/refund", headers=admin["headers"])
    check("Admin Refund Payment (200/400)", "POST", f"/payments/{payment_id}/refund", r, (200, 400))

    return {"payment_id": payment_id}


# ==============================================================================
# 8. COUPONS & DISCOUNTS APIS
# ==============================================================================
def test_coupons_api(customer: dict, admin: dict, booking_id: int):
    log_step("8. COUPONS & DISCOUNTS APIS (/coupons)")

    code = f"SAVE{uid('cp').upper()}"

    # 8.1 Create Coupon (Admin)
    r = client.post("/coupons/", headers=admin["headers"], json={
        "code": code,
        "discount_type": "percentage",
        "discount_value": 15.0,
        "max_discount_amount": 200.0,
        "min_order_amount": 299.0,
        "usage_limit_per_user": 3,
        "is_active": True,
    })
    check("Create Coupon (201)", "POST", "/coupons/", r, (201,))
    coupon = r.json()
    coupon_id = coupon["id"]

    # 8.2 List Coupons (Admin)
    r = client.get("/coupons/", headers=admin["headers"])
    check("List Coupons (200)", "GET", "/coupons/", r, (200,))

    # 8.3 Get Coupon by ID
    r = client.get(f"/coupons/{coupon_id}", headers=customer["headers"])
    check("Get Coupon By ID (200)", "GET", f"/coupons/{coupon_id}", r, (200,))

    # 8.4 Get Coupon by Code
    r = client.get(f"/coupons/code/{code}", headers=customer["headers"])
    check("Get Coupon By Code (200)", "GET", f"/coupons/code/{code}", r, (200,))

    # 8.5 Validate Coupon (Customer)
    r = client.post("/coupons/validate", headers=customer["headers"], json={
        "code": code,
        "amount": 500.0,
    })
    check("Validate Coupon Code (200)", "POST", "/coupons/validate", r, (200,))

    # 8.6 Apply Coupon to Booking (Customer)
    r = client.post("/coupons/apply", headers=customer["headers"], json={
        "code": code,
        "booking_id": booking_id,
        "amount": 699.0,
    })
    check("Apply Coupon to Booking (200)", "POST", "/coupons/apply", r, (200,))

    # 8.7 Update Coupon (Admin)
    r = client.put(f"/coupons/{coupon_id}", headers=admin["headers"], json={
        "discount_value": 20.0,
    })
    check("Update Coupon (200)", "PUT", f"/coupons/{coupon_id}", r, (200,))

    # 8.8 Delete Coupon (Admin)
    r = client.delete(f"/coupons/{coupon_id}", headers=admin["headers"])
    check("Delete Coupon (200)", "DELETE", f"/coupons/{coupon_id}", r, (200,))


# ==============================================================================
# 9. INVOICES APIS
# ==============================================================================
def test_invoices_api(customer: dict, admin: dict, booking_id: int):
    log_step("9. INVOICES & BILLING APIS (/invoices)")

    # 9.1 Create Invoice (Admin)
    r = client.post("/invoices/", headers=admin["headers"], json={
        "booking_id": booking_id,
        "subtotal": 699.0,
        "discount_amount": 50.0,
        "tax_percentage": 18.0,
        "total_amount": 765.82,
        "amount_paid": 765.82,
        "notes": "Original tax invoice.",
    })
    check("Create Invoice (201)", "POST", "/invoices/", r, (201,))
    invoice = r.json()
    invoice_id = invoice["id"]
    invoice_number = invoice["invoice_number"]

    # 9.2 List Invoices (Customer & Admin)
    r = client.get("/invoices/", headers=customer["headers"])
    check("List Customer Invoices (200)", "GET", "/invoices/", r, (200,))

    r = client.get("/invoices/", headers=admin["headers"])
    check("List Admin Invoices (200)", "GET", "/invoices/", r, (200,))

    # 9.3 Get Invoice by ID
    r = client.get(f"/invoices/{invoice_id}", headers=customer["headers"])
    check("Get Invoice By ID (200)", "GET", f"/invoices/{invoice_id}", r, (200,))

    # 9.4 Get Invoice by Number
    r = client.get(f"/invoices/number/{invoice_number}", headers=admin["headers"])
    check("Get Invoice By Number (200)", "GET", f"/invoices/number/{invoice_number}", r, (200,))

    # 9.5 Update Invoice
    r = client.put(f"/invoices/{invoice_id}", headers=admin["headers"], json={
        "notes": "Updated invoice notes - paid in full.",
    })
    check("Update Invoice (200)", "PUT", f"/invoices/{invoice_id}", r, (200,))

    # 9.6 Issue Invoice
    r = client.post(f"/invoices/{invoice_id}/issue", headers=admin["headers"])
    check("Issue Invoice (200)", "POST", f"/invoices/{invoice_id}/issue", r, (200,))


# ==============================================================================
# 10. REVIEWS & RATINGS APIS
# ==============================================================================
def test_reviews_api(customer: dict, admin: dict, booking_id: int, technician_id: int):
    log_step("10. REVIEWS & RATINGS APIS (/reviews)")

    # 10.1 Create Review
    r = client.post("/reviews/", headers=customer["headers"], json={
        "booking_id": booking_id,
        "rating": 5,
        "comment": "Exceptional service, punctual and polite!",
    })
    check("Create Review (201)", "POST", "/reviews/", r, (201,))
    review = r.json()
    review_id = review["id"]

    # 10.2 List Reviews (Public)
    r = client.get("/reviews/")
    check("List Reviews Public (200)", "GET", "/reviews/", r, (200,))

    # 10.3 Get Review by ID
    r = client.get(f"/reviews/{review_id}")
    check("Get Review By ID (200)", "GET", f"/reviews/{review_id}", r, (200,))

    # 10.4 Patch Review
    r = client.patch(f"/reviews/{review_id}", headers=customer["headers"], json={
        "comment": "Exceptional service, very professional!",
    })
    check("Patch Review (200)", "PATCH", f"/reviews/{review_id}", r, (200,))

    # 10.5 Update Review (PUT)
    r = client.put(f"/reviews/{review_id}", headers=customer["headers"], json={
        "rating": 5,
        "comment": "Completely satisfied with the job.",
    })
    check("Update Review (200)", "PUT", f"/reviews/{review_id}", r, (200,))

    # 10.6 Get Technician Reviews
    r = client.get(f"/reviews/technician/{technician_id}")
    check("Get Technician Reviews (200)", "GET", f"/reviews/technician/{technician_id}", r, (200,))

    # 10.7 Get Technician Rating Summary
    r = client.get(f"/reviews/technician/{technician_id}/summary")
    check("Get Technician Rating Summary (200)", "GET", f"/reviews/technician/{technician_id}/summary", r, (200,))


# ==============================================================================
# 11. NOTIFICATIONS APIS
# ==============================================================================
def test_notifications_api(customer: dict, admin: dict):
    log_step("11. NOTIFICATIONS & DISPATCH APIS (/notifications)")

    # 11.1 Create Notification (Admin)
    r = client.post("/notifications/", headers=admin["headers"], json={
        "user_id": customer["user_id"],
        "title": "Welcome to HomiQ",
        "message": "Thank you for using our platform.",
        "notification_type": "general",
    })
    check("Create Notification (201)", "POST", "/notifications/", r, (201,))
    notif = r.json()
    notif_id = notif["id"]

    # 11.2 List Notifications
    r = client.get("/notifications/", headers=customer["headers"])
    check("List Notifications (200)", "GET", "/notifications/", r, (200,))

    # 11.3 Get Unread Notifications
    r = client.get("/notifications/unread", headers=customer["headers"])
    check("Get Unread Notifications (200)", "GET", "/notifications/unread", r, (200,))

    # 11.4 Mark As Read (PATCH)
    r = client.patch(f"/notifications/{notif_id}/read", headers=customer["headers"])
    check("Patch Mark As Read (200)", "PATCH", f"/notifications/{notif_id}/read", r, (200,))

    # 11.5 Mark As Read (PUT)
    r = client.put(f"/notifications/{notif_id}/read", headers=customer["headers"])
    check("Put Mark As Read (200)", "PUT", f"/notifications/{notif_id}/read", r, (200,))

    # 11.6 Mark Multiple As Read
    r = client.post("/notifications/read-multiple", headers=customer["headers"], json={
        "ids": [notif_id],
    })
    check("Mark Multiple As Read (200)", "POST", "/notifications/read-multiple", r, (200,))

    # 11.7 Mark All As Read (PUT & PATCH)
    r = client.put("/notifications/read-all", headers=customer["headers"])
    check("Put Mark All As Read (200)", "PUT", "/notifications/read-all", r, (200,))

    r = client.patch("/notifications/read-all", headers=customer["headers"])
    check("Patch Mark All As Read (200)", "PATCH", "/notifications/read-all", r, (200,))

    # 11.8 Dispatch Multi-Channel Notification
    r = client.post("/notifications/dispatch", headers=admin["headers"], json={
        "user_id": customer["user_id"],
        "title": "Service Update",
        "message": "Your technician has arrived.",
        "channels": ["in_app", "email"],
    })
    check("Dispatch Multi-Channel Notif (200)", "POST", "/notifications/dispatch", r, (200,))

    # 11.9 Delete Notification
    r = client.delete(f"/notifications/{notif_id}", headers=customer["headers"])
    check("Delete Notification (200)", "DELETE", f"/notifications/{notif_id}", r, (200,))


# ==============================================================================
# 12. TRACKING, LOCATION & GOOGLE MAPS APIS
# ==============================================================================
def test_tracking_and_maps_api(customer: dict, technician: dict, booking_id: int):
    log_step("12. TRACKING, LIVE LOCATION & MAPS APIS (/tracking, /location, /maps)")

    # 12.1 Update Location (POST /location/update)
    r = client.post("/location/update", headers=technician["headers"], json={
        "booking_id": booking_id,
        "latitude": 12.9716,
        "longitude": 77.5946,
        "speed": 22.5,
        "heading": 90.0,
        "eta_minutes": 15,
    })
    check("Update Live Location POST (200)", "POST", "/location/update", r, (200,))

    # 12.2 Get Current Location (/location/current)
    r = client.get("/location/current", headers=technician["headers"])
    check("Get Current Location (200)", "GET", "/location/current", r, (200,))

    # 12.3 Get Location for Booking (/location/booking/{id})
    r = client.get(f"/location/booking/{booking_id}", headers=customer["headers"])
    check("Get Booking Location & ETA (200)", "GET", f"/location/booking/{booking_id}", r, (200,))

    # 12.4 Legacy Tracking PUT /tracking/{id}/location
    r = client.put(f"/tracking/{booking_id}/location", headers=technician["headers"], json={
        "latitude": 12.9720,
        "longitude": 77.5950,
        "speed": 18.0,
        "heading": 120.0,
    })
    check("Update Location Legacy PUT (200)", "PUT", f"/tracking/{booking_id}/location", r, (200,))

    # 12.5 Legacy Tracking GET /tracking/{id}/location
    r = client.get(f"/tracking/{booking_id}/location", headers=customer["headers"])
    check("Get Location Legacy GET (200)", "GET", f"/tracking/{booking_id}/location", r, (200,))

    # 12.6 Legacy Tracking History GET /tracking/{id}/history
    r = client.get(f"/tracking/{booking_id}/history", headers=customer["headers"])
    check("Get Tracking History (200)", "GET", f"/tracking/{booking_id}/history", r, (200,))

    # 12.7 Legacy Tracking Me GET /tracking/me/location
    r = client.get("/tracking/me/location", headers=technician["headers"])
    check("Get Tech My Location (200)", "GET", "/tracking/me/location", r, (200,))

    # 12.8 Maps Geocode (Mock or Live)
    r = client.get("/maps/geocode?address=Indiranagar%20Bengaluru", headers=customer["headers"])
    check("Maps Geocode Address (200)", "GET", "/maps/geocode", r, (200,))

    # 12.9 Maps Reverse Geocode
    r = client.get("/maps/reverse-geocode?latitude=12.9716&longitude=77.5946", headers=customer["headers"])
    check("Maps Reverse Geocode (200)", "GET", "/maps/reverse-geocode", r, (200,))

    # 12.10 Maps ETA Calculation
    r = client.get("/maps/eta?origin_lat=12.9716&origin_lng=77.5946&dest_lat=12.9800&dest_lng=77.6000", headers=customer["headers"])
    check("Maps Calculate ETA (200)", "GET", "/maps/eta", r, (200,))

    # 12.11 Maps Nearby Technicians
    r = client.get("/maps/nearby-technicians?latitude=12.9716&longitude=77.5946&radius_km=30", headers=customer["headers"])
    check("Maps Find Nearby Technicians (200)", "GET", "/maps/nearby-technicians", r, (200,))


# ==============================================================================
# 13. JOBS & APPLICATIONS APIS
# ==============================================================================
def test_jobs_api(company: dict, technician: dict):
    log_step("13. JOBS & APPLICATIONS APIS (/jobs)")

    # 13.1 Create Job Post (Company)
    r = client.post("/jobs/", headers=company["headers"], json={
        "title": "Senior AC & HVAC Technician",
        "description": "Looking for experienced AC technician for multi-unit apartment maintenance.",
        "requirements": "3+ years experience in VRV/VRF systems, valid certification.",
        "is_active": True,
    })
    check("Create Job Post (201)", "POST", "/jobs/", r, (201,))
    job = r.json()
    job_id = job["id"]

    # 13.2 List Active Job Posts (Technician discovery)
    r = client.get("/jobs/", headers=technician["headers"])
    check("List Active Job Posts (200)", "GET", "/jobs/", r, (200,))

    # 13.3 List My Job Posts (Company)
    r = client.get("/jobs/my", headers=company["headers"])
    check("List Company My Job Posts (200)", "GET", "/jobs/my", r, (200,))

    # 13.4 Get Job Post by ID
    r = client.get(f"/jobs/{job_id}", headers=technician["headers"])
    check("Get Job Post By ID (200)", "GET", f"/jobs/{job_id}", r, (200,))

    # 13.5 Apply to Job Post (Technician)
    r = client.post(f"/jobs/{job_id}/apply", headers=technician["headers"], json={
        "cover_letter": "I have 6 years experience in residential and commercial AC maintenance.",
    })
    check("Technician Apply to Job (201)", "POST", f"/jobs/{job_id}/apply", r, (201,))
    app_data = r.json()
    app_id = app_data["id"]

    # 13.6 List Job Applications (Company)
    r = client.get(f"/jobs/{job_id}/applications", headers=company["headers"])
    check("Company List Job Applicants (200)", "GET", f"/jobs/{job_id}/applications", r, (200,))

    # 13.7 Update Application Status (Company)
    r = client.put(f"/jobs/applications/{app_id}/status", headers=company["headers"], json={
        "status": "shortlisted",
    })
    check("Company Shortlist Applicant (200)", "PUT", f"/jobs/applications/{app_id}/status", r, (200,))

    # 13.8 List My Applications (Technician)
    r = client.get("/jobs/applications/my", headers=technician["headers"])
    check("Technician My Applications (200)", "GET", "/jobs/applications/my", r, (200,))

    # 13.9 Update Job Post (Company)
    r = client.put(f"/jobs/{job_id}", headers=company["headers"], json={
        "title": "Lead HVAC & Electrical Technician",
    })
    check("Company Update Job Post (200)", "PUT", f"/jobs/{job_id}", r, (200,))


# ==============================================================================
# 14. MEDIA & CLOUDINARY APIS
# ==============================================================================
def test_media_api(customer: dict, admin: dict):
    log_step("14. MEDIA & CLOUDINARY UPLOAD APIS (/media)")

    # 14.1 Upload Media File
    fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
    r = client.post(
        "/media/upload",
        headers=customer["headers"],
        data={"folder": "homiq/tests"},
        files={"file": ("test_asset.png", fake_img, "image/png")}
    )
    check("Upload Media File (201)", "POST", "/media/upload", r, (201,))
    media_data = r.json() if r.status_code == 201 else {}
    public_id = media_data.get("public_id", "homiq/tests/mock_id")

    # 14.2 Get Media Details
    r = client.get(f"/media/{public_id}")
    check("Get Media Asset Details (200)", "GET", f"/media/{public_id}", r, (200,))

    # 14.3 Delete Media File
    r = client.delete(f"/media/{public_id}", headers=customer["headers"])
    check("Delete Media Asset (200)", "DELETE", f"/media/{public_id}", r, (200,))


# ==============================================================================
# 15. REPORTS & ANALYTICS APIS
# ==============================================================================
def test_reports_and_analytics_api(customer: dict, technician: dict, admin: dict):
    log_step("15. REPORTS & ANALYTICS APIS (/reports, /analytics)")

    # 15.1 Admin Full Analytics
    r = client.get("/analytics/admin", headers=admin["headers"])
    check("Admin Full Analytics (200)", "GET", "/analytics/admin", r, (200,))

    # 15.2 Customer Personal Analytics
    r = client.get("/analytics/customer", headers=customer["headers"])
    check("Customer Personal Analytics (200)", "GET", "/analytics/customer", r, (200,))

    # 15.3 Technician Personal Analytics
    r = client.get("/analytics/technician", headers=technician["headers"])
    check("Technician Personal Analytics (200)", "GET", "/analytics/technician", r, (200,))

    # 15.4 Periodic Business Reports (Admin)
    r = client.get("/reports/daily", headers=admin["headers"])
    check("Daily Business Report (200)", "GET", "/reports/daily", r, (200,))

    r = client.get("/reports/weekly", headers=admin["headers"])
    check("Weekly Business Report (200)", "GET", "/reports/weekly", r, (200,))

    r = client.get("/reports/monthly", headers=admin["headers"])
    check("Monthly Business Report (200)", "GET", "/reports/monthly", r, (200,))

    r = client.get("/reports/yearly", headers=admin["headers"])
    check("Yearly Business Report (200)", "GET", "/reports/yearly", r, (200,))

    # 15.5 Export Reports (CSV)
    r = client.get("/reports/export?format=csv&period=monthly", headers=admin["headers"])
    check("Export Reports CSV (200)", "GET", "/reports/export", r, (200,))


# ==============================================================================
# 16. SEARCH & RECOMMENDATIONS APIS
# ==============================================================================
def test_search_and_recommendations_api(customer: dict):
    log_step("16. SEARCH, AUTOCOMPLETE & RECOMMENDATION APIS (/search, /recommendations)")

    # 16.1 Global Search
    r = client.get("/search?q=repair&limit=10")
    check("Global Unified Search (200)", "GET", "/search", r, (200,))

    # 16.2 Search Services
    r = client.get("/search/services?q=AC&sort_by=popular")
    check("Search Services (200)", "GET", "/search/services", r, (200,))

    # 16.3 Search Technicians
    r = client.get("/search/technicians?city=Bengaluru&sort_by=rating_desc")
    check("Search Technicians (200)", "GET", "/search/technicians", r, (200,))

    # 16.4 Search Bookings
    r = client.get("/search/bookings", headers=customer["headers"])
    check("Search Bookings (200)", "GET", "/search/bookings", r, (200,))

    # 16.5 Live Autocomplete Suggestions
    r = client.get("/search/suggestions?q=cle")
    check("Live Autocomplete Suggestions (200)", "GET", "/search/suggestions", r, (200,))

    # 16.6 Recent Searches
    r = client.get("/search/recent", headers=customer["headers"])
    check("Get Recent Searches (200)", "GET", "/search/recent", r, (200,))

    # 16.7 Unified Recommendations
    r = client.get("/recommendations", headers=customer["headers"])
    check("Unified Recommendations (200)", "GET", "/recommendations", r, (200,))

    # 16.8 Service Recommendations
    r = client.get("/recommendations/services", headers=customer["headers"])
    check("Service Recommendations (200)", "GET", "/recommendations/services", r, (200,))

    # 16.9 Technician Recommendations
    r = client.get("/recommendations/technicians", headers=customer["headers"])
    check("Technician Recommendations (200)", "GET", "/recommendations/technicians", r, (200,))


# ==============================================================================
# 17. SECURITY & SESSIONS APIS
# ==============================================================================
def test_security_and_sessions_api(customer: dict, admin: dict):
    log_step("17. SECURITY, ACTIVE SESSIONS & AUDIT LOGS APIS (/security)")

    # 17.1 List Active Device Sessions
    r = client.get("/security/sessions", headers=customer["headers"])
    check("List Active Sessions (200)", "GET", "/security/sessions", r, (200,))

    # 17.2 Logout All Devices
    r = client.delete("/security/logout-all", headers=customer["headers"])
    check("Logout All Devices (200)", "DELETE", "/security/logout-all", r, (200,))

    # 17.3 Query Security Audit Logs (Admin)
    r = client.get("/security/audit-logs?limit=20", headers=admin["headers"])
    check("Query Security Audit Logs (200)", "GET", "/security/audit-logs", r, (200,))


# ==============================================================================
# 18. TASKS & SCHEDULER APIS
# ==============================================================================
def test_tasks_and_scheduler_api(admin: dict):
    log_step("18. BACKGROUND TASKS & SCHEDULER APIS (/tasks, /scheduler)")

    # 18.1 Get Background Task Status
    r = client.get("/tasks/status/mock_task_id_123", headers=admin["headers"])
    check("Get Task Status (200)", "GET", "/tasks/status/mock_task_id_123", r, (200,))

    # 18.2 Retry Failed Task (Admin)
    r = client.post("/tasks/retry/mock_task_id_123", headers=admin["headers"])
    check("Retry Background Task (200)", "POST", "/tasks/retry/mock_task_id_123", r, (200,))

    # 18.3 List Scheduled Jobs (Admin)
    r = client.get("/scheduler/jobs", headers=admin["headers"])
    check("List Scheduled Jobs (200)", "GET", "/scheduler/jobs", r, (200,))


# ==============================================================================
# 19. SYSTEM MONITORING & HEALTH APIS
# ==============================================================================
def test_monitoring_and_health_api(customer: dict, admin: dict):
    log_step("19. MONITORING, PROMETHEUS & HEALTH APIS (/health, /metrics, /dashboard)")

    # 19.1 Basic Health Check
    r = client.get("/health")
    check("Health Check (/health) (200)", "GET", "/health", r, (200,))

    # 19.2 Detailed Health Diagnostics
    r = client.get("/health/detail")
    check("Detailed Health Diagnostics (200/503)", "GET", "/health/detail", r, (200, 503))

    # 19.3 Prometheus Metrics
    r = client.get("/metrics")
    check("Prometheus Metrics (200)", "GET", "/metrics", r, (200,))

    # 19.4 Role-aware Root Dashboard (/dashboard)
    r = client.get("/dashboard", headers=customer["headers"])
    check("Root Role Dashboard (Customer) (200)", "GET", "/dashboard", r, (200,))

    r = client.get("/dashboard", headers=admin["headers"])
    check("Root Role Dashboard (Admin) (200)", "GET", "/dashboard", r, (200,))


# ==============================================================================
# 20. ADMIN PANEL ENDPOINTS
# ==============================================================================
def test_admin_panel_api(admin: dict, customer: dict, booking_id: int):
    log_step("20. ADMIN PANEL MANAGEMENT & CONTROL APIS (/admin/*)")

    # 20.1 Admin Dashboard
    r = client.get("/admin/dashboard", headers=admin["headers"])
    check("Admin Dashboard (200)", "GET", "/admin/dashboard", r, (200,))

    # 20.2 List Users
    r = client.get("/admin/users", headers=admin["headers"])
    check("Admin List Users (200)", "GET", "/admin/users", r, (200,))

    # 20.3 Get User Detail
    r = client.get(f"/admin/users/{customer['user_id']}", headers=admin["headers"])
    check("Admin Get User Details (200)", "GET", f"/admin/users/{customer['user_id']}", r, (200,))

    # 20.4 List Technicians
    r = client.get("/admin/technicians", headers=admin["headers"])
    check("Admin List Technicians (200)", "GET", "/admin/technicians", r, (200,))

    # 20.5 List Admin Bookings
    r = client.get("/admin/bookings", headers=admin["headers"])
    check("Admin List Bookings (200)", "GET", "/admin/bookings", r, (200,))

    # 20.6 Get Booking Details
    r = client.get(f"/admin/bookings/{booking_id}", headers=admin["headers"])
    check("Admin Get Booking (200)", "GET", f"/admin/bookings/{booking_id}", r, (200,))

    # 20.7 Get Booking Audit Logs
    r = client.get(f"/admin/bookings/{booking_id}/logs", headers=admin["headers"])
    check("Admin Booking Logs (200)", "GET", f"/admin/bookings/{booking_id}/logs", r, (200,))

    # 20.8 Admin Categories
    r = client.get("/admin/categories", headers=admin["headers"])
    check("Admin List Categories (200)", "GET", "/admin/categories", r, (200,))

    # 20.9 Admin Coupons
    r = client.get("/admin/coupons", headers=admin["headers"])
    check("Admin List Coupons (200)", "GET", "/admin/coupons", r, (200,))

    # 20.10 Admin Invoices
    r = client.get("/admin/invoices", headers=admin["headers"])
    check("Admin List Invoices (200)", "GET", "/admin/invoices", r, (200,))

    # 20.11 Admin Reviews
    r = client.get("/admin/reviews", headers=admin["headers"])
    check("Admin List Reviews (200)", "GET", "/admin/reviews", r, (200,))

    # 20.12 Admin Reports & Analytics
    r = client.get("/admin/reports", headers=admin["headers"])
    check("Admin Reports Overview (200)", "GET", "/admin/reports", r, (200,))

    r = client.get("/admin/reports/revenue", headers=admin["headers"])
    check("Admin Revenue Report (200)", "GET", "/admin/reports/revenue", r, (200,))

    r = client.get("/admin/reports/bookings", headers=admin["headers"])
    check("Admin Bookings Report (200)", "GET", "/admin/reports/bookings", r, (200,))

    r = client.get("/admin/reports/technicians", headers=admin["headers"])
    check("Admin Technicians Report (200)", "GET", "/admin/reports/technicians", r, (200,))

    r = client.get("/admin/analytics/overview", headers=admin["headers"])
    check("Admin Analytics Overview (200)", "GET", "/admin/analytics/overview", r, (200,))

    r = client.get("/admin/analytics/growth", headers=admin["headers"])
    check("Admin Growth Analytics (200)", "GET", "/admin/analytics/growth", r, (200,))

    r = client.get("/admin/analytics/customers", headers=admin["headers"])
    check("Admin Customer Analytics (200)", "GET", "/admin/analytics/customers", r, (200,))

    r = client.get("/admin/analytics/bookings", headers=admin["headers"])
    check("Admin Booking Analytics (200)", "GET", "/admin/analytics/bookings", r, (200,))

    r = client.get("/admin/analytics/revenue", headers=admin["headers"])
    check("Admin Revenue Analytics (200)", "GET", "/admin/analytics/revenue", r, (200,))

    # 20.13 Platform Settings
    r = client.get("/admin/settings", headers=admin["headers"])
    check("Admin Get Platform Settings (200)", "GET", "/admin/settings", r, (200,))

    r = client.put("/admin/settings", headers=admin["headers"], json={
        "commission_percentage": 12.5,
        "tax_percentage": 18.0,
    })
    check("Admin Update Platform Settings (200)", "PUT", "/admin/settings", r, (200,))


# ==============================================================================
# 21. CHAT HISTORY & REST COMPATIBILITY
# ==============================================================================
def test_chat_and_websocket_api(customer: dict, booking_id: int):
    log_step("21. WEBSOCKET HELPERS & CHAT HISTORY (/chat, /ws)")

    # 21.1 Get Chat History for Booking
    r = client.get(f"/chat/{booking_id}/history", headers=customer["headers"])
    check("Get Chat History (200)", "GET", f"/chat/{booking_id}/history", r, (200,))


# ==============================================================================
# MAIN TEST RUNNER
# ==============================================================================
def main():
    print("=" * 80)
    print("HOMIQ BACKEND - MASTER COMPREHENSIVE API TEST SUITE")
    print(f"Timestamp: {datetime.datetime.now().isoformat()}")
    print("=" * 80)

    # 1. Setup Role Personas
    log_step("0. SETUP TEST ACTORS & TOKENS")
    customer = register_user("customer", "master_cust")
    technician = register_user("technician", "master_tech")
    company = register_user("company", "master_comp")
    admin = login_admin()

    print(f"  Customer Registered:   {customer['email']} (ID: {customer['user_id']})")
    print(f"  Technician Registered: {technician['email']} (ID: {technician['user_id']})")
    print(f"  Company Registered:    {company['email']} (ID: {company['user_id']})")
    print(f"  Admin Logged In:       {admin['email']}")

    # 2. Execute Test Suites Sequentially
    test_auth_api(customer, admin)
    cust_data = test_customer_api(customer, technician)
    test_technician_api(technician, customer, admin)
    test_company_api(company)
    svc_data = test_services_api(admin)

    booking_data = test_bookings_and_lifecycle_api(
        customer=customer,
        technician=technician,
        admin=admin,
        service_id=svc_data["service_id"],
        address_id=cust_data["primary_address_id"],
    )

    booking_id = booking_data["booking_id"]
    technician_id = booking_data["technician_id"]

    test_payments_api(customer, admin, booking_id)
    test_coupons_api(customer, admin, booking_id)
    test_invoices_api(customer, admin, booking_id)
    test_reviews_api(customer, admin, booking_id, technician_id)
    test_notifications_api(customer, admin)
    test_tracking_and_maps_api(customer, technician, booking_id)
    test_jobs_api(company, technician)
    test_media_api(customer, admin)
    test_reports_and_analytics_api(customer, technician, admin)
    test_search_and_recommendations_api(customer)
    test_security_and_sessions_api(customer, admin)
    test_tasks_and_scheduler_api(admin)
    test_monitoring_and_health_api(customer, admin)
    test_admin_panel_api(admin, customer, booking_id)
    test_chat_and_websocket_api(customer, booking_id)

    # 3. Final Summary Report
    elapsed = time.time() - START_TIME
    print("\n" + "=" * 80)
    print("HOMIQ BACKEND API TEST SUMMARY")
    print("=" * 80)
    print(f"Total Tests Executed: {len(PASSED_TESTS) + len(FAILED_TESTS)}")
    print(f"Total Passed:         {len(PASSED_TESTS)}")
    print(f"Total Failed:         {len(FAILED_TESTS)}")
    print(f"Duration:             {elapsed:.2f} seconds")
    print("=" * 80)

    if FAILED_TESTS:
        print("\nFAILURE DETAILS:")
        for name, ep, code, err in FAILED_TESTS:
            print(f"  - [{code}] {name} ({ep}) -> {err}")
        print("\nSTATUS: SOME TESTS FAILED")
        return 1
    else:
        print("\nSTATUS: ALL BACKEND APIS TESTED AND PASSED SUCCESSFULLY!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
