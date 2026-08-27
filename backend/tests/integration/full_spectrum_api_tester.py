"""
==============================================================================
HomiQ Backend - Full-Spectrum OpenAPI Comprehensive Auditor & Test Suite
Covers 100% of all registered OpenAPI endpoints & HTTP methods across all 21 routers:
- Dedicated test personas: Customer, Technician, Company, Admin, Unauthenticated
- Contextual state chain (IDs captured & threaded through dependent flows)
- Complete Booking state machine & SmartVerify (QR & OTP) verification
- Technician booking patch workflows & Admin override workflows
- Positive (2xx), Validation (422/400), Auth (401), Role (403), Not-Found (404),
  Conflict/State (409) test cases
- Generates exhaustive execution report
==============================================================================
"""

from __future__ import annotations

import datetime
import io
import json
import os
import sys
import time
import traceback
import uuid
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@dataclass
class TestResult:
    test_id: str
    category: str  # POSITIVE, AUTH_401, ROLE_403, VALIDATION_422_400, NOT_FOUND_404, STATE_409
    method: str
    path: str
    description: str
    actor: str
    request_summary: str
    expected_status: List[int]
    actual_status: int
    passed: bool
    duration_ms: float
    error_detail: Optional[str] = None
    code_changed: Optional[str] = None

class FullSpectrumAPITester:
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
        self.password = "TestPassword@1234"
        self.context: Dict[str, Any] = {}

    def uid(self, prefix: str = "t") -> str:
        return f"{prefix}_{uuid.uuid4().hex[:8]}"

    def gen_email(self, role: str) -> str:
        return f"test_{role}_{uuid.uuid4().hex[:8]}@example.com"

    def future_date(self, days: int = 3) -> str:
        return (datetime.date.today() + datetime.timedelta(days=days)).isoformat()

    def run_case(
        self,
        test_id: str,
        category: str,
        method: str,
        path: str,
        description: str,
        actor: str,
        expected_status: List[int],
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Any] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        code_changed: Optional[str] = None,
    ) -> Any:
        t0 = time.time()
        kw: Dict[str, Any] = {}
        if headers:
            kw["headers"] = headers
        if json_data is not None:
            kw["json"] = json_data
        if params is not None:
            kw["params"] = params
        if files is not None:
            kw["files"] = files
        if data is not None:
            kw["data"] = data

        req_summary = f"body={json.dumps(json_data)[:80]}" if json_data else (f"params={params}" if params else "no_body")

        try:
            resp = client.request(method, path, **kw)
            duration_ms = round((time.time() - t0) * 1000, 2)
            actual_status = resp.status_code
            passed = actual_status in expected_status

            sample = resp.text[:300].replace("\n", " ") if resp.text else ""
            err = None if passed else f"Expected {expected_status} but received {actual_status}: {sample}"

            res = TestResult(
                test_id=test_id,
                category=category,
                method=method,
                path=path,
                description=description,
                actor=actor,
                request_summary=req_summary,
                expected_status=expected_status,
                actual_status=actual_status,
                passed=passed,
                duration_ms=duration_ms,
                error_detail=err,
                code_changed=code_changed,
            )
            self.results.append(res)

            status_tag = "PASS" if passed else "FAIL"
            print(f"  [{status_tag}] {test_id:<34} | {category:<18} | {method:<6} {path:<45} -> {actual_status} ({duration_ms}ms)")
            if not passed:
                print(f"         DETAIL: {err}")
            return resp
        except Exception as exc:
            duration_ms = round((time.time() - t0) * 1000, 2)
            tb = traceback.format_exc()
            res = TestResult(
                test_id=test_id,
                category=category,
                method=method,
                path=path,
                description=description,
                actor=actor,
                request_summary=req_summary,
                expected_status=expected_status,
                actual_status=500,
                passed=False,
                duration_ms=duration_ms,
                error_detail=f"Exception: {str(exc)}\n{tb}",
                code_changed=code_changed,
            )
            self.results.append(res)
            print(f"  [ERROR] {test_id:<34} | {category:<18} | {method:<6} {path:<45} -> EXCEPTION: {exc}")
            return None

    def register_persona(self, role: str, prefix: str) -> Dict[str, Any]:
        email = self.gen_email(prefix)
        phone = f"98{uuid.uuid4().int % 100000000:08d}"
        r = client.post("/auth/register", json={
            "email": email,
            "password": self.password,
            "full_name": f"Test {prefix.capitalize()} User",
            "phone": phone,
            "role": role,
        })
        assert r.status_code == 201, f"Failed to register persona {role}: {r.text}"
        data = r.json()
        token = data["access_token"]
        refresh_tok = data.get("refresh_token", "")
        return {
            "email": email,
            "password": self.password,
            "token": token,
            "refresh_token": refresh_tok,
            "user_id": data["user"]["id"],
            "role": role,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    def setup_actors(self):
        print("\n" + "="*80)
        print("PHASE 0: PERSONA SETUP & TOKEN CAPTURE")
        print("="*80)

        # 1. Customer
        self.context["customer"] = self.register_persona("customer", "cust_actor")
        print(f"  [+] Customer Actor:   {self.context['customer']['email']} (User ID: {self.context['customer']['user_id']})")

        # 2. Technician 1
        self.context["technician"] = self.register_persona("technician", "tech_actor")
        print(f"  [+] Technician 1:     {self.context['technician']['email']} (User ID: {self.context['technician']['user_id']})")

        # 3. Technician 2 (for reassignments)
        self.context["technician_2"] = self.register_persona("technician", "tech2_actor")
        print(f"  [+] Technician 2:     {self.context['technician_2']['email']} (User ID: {self.context['technician_2']['user_id']})")

        # 4. Company
        self.context["company"] = self.register_persona("company", "comp_actor")
        print(f"  [+] Company Actor:    {self.context['company']['email']} (User ID: {self.context['company']['user_id']})")

        # 5. Admin (Superuser)
        admin_email = "admin_master@homiq.com"
        r = client.post("/auth/login", json={"identifier": admin_email, "password": self.password})
        if r.status_code == 200:
            data = r.json()
            self.context["admin"] = {
                "email": admin_email,
                "token": data["access_token"],
                "refresh_token": data.get("refresh_token", ""),
                "user_id": data["user"]["id"],
                "role": "admin",
                "headers": {"Authorization": f"Bearer {data['access_token']}"},
            }
        else:
            self.context["admin"] = self.register_persona("admin", "admin_actor")
        print(f"  [+] Admin Actor:      {self.context['admin']['email']} (User ID: {self.context['admin']['user_id']})")

        # 6. Anon
        self.context["anon"] = {"headers": {}}

    def test_auth_suite(self):
        print("\n" + "="*80)
        print("PHASE 1: AUTH & IDENTITY APIS (/auth)")
        print("="*80)
        c = self.context["customer"]

        self.run_case(
            "AUTH_REG_DUP", "VALIDATION_422_400", "POST", "/auth/register",
            "Register with already existing email", "anonymous", [400],
            json_data={"email": c["email"], "password": self.password, "full_name": "Dup", "phone": "9999999999", "role": "customer"}
        )
        self.run_case(
            "AUTH_REG_INVALID", "VALIDATION_422_400", "POST", "/auth/register",
            "Register with invalid email format", "anonymous", [422],
            json_data={"email": "not-an-email", "password": "123", "full_name": "Dup", "phone": "123", "role": "customer"}
        )
        self.run_case(
            "AUTH_LOGIN_OK", "POSITIVE", "POST", "/auth/login",
            "Login with valid credentials", "anonymous", [200],
            json_data={"email": c["email"], "password": self.password}
        )
        self.run_case(
            "AUTH_LOGIN_BAD_PWD", "AUTH_401", "POST", "/auth/login",
            "Login with incorrect password", "anonymous", [401],
            json_data={"email": c["email"], "password": "WrongPassword123!"}
        )
        self.run_case(
            "AUTH_REFRESH_OK", "POSITIVE", "POST", f"/auth/refresh?refresh_token={c['refresh_token']}",
            "Refresh JWT access token", "anonymous", [200],
            code_changed="Added get_user_by_id alias to UserCRUD in app/crud/user.py"
        )
        self.run_case(
            "AUTH_REFRESH_BAD", "AUTH_401", "POST", "/auth/refresh?refresh_token=fake_refresh_token_abc",
            "Refresh with invalid refresh token", "anonymous", [401]
        )
        self.run_case(
            "AUTH_FORGOT_PWD", "POSITIVE", "POST", "/auth/forgot-password",
            "Request password reset link/instructions", "anonymous", [200],
            json_data={"email": c["email"]}
        )
        self.run_case(
            "AUTH_RESET_PWD", "POSITIVE", "POST", "/auth/reset-password",
            "Reset user password with valid token payload", "anonymous", [200],
            json_data={"token": "reset_token_sample", "new_password": self.password}
        )
        self.run_case(
            "AUTH_ME_OK", "POSITIVE", "GET", "/auth/me",
            "Get authenticated user profile details", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "AUTH_ME_NO_TOKEN", "AUTH_401", "GET", "/auth/me",
            "Access /auth/me without token", "anonymous", [401, 403],
            headers=self.context["anon"]["headers"]
        )

    def test_customer_suite(self):
        print("\n" + "="*80)
        print("PHASE 2: CUSTOMER PROFILE & ADDRESSES (/customer)")
        print("="*80)
        c = self.context["customer"]
        tech = self.context["technician"]

        self.run_case(
            "CUST_PROF_GET", "POSITIVE", "GET", "/customer/profile",
            "Get customer profile with addresses", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_PROF_PUT", "POSITIVE", "PUT", "/customer/profile",
            "Update customer profile data", "customer", [200],
            headers=c["headers"],
            json_data={"full_name": "Audited Customer", "city": "Bengaluru", "state": "Karnataka", "postal_code": "560001", "preferred_language": "en"}
        )
        fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        self.run_case(
            "CUST_IMG_UPLOAD", "POSITIVE", "POST", "/customer/profile/image",
            "Upload customer profile avatar", "customer", [200],
            headers=c["headers"],
            files={"file": ("profile.png", fake_img, "image/png")}
        )
        resp_addr1 = self.run_case(
            "CUST_ADDR_CREATE_1", "POSITIVE", "POST", "/customer/addresses",
            "Create primary default address", "customer", [201],
            headers=c["headers"],
            json_data={
                "full_name": "Audited Customer", "phone": "9876543210", "house_no": "101",
                "building": "Palm Heights", "landmark": "Near Metro", "area": "Indiranagar",
                "city": "Bengaluru", "state": "Karnataka", "pincode": "560038",
                "latitude": 12.9784, "longitude": 77.6408, "is_default": True,
            }
        )
        addr1_id = resp_addr1.json()["id"] if resp_addr1 and resp_addr1.status_code == 201 else 1
        self.context["address_id"] = addr1_id

        resp_addr2 = self.run_case(
            "CUST_ADDR_CREATE_2", "POSITIVE", "POST", "/customer/addresses",
            "Create secondary non-default address", "customer", [201],
            headers=c["headers"],
            json_data={
                "full_name": "Office Address", "phone": "9876543210", "house_no": "502",
                "building": "Tower B", "area": "Whitefield", "city": "Bengaluru",
                "state": "Karnataka", "pincode": "560066", "is_default": False,
            }
        )
        addr2_id = resp_addr2.json()["id"] if resp_addr2 and resp_addr2.status_code == 201 else 2
        self.context["address_id_2"] = addr2_id

        self.run_case(
            "CUST_ADDR_LIST", "POSITIVE", "GET", "/customer/addresses",
            "List customer addresses", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_ADDR_GET_ID", "POSITIVE", "GET", f"/customer/addresses/{addr1_id}",
            "Get single address by ID", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_ADDR_NOT_FOUND", "NOT_FOUND_404", "GET", "/customer/addresses/999999",
            "Get non-existent customer address ID", "customer", [404],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_ADDR_UPDATE", "POSITIVE", "PUT", f"/customer/addresses/{addr1_id}",
            "Update existing customer address", "customer", [200],
            headers=c["headers"],
            json_data={"landmark": "Opposite Metro Pillar 45"}
        )
        self.run_case(
            "CUST_ADDR_SET_DEFAULT", "POSITIVE", "PUT", f"/customer/addresses/{addr2_id}/default",
            "Set secondary address as default", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_ADDR_DELETE", "POSITIVE", "DELETE", f"/customer/addresses/{addr2_id}",
            "Delete secondary address", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_DASHBOARD", "POSITIVE", "GET", "/customer/dashboard",
            "Get customer stats and recent activity", "customer", [200],
            headers=c["headers"]
        )
        self.run_case(
            "CUST_ROLE_GUARD_TECH", "ROLE_403", "GET", "/customer/profile",
            "Technician role attempting customer profile", "technician", [403],
            headers=tech["headers"]
        )

    def test_technician_suite(self):
        print("\n" + "="*80)
        print("PHASE 3: TECHNICIAN PROFILE & OPERATIONS (/technician)")
        print("="*80)
        tech = self.context["technician"]
        tech2 = self.context["technician_2"]
        cust = self.context["customer"]

        resp_tp = self.run_case(
            "TECH_PROF_GET", "POSITIVE", "GET", "/technician/profile",
            "Get technician profile details", "technician", [200],
            headers=tech["headers"]
        )
        self.context["technician_db_id"] = resp_tp.json()["id"] if resp_tp and resp_tp.status_code == 200 else 1

        resp_tp2 = client.get("/technician/profile", headers=tech2["headers"])
        self.context["technician_2_db_id"] = resp_tp2.json()["id"] if resp_tp2.status_code == 200 else 2

        self.run_case(
            "TECH_PROF_UPDATE", "POSITIVE", "PUT", "/technician/profile",
            "Update technician specialization and skills", "technician", [200],
            headers=tech["headers"],
            json_data={
                "specialization": "HVAC & Electrical",
                "experience_years": 5,
                "skills": ["Split AC", "Inverter PCB", "Wiring"],
                "languages": ["English", "Hindi"],
                "working_hours": "08:00 - 20:00",
                "service_radius_km": 30.0,
                "latitude": 12.9716,
                "longitude": 77.5946,
            }
        )
        fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        self.run_case(
            "TECH_IMG_UPLOAD", "POSITIVE", "POST", "/technician/profile/image",
            "Upload technician profile photo", "technician", [200],
            headers=tech["headers"],
            files={"file": ("tech.png", fake_img, "image/png")}
        )
        fake_doc_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        self.run_case(
            "TECH_GOVT_ID_UPLOAD", "POSITIVE", "POST", "/technician/profile/government-id",
            "Upload technician government ID image", "technician", [200],
            headers=tech["headers"],
            files={"file": ("govt_id.png", fake_doc_img, "image/png")}
        )
        self.run_case(
            "TECH_SET_ONLINE", "POSITIVE", "PATCH", "/technician/online",
            "Mark technician online", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_SET_OFFLINE", "POSITIVE", "PATCH", "/technician/offline",
            "Mark technician offline", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_SET_AVAIL", "POSITIVE", "PUT", "/technician/availability",
            "Update availability & online flags", "technician", [200],
            headers=tech["headers"],
            json_data={"availability": True, "is_online": True}
        )
        self.run_case(
            "TECH_LIST_PUBLIC", "POSITIVE", "GET", "/technician/?specialization=HVAC%20%26%20Electrical",
            "Public search/list technicians", "anonymous", [200]
        )
        self.run_case(
            "TECH_MY_JOBS", "POSITIVE", "GET", "/technician/jobs",
            "Get assigned jobs for technician", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_BOOKINGS", "POSITIVE", "GET", "/technician/bookings",
            "Get technician bookings", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_ACTIVE_BOOKINGS", "POSITIVE", "GET", "/technician/bookings/active",
            "Get in-flight bookings for technician", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_HISTORY", "POSITIVE", "GET", "/technician/history",
            "Get past booking history for technician", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_EARNINGS", "POSITIVE", "GET", "/technician/earnings",
            "Get earnings summary for technician", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_DASHBOARD", "POSITIVE", "GET", "/technician/dashboard",
            "Get technician dashboard metrics", "technician", [200],
            headers=tech["headers"]
        )
        fake_license_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        resp_doc = self.run_case(
            "TECH_DOC_UPLOAD", "POSITIVE", "POST", "/technician/documents",
            "Upload trade certification document", "technician", [201],
            headers=tech["headers"],
            data={"doc_type": "driving_license"},
            files={"file": ("license.png", fake_license_img, "image/png")}
        )
        self.context["tech_doc_id"] = resp_doc.json()["id"] if resp_doc and resp_doc.status_code == 201 else 1

        self.run_case(
            "TECH_DOC_LIST", "POSITIVE", "GET", "/technician/documents",
            "List uploaded verification documents", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TECH_ROLE_GUARD_CUST", "ROLE_403", "GET", "/technician/profile",
            "Customer role attempting technician profile", "customer", [403],
            headers=cust["headers"]
        )

    def test_company_suite(self):
        print("\n" + "="*80)
        print("PHASE 4: COMPANY PROFILE APIS (/company)")
        print("="*80)
        comp = self.context["company"]
        tech = self.context["technician"]

        self.run_case(
            "COMP_PROF_GET", "POSITIVE", "GET", "/company/profile",
            "Get company profile", "company", [200],
            headers=comp["headers"]
        )
        self.run_case(
            "COMP_PROF_UPDATE", "POSITIVE", "PUT", "/company/profile",
            "Update company profile metadata", "company", [200],
            headers=comp["headers"],
            json_data={
                "company_name": "Premier Facility Solutions",
                "industry": "Commercial & Residential Services",
                "description": "Multi-city facilities repair and installation provider.",
                "website": "https://premierfacility.example.com",
            }
        )
        self.run_case(
            "COMP_LIST_PUBLIC", "POSITIVE", "GET", "/company/",
            "List registered companies publicly", "anonymous", [200]
        )
        self.run_case(
            "COMP_ROLE_GUARD_TECH", "ROLE_403", "GET", "/company/profile",
            "Technician role attempting company profile", "technician", [403],
            headers=tech["headers"]
        )

    def test_services_suite(self):
        print("\n" + "="*80)
        print("PHASE 5: SERVICES & CATEGORIES APIS (/services)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]

        cat_name = f"Category_{self.uid('cat')}"
        resp_cat = self.run_case(
            "SVC_CAT_CREATE", "POSITIVE", "POST", "/services/categories",
            "Create new service category (Admin)", "admin", [201],
            headers=admin["headers"],
            json_data={"name": cat_name, "description": "Home AC, Heating and Cooling", "icon": "ac-icon", "is_active": True}
        )
        cat_id = resp_cat.json()["id"] if resp_cat and resp_cat.status_code == 201 else 1
        self.context["category_id"] = cat_id

        self.run_case(
            "SVC_CAT_CREATE_FORBIDDEN", "ROLE_403", "POST", "/services/categories",
            "Customer role attempting category creation", "customer", [403],
            headers=cust["headers"],
            json_data={"name": f"Forbidden_{self.uid()}", "description": "Test"}
        )
        self.run_case(
            "SVC_CAT_LIST", "POSITIVE", "GET", "/services/categories",
            "List all service categories", "anonymous", [200]
        )
        self.run_case(
            "SVC_CAT_GET_ID", "POSITIVE", "GET", f"/services/categories/{cat_id}",
            "Get category by unique ID", "anonymous", [200]
        )
        self.run_case(
            "SVC_CAT_NOT_FOUND", "NOT_FOUND_404", "GET", "/services/categories/999999",
            "Get non-existent category ID", "anonymous", [404]
        )
        self.run_case(
            "SVC_CAT_UPDATE", "POSITIVE", "PUT", f"/services/categories/{cat_id}",
            "Update category details", "admin", [200],
            headers=admin["headers"],
            json_data={"name": f"{cat_name}_Renamed", "description": "Updated description"}
        )

        svc_name = f"AC_Full_Service_{self.uid('svc')}"
        resp_svc = self.run_case(
            "SVC_CREATE", "POSITIVE", "POST", "/services/",
            "Create new service under category", "admin", [201],
            headers=admin["headers"],
            json_data={
                "name": svc_name,
                "description": "Comprehensive AC deep cleaning and gas pressure check.",
                "category_id": cat_id,
                "base_price": 599.0,
                "price": 599.0,
                "duration_minutes": 60,
                "is_active": True,
            }
        )
        svc_id = resp_svc.json()["id"] if resp_svc and resp_svc.status_code == 201 else 1
        self.context["service_id"] = svc_id

        self.run_case(
            "SVC_LIST_FILTER", "POSITIVE", "GET", f"/services/?category_id={cat_id}&min_price=100&max_price=1000",
            "List services with price and category filters", "anonymous", [200]
        )
        self.run_case(
            "SVC_GET_ID", "POSITIVE", "GET", f"/services/{svc_id}",
            "Get service by unique ID", "anonymous", [200]
        )
        self.run_case(
            "SVC_NOT_FOUND", "NOT_FOUND_404", "GET", "/services/999999",
            "Get non-existent service ID", "anonymous", [404]
        )
        self.run_case(
            "SVC_UPDATE", "POSITIVE", "PUT", f"/services/{svc_id}",
            "Update service price and duration", "admin", [200],
            headers=admin["headers"],
            json_data={"price": 649.0, "duration_minutes": 75}
        )
        fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        self.run_case(
            "SVC_IMG_UPLOAD", "POSITIVE", "POST", f"/services/{svc_id}/image",
            "Upload service catalog banner image", "admin", [200],
            headers=admin["headers"],
            files={"file": ("service.png", fake_img, "image/png")},
            code_changed="Made upload_service_image async in app/services/service.py"
        )

    def test_bookings_and_lifecycle_suite(self):
        print("\n" + "="*80)
        print("PHASE 6: BOOKINGS, LIFECYCLE & SMARTVERIFY STATE MACHINE (/bookings)")
        print("="*80)
        cust = self.context["customer"]
        tech = self.context["technician"]
        admin = self.context["admin"]
        svc_id = self.context.get("service_id", 1)
        addr_id = self.context.get("address_id", 1)
        tech_db_id = self.context.get("technician_db_id", 1)

        self.run_case(
            "BOOKING_PAST_DATE", "VALIDATION_422_400", "POST", "/bookings/",
            "Create booking with past date (should fail)", "customer", [422],
            headers=cust["headers"],
            json_data={"service_id": svc_id, "address_id": addr_id, "booking_date": "2020-01-01", "preferred_time": "10:00:00", "estimated_price": 500.0}
        )
        self.run_case(
            "BOOKING_BAD_SVC", "NOT_FOUND_404", "POST", "/bookings/",
            "Create booking with non-existent service ID", "customer", [404],
            headers=cust["headers"],
            json_data={"service_id": 999999, "address_id": addr_id, "booking_date": self.future_date(5), "preferred_time": "10:00:00", "estimated_price": 500.0}
        )
        resp_b = self.run_case(
            "BOOKING_CREATE_OK", "POSITIVE", "POST", "/bookings/",
            "Create booking with valid payload (status: pending)", "customer", [201],
            headers=cust["headers"],
            json_data={
                "service_id": svc_id,
                "address_id": addr_id,
                "booking_date": self.future_date(4),
                "preferred_time": "10:30:00",
                "estimated_price": 649.0,
                "customer_note": "Master test booking note.",
            }
        )
        booking_id = resp_b.json()["id"] if resp_b and resp_b.status_code == 201 else 1
        self.context["booking_id"] = booking_id

        self.run_case(
            "BOOKING_LIST_CUST", "POSITIVE", "GET", "/bookings/",
            "List bookings for authenticated customer", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "BOOKING_LIST_ADMIN", "POSITIVE", "GET", "/bookings/",
            "List all bookings for platform admin", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "BOOKING_GET_ID", "POSITIVE", "GET", f"/bookings/{booking_id}",
            "Get booking details by ID", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "BOOKING_UPDATE", "POSITIVE", "PUT", f"/bookings/{booking_id}",
            "Update customer booking note", "customer", [200],
            headers=cust["headers"],
            json_data={"customer_note": "Updated customer instructions."}
        )
        self.run_case(
            "BOOKING_ASSIGN_FORBIDDEN", "ROLE_403", "PUT", f"/bookings/{booking_id}/assign",
            "Customer role attempting technician assignment", "customer", [403],
            headers=cust["headers"],
            json_data={"technician_id": tech_db_id}
        )
        self.run_case(
            "BOOKING_ADMIN_ASSIGN", "POSITIVE", "PUT", f"/bookings/{booking_id}/assign",
            "Admin assigns technician to booking (status: assigned)", "admin", [200],
            headers=admin["headers"],
            json_data={"technician_id": tech_db_id}
        )
        self.run_case(
            "BOOKING_RESCHEDULE", "POSITIVE", "PUT", f"/bookings/{booking_id}/reschedule",
            "Customer reschedules assigned booking", "customer", [200],
            headers=cust["headers"],
            json_data={"booking_date": self.future_date(6), "preferred_time": "15:00:00"}
        )
        self.run_case(
            "BOOKING_TECH_ACCEPT", "POSITIVE", "POST", f"/bookings/{booking_id}/accept",
            "Technician accepts assigned booking (status: accepted)", "technician", [200],
            headers=tech["headers"],
            json_data={"reason": "Accepting job"}
        )
        self.run_case(
            "BOOKING_DUP_ACCEPT", "STATE_409", "POST", f"/bookings/{booking_id}/accept",
            "Technician duplicate accept on already accepted booking", "technician", [409],
            headers=tech["headers"],
            json_data={"reason": "Duplicate accept"}
        )
        self.run_case(
            "BOOKING_START_TRIP", "POSITIVE", "POST", f"/bookings/{booking_id}/start-trip",
            "Technician starts trip to customer location (status: on_the_way)", "technician", [200],
            headers=tech["headers"],
            json_data={"reason": "En route"}
        )
        self.run_case(
            "BOOKING_INVALID_STATE_JUMP", "STATE_409", "POST", f"/bookings/{booking_id}/complete",
            "Attempt complete when booking is on_the_way (invalid state transition)", "technician", [409],
            headers=tech["headers"],
            json_data={"reason": "Premature completion"}
        )

        # Active Trip Location Updates
        self.run_case(
            "TRACK_UPDATE_POST", "POSITIVE", "POST", "/location/update",
            "Update live technician GPS coordinates", "technician", [200],
            headers=tech["headers"],
            json_data={"booking_id": booking_id, "latitude": 12.9716, "longitude": 77.5946, "speed": 25.0, "heading": 90.0, "eta_minutes": 12}
        )
        self.run_case(
            "TRACK_GET_CURRENT", "POSITIVE", "GET", "/location/current",
            "Get current tracked location for authenticated technician", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "TRACK_GET_BOOKING_LOC", "POSITIVE", "GET", f"/location/booking/{booking_id}",
            "Get live technician location & driving ETA for booking", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "TRACK_GET_TECH_LOC", "POSITIVE", "GET", f"/location/technician/{tech_db_id}",
            "Get live location for specific technician", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "TRACK_LEGACY_ME", "POSITIVE", "GET", "/tracking/me/location",
            "Legacy get technician current location", "technician", [200],
            headers=tech["headers"],
            code_changed="Reordered tracking routes in app/api/tracking/router.py"
        )
        self.run_case(
            "TRACK_LEGACY_PUT", "POSITIVE", "PUT", f"/tracking/{booking_id}/location",
            "Legacy update technician location", "technician", [200],
            headers=tech["headers"],
            json_data={"latitude": 12.9720, "longitude": 77.5950}
        )
        self.run_case(
            "TRACK_LEGACY_GET", "POSITIVE", "GET", f"/tracking/{booking_id}/location",
            "Legacy get latest location for booking", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "TRACK_LEGACY_HIST", "POSITIVE", "GET", f"/tracking/{booking_id}/history",
            "Legacy get tracking history log", "customer", [200],
            headers=cust["headers"]
        )

        self.run_case(
            "BOOKING_ARRIVED", "POSITIVE", "POST", f"/bookings/{booking_id}/arrived",
            "Technician marks arrival at job site (status: arrived)", "technician", [200],
            headers=tech["headers"],
            json_data={"reason": "Arrived at location"}
        )
        resp_qr = self.run_case(
            "SMARTVERIFY_GEN_QR", "POSITIVE", "POST", f"/bookings/{booking_id}/generate-qr",
            "Customer generates encrypted verification QR code", "customer", [200, 201],
            headers=cust["headers"]
        )
        qr_token = resp_qr.json().get("verification_token", "sample_token") if resp_qr and resp_qr.status_code in (200, 201) else "sample_token"

        self.run_case(
            "SMARTVERIFY_GET_QR", "POSITIVE", "GET", f"/bookings/{booking_id}/qr",
            "Retrieve active verification QR token", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "SMARTVERIFY_SCAN_QR", "POSITIVE", "POST", f"/bookings/{booking_id}/scan-qr",
            "Technician scans customer QR code (status: qr_verified)", "technician", [200],
            headers=tech["headers"],
            json_data={"verification_token": qr_token}
        )
        resp_otp = self.run_case(
            "SMARTVERIFY_GEN_OTP", "POSITIVE", "POST", f"/bookings/{booking_id}/generate-otp",
            "Generate service start verification OTP", "customer", [200],
            headers=cust["headers"]
        )
        otp_code = resp_otp.json().get("otp_code", "123456") if resp_otp and resp_otp.status_code == 200 else "123456"

        self.run_case(
            "SMARTVERIFY_VERIFY_OTP", "POSITIVE", "POST", f"/bookings/{booking_id}/verify-otp",
            "Customer verifies OTP and starts service work (status: in_progress)", "customer", [200],
            headers=cust["headers"],
            json_data={"otp_code": otp_code}
        )
        self.run_case(
            "SMARTVERIFY_STATUS", "POSITIVE", "GET", f"/bookings/{booking_id}/verification-status",
            "Check current SmartVerify verification step status", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "BOOKING_COMPLETE", "POSITIVE", "POST", f"/bookings/{booking_id}/complete",
            "Technician completes service job (status: completed)", "technician", [200],
            headers=tech["headers"],
            json_data={"reason": "Service completed and tested"}
        )
        self.run_case(
            "BOOKING_CANCEL_COMPLETED_CONFLICT", "STATE_409", "POST", f"/bookings/{booking_id}/cancel",
            "Attempt to cancel a completed booking (terminal state conflict)", "customer", [409],
            headers=cust["headers"],
            json_data={"reason": "Cancel completed"}
        )
        self.run_case(
            "BOOKING_TRACK", "POSITIVE", "GET", f"/bookings/{booking_id}/track",
            "Track booking status & technician details", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "BOOKING_HISTORY", "POSITIVE", "GET", f"/bookings/{booking_id}/history",
            "Get complete status change audit trail", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "BOOKING_TECH_DETAILS", "POSITIVE", "GET", f"/bookings/{booking_id}/technician",
            "View assigned technician information", "customer", [200],
            headers=cust["headers"]
        )

        # ── Test Technician Alternative Patch Booking Routes ─────────────────────────
        # Create a second booking for tech patch route verification
        resp_b_patch = client.post("/bookings/", headers=cust["headers"], json={
            "service_id": svc_id, "address_id": addr_id, "booking_date": self.future_date(8),
            "preferred_time": "14:00:00", "estimated_price": 599.0,
        })
        bp_id = resp_b_patch.json()["id"] if resp_b_patch.status_code == 201 else 1

        # Admin assigns tech
        client.put(f"/admin/bookings/{bp_id}/assign", headers=admin["headers"], json={"technician_id": tech_db_id})

        # Tech PATCH /technician/bookings/{id}/accept
        self.run_case(
            "TECH_PATCH_ACCEPT", "POSITIVE", "PATCH", f"/technician/bookings/{bp_id}/accept",
            "Technician accepts booking via PATCH route", "technician", [200],
            headers=tech["headers"]
        )
        # Tech PATCH /technician/bookings/{id}/start-trip
        self.run_case(
            "TECH_PATCH_START_TRIP", "POSITIVE", "PATCH", f"/technician/bookings/{bp_id}/start-trip",
            "Technician starts trip via PATCH route", "technician", [200],
            headers=tech["headers"]
        )
        # Tech PATCH /technician/bookings/{id}/arrived
        self.run_case(
            "TECH_PATCH_ARRIVED", "POSITIVE", "PATCH", f"/technician/bookings/{bp_id}/arrived",
            "Technician arrives via PATCH route", "technician", [200],
            headers=tech["headers"]
        )
        # Tech PATCH /technician/bookings/{id}/start-service
        self.run_case(
            "TECH_PATCH_START_SVC", "POSITIVE", "PATCH", f"/technician/bookings/{bp_id}/start-service",
            "Technician starts service work via PATCH route", "technician", [200],
            headers=tech["headers"]
        )
        # Tech PATCH /technician/bookings/{id}/complete
        self.run_case(
            "TECH_PATCH_COMPLETE", "POSITIVE", "PATCH", f"/technician/bookings/{bp_id}/complete",
            "Technician completes service via PATCH route", "technician", [200],
            headers=tech["headers"]
        )

        # ── Test Admin Overrides, Reassignment & Cancellation ─────────────────────
        # Create a third booking for admin override operations
        resp_b_adm = client.post("/bookings/", headers=cust["headers"], json={
            "service_id": svc_id, "address_id": addr_id, "booking_date": self.future_date(9),
            "preferred_time": "16:00:00", "estimated_price": 750.0,
        })
        badm_id = resp_b_adm.json()["id"] if resp_b_adm.status_code == 201 else 1

        # Admin PATCH /admin/bookings/{id}/assign
        self.run_case(
            "ADM_PATCH_ASSIGN", "POSITIVE", "PATCH", f"/admin/bookings/{badm_id}/assign",
            "Admin assigns tech via PATCH route", "admin", [200],
            headers=admin["headers"],
            json_data={"technician_id": tech_db_id}
        )
        # Admin PUT & PATCH /admin/bookings/{id}/reassign
        tech2_id = self.context.get("technician_2_db_id", 2)
        self.run_case(
            "ADM_PUT_REASSIGN", "POSITIVE", "PUT", f"/admin/bookings/{badm_id}/reassign",
            "Admin reassigns tech via PUT route", "admin", [200],
            headers=admin["headers"],
            json_data={"technician_id": tech2_id}
        )
        self.run_case(
            "ADM_PATCH_REASSIGN", "POSITIVE", "PATCH", f"/admin/bookings/{badm_id}/reassign",
            "Admin reassigns tech via PATCH route", "admin", [200],
            headers=admin["headers"],
            json_data={"technician_id": tech_db_id}
        )
        # Admin PUT /admin/bookings/{id}/status
        self.run_case(
            "ADM_PUT_STATUS", "POSITIVE", "PUT", f"/admin/bookings/{badm_id}/status",
            "Admin updates booking status directly", "admin", [200],
            headers=admin["headers"],
            json_data={"status": "accepted", "admin_note": "Admin manual accepted state update."}
        )
        # Admin PUT & PATCH /admin/bookings/{id}/override-status
        self.run_case(
            "ADM_PUT_OVERRIDE", "POSITIVE", "PUT", f"/admin/bookings/{badm_id}/override-status",
            "Admin overrides status bypassing state machine (PUT)", "admin", [200],
            headers=admin["headers"],
            json_data={"status": "in_progress", "admin_note": "Bypass to in_progress."}
        )
        self.run_case(
            "ADM_PATCH_OVERRIDE", "POSITIVE", "PATCH", f"/admin/bookings/{badm_id}/override-status",
            "Admin overrides status bypassing state machine (PATCH)", "admin", [200],
            headers=admin["headers"],
            json_data={"status": "assigned", "admin_note": "Bypass back to assigned."}
        )
        # Admin POST /admin/bookings/{id}/force-cancel
        self.run_case(
            "ADM_FORCE_CANCEL", "POSITIVE", "POST", f"/admin/bookings/{badm_id}/force-cancel",
            "Admin force cancels booking", "admin", [200],
            headers=admin["headers"],
            json_data={"reason": "Customer requested cancellation via call center."}
        )

    def test_payments_suite(self):
        print("\n" + "="*80)
        print("PHASE 7: PAYMENTS, ORDERS, INVOICES & WEBHOOKS (/payments)")
        print("="*80)
        cust = self.context["customer"]
        admin = self.context["admin"]
        booking_id = self.context.get("booking_id", 1)

        resp_order = self.run_case(
            "PAY_CREATE_ORDER", "POSITIVE", "POST", "/payments/create-order",
            "Create Razorpay order for booking", "customer", [200],
            headers=cust["headers"],
            json_data={"booking_id": booking_id}
        )
        order_info = resp_order.json() if resp_order and resp_order.status_code == 200 else {}
        payment_id = order_info.get("payment_id", 1)
        order_id = order_info.get("id", f"order_test_{uuid.uuid4().hex[:8]}")
        self.context["payment_id"] = payment_id

        self.run_case(
            "PAY_LIST_CUST", "POSITIVE", "GET", "/payments/",
            "List payments for customer", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "PAY_LIST_ADMIN", "POSITIVE", "GET", "/payments/",
            "List all platform payments for admin", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "PAY_GET_ID", "POSITIVE", "GET", f"/payments/{payment_id}",
            "Get payment details by ID", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "PAY_HISTORY", "POSITIVE", "GET", "/payments/history",
            "Get user transaction history", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "PAY_VERIFY_INVALID_SIG", "VALIDATION_422_400", "POST", "/payments/verify",
            "Verify payment with forged signature (should fail)", "customer", [400],
            headers=cust["headers"],
            json_data={"razorpay_order_id": order_id, "razorpay_payment_id": f"pay_test_{uuid.uuid4().hex[:8]}", "razorpay_signature": "forged_signature"}
        )
        unique_pay_id = f"pay_live_cap_{uuid.uuid4().hex[:8]}"
        self.run_case(
            "PAY_WEBHOOK_HANDLER", "POSITIVE", "POST", "/payments/webhook",
            "Simulate Razorpay captured webhook event", "anonymous", [200],
            json_data={
                "event": "payment.captured",
                "payload": {
                    "payment": {
                        "entity": {
                            "id": unique_pay_id,
                            "order_id": order_id,
                            "status": "captured",
                            "amount": 64900,
                            "currency": "INR",
                            "method": "upi",
                        }
                    }
                }
            },
            code_changed="Used PaymentMethod.UNKNOWN in app/services/payment.py"
        )
        self.run_case(
            "PAY_GET_INVOICE", "POSITIVE", "GET", f"/payments/invoice/{payment_id}",
            "Get payment invoice breakdown", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "PAY_REFUND_ADMIN", "POSITIVE", "POST", f"/payments/{payment_id}/refund",
            "Admin initiates refund for payment ID", "admin", [200, 400],
            headers=admin["headers"]
        )

    def test_coupons_suite(self):
        print("\n" + "="*80)
        print("PHASE 8: COUPONS & DISCOUNT ENGINE (/coupons)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]
        booking_id = self.context.get("booking_id", 1)

        code = f"HOMIQ_{self.uid('cp').upper()}"
        today_date = datetime.date.today().isoformat()
        future_date = (datetime.date.today() + datetime.timedelta(days=30)).isoformat()
        resp_cp = self.run_case(
            "COUPON_CREATE", "POSITIVE", "POST", "/coupons/",
            "Create new discount coupon (Admin)", "admin", [201],
            headers=admin["headers"],
            json_data={
                "code": code,
                "discount_type": "percentage",
                "discount_value": 20.0,
                "max_discount_amount": 150.0,
                "min_order_amount": 299.0,
                "usage_limit_per_user": 2,
                "valid_from": today_date,
                "valid_until": future_date,
                "is_active": True,
            }
        )
        coupon_id = resp_cp.json()["id"] if resp_cp and resp_cp.status_code == 201 else 1
        self.context["coupon_id"] = coupon_id
        self.context["coupon_code"] = code

        self.run_case(
            "COUPON_LIST", "POSITIVE", "GET", "/coupons/",
            "List coupons (Admin)", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "COUPON_GET_ID", "POSITIVE", "GET", f"/coupons/{coupon_id}",
            "Get coupon by ID", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "COUPON_GET_CODE", "POSITIVE", "GET", f"/coupons/code/{code}",
            "Get coupon by promo code", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "COUPON_VALIDATE", "POSITIVE", "POST", "/coupons/validate",
            "Validate coupon code against order value", "customer", [200],
            headers=cust["headers"],
            json_data={"code": code, "amount": 649.0, "booking_id": booking_id}
        )
        self.run_case(
            "COUPON_APPLY", "POSITIVE", "POST", "/coupons/apply",
            "Apply coupon code to booking", "customer", [200],
            headers=cust["headers"],
            json_data={"code": code, "booking_id": booking_id, "amount": 649.0}
        )
        self.run_case(
            "COUPON_UPDATE", "POSITIVE", "PUT", f"/coupons/{coupon_id}",
            "Update coupon discount value", "admin", [200],
            headers=admin["headers"],
            json_data={"discount_value": 25.0}
        )
        self.run_case(
            "COUPON_DELETE", "POSITIVE", "DELETE", f"/coupons/{coupon_id}",
            "Delete coupon by ID", "admin", [200],
            headers=admin["headers"]
        )

    def test_invoices_suite(self):
        print("\n" + "="*80)
        print("PHASE 9: INVOICES & BILLING APIS (/invoices)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]
        svc_id = self.context.get("service_id", 1)
        addr_id = self.context.get("address_id", 1)

        resp_b2 = client.post("/bookings/", headers=cust["headers"], json={
            "service_id": svc_id, "address_id": addr_id, "booking_date": self.future_date(7),
            "preferred_time": "12:00:00", "estimated_price": 800.0,
        })
        b2_id = resp_b2.json()["id"] if resp_b2.status_code == 201 else self.context.get("booking_id", 1)

        self.run_case(
            "INVOICE_CREATE_FORBIDDEN", "ROLE_403", "POST", "/invoices/",
            "Customer role attempting invoice creation", "customer", [403],
            headers=cust["headers"],
            json_data={"booking_id": b2_id, "subtotal": 800.0, "total_amount": 944.0}
        )
        resp_inv = self.run_case(
            "INVOICE_CREATE", "POSITIVE", "POST", "/invoices/",
            "Create tax invoice for booking", "admin", [201],
            headers=admin["headers"],
            json_data={
                "booking_id": b2_id,
                "subtotal": 800.0,
                "discount_amount": 50.0,
                "tax_percentage": 18.0,
                "total_amount": 894.0,
                "amount_paid": 0.0,
                "notes": "Draft commercial invoice.",
            },
            code_changed="Made generate_invoice_number loop-safe against unique key collisions in app/crud/invoice.py"
        )
        inv_data = resp_inv.json() if resp_inv and resp_inv.status_code == 201 else {}
        inv_id = inv_data.get("id", 1)
        inv_num = inv_data.get("invoice_number", "INV-1")

        self.run_case(
            "INVOICE_LIST_CUST", "POSITIVE", "GET", "/invoices/",
            "List invoices for customer", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "INVOICE_LIST_ADMIN", "POSITIVE", "GET", "/invoices/",
            "List all invoices for admin", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "INVOICE_GET_ID", "POSITIVE", "GET", f"/invoices/{inv_id}",
            "Get invoice details by ID", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "INVOICE_GET_NUM", "POSITIVE", "GET", f"/invoices/number/{inv_num}",
            "Get invoice details by invoice number", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "INVOICE_UPDATE", "POSITIVE", "PUT", f"/invoices/{inv_id}",
            "Update invoice notes & payment status", "admin", [200],
            headers=admin["headers"],
            json_data={"notes": "Final approved invoice."}
        )
        self.run_case(
            "INVOICE_ISSUE", "POSITIVE", "POST", f"/invoices/{inv_id}/issue",
            "Transition invoice status to issued", "admin", [200],
            headers=admin["headers"]
        )

    def test_reviews_suite(self):
        print("\n" + "="*80)
        print("PHASE 10: REVIEWS & RATINGS APIS (/reviews)")
        print("="*80)
        cust = self.context["customer"]
        tech_db_id = self.context.get("technician_db_id", 1)
        booking_id = self.context.get("booking_id", 1)

        resp_rev = self.run_case(
            "REVIEW_CREATE", "POSITIVE", "POST", "/reviews/",
            "Create verified review for completed booking", "customer", [201],
            headers=cust["headers"],
            json_data={
                "booking_id": booking_id,
                "technician_id": tech_db_id,
                "rating": 5,
                "comment": "Outstanding technical expertise and very neat work!"
            }
        )
        rev_id = resp_rev.json()["id"] if resp_rev and resp_rev.status_code == 201 else 1

        self.run_case(
            "REVIEW_LIST_PUBLIC", "POSITIVE", "GET", "/reviews/",
            "List reviews publicly with pagination", "anonymous", [200]
        )
        self.run_case(
            "REVIEW_GET_ID", "POSITIVE", "GET", f"/reviews/{rev_id}",
            "Get review details by ID", "anonymous", [200]
        )
        self.run_case(
            "REVIEW_PATCH", "POSITIVE", "PATCH", f"/reviews/{rev_id}",
            "Patch review comment", "customer", [200],
            headers=cust["headers"],
            json_data={"comment": "Outstanding technical expertise, strongly recommended!"}
        )
        self.run_case(
            "REVIEW_PUT", "POSITIVE", "PUT", f"/reviews/{rev_id}",
            "Update rating and full review content", "customer", [200],
            headers=cust["headers"],
            json_data={"rating": 5, "comment": "Fully resolved my problem in under 1 hour."}
        )
        self.run_case(
            "REVIEW_TECH_LIST", "POSITIVE", "GET", f"/reviews/technician/{tech_db_id}",
            "Get all reviews for technician", "anonymous", [200]
        )
        self.run_case(
            "REVIEW_TECH_SUMMARY", "POSITIVE", "GET", f"/reviews/technician/{tech_db_id}/summary",
            "Get star rating distribution for technician", "anonymous", [200]
        )

    def test_notifications_suite(self):
        print("\n" + "="*80)
        print("PHASE 11: NOTIFICATIONS & MULTI-CHANNEL DISPATCH (/notifications)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]
        cust_user_id = cust["user_id"]

        resp_notif = self.run_case(
            "NOTIF_CREATE", "POSITIVE", "POST", "/notifications/",
            "Create user notification (Admin/System)", "admin", [201],
            headers=admin["headers"],
            json_data={"user_id": cust_user_id, "title": "Service Completed", "message": "Your booking has been completed.", "notification_type": "booking"}
        )
        notif_id = resp_notif.json()["id"] if resp_notif and resp_notif.status_code == 201 else 1

        self.run_case(
            "NOTIF_LIST", "POSITIVE", "GET", "/notifications/",
            "List user notifications", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_UNREAD", "POSITIVE", "GET", "/notifications/unread",
            "Get unread notifications and badge count", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_MARK_READ_PATCH", "POSITIVE", "PATCH", f"/notifications/{notif_id}/read",
            "Mark single notification read via PATCH", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_MARK_READ_PUT", "POSITIVE", "PUT", f"/notifications/{notif_id}/read",
            "Mark single notification read via PUT", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_READ_MULTIPLE", "POSITIVE", "POST", "/notifications/read-multiple",
            "Mark list of notification IDs as read", "customer", [200],
            headers=cust["headers"],
            json_data={"notification_ids": [notif_id]}
        )
        self.run_case(
            "NOTIF_READ_ALL_PUT", "POSITIVE", "PUT", "/notifications/read-all",
            "Mark all user notifications as read via PUT", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_READ_ALL_PATCH", "POSITIVE", "PATCH", "/notifications/read-all",
            "Mark all user notifications as read via PATCH", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "NOTIF_DISPATCH_MULTI", "POSITIVE", "POST", "/notifications/dispatch",
            "Dispatch multi-channel (In-App, Email, SMS, Push)", "admin", [200],
            headers=admin["headers"],
            json_data={
                "user_id": cust_user_id,
                "title": "Payment Received",
                "message": "Thank you for your payment.",
                "channels": ["in_app", "email"],
            }
        )
        self.run_case(
            "NOTIF_DELETE", "POSITIVE", "DELETE", f"/notifications/{notif_id}",
            "Delete single notification by ID", "customer", [200],
            headers=cust["headers"]
        )

    def test_maps_suite(self):
        print("\n" + "="*80)
        print("PHASE 12: MAPS, GEOCODING & DISTANCE MATRIX APIS (/maps)")
        print("="*80)
        cust = self.context["customer"]

        self.run_case(
            "MAPS_GEOCODE", "POSITIVE", "GET", "/maps/geocode?address=Indiranagar%2C%20Bengaluru",
            "Geocode street address to lat/lng coordinates", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "MAPS_REV_GEOCODE", "POSITIVE", "GET", "/maps/reverse-geocode?latitude=12.9716&longitude=77.5946",
            "Reverse geocode coordinates to human-readable address", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "MAPS_ETA", "POSITIVE", "GET", "/maps/eta?origin_lat=12.9716&origin_lng=77.5946&dest_lat=12.9800&dest_lng=77.6000",
            "Calculate driving distance & ETA between coordinates", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "MAPS_NEARBY_TECHS", "POSITIVE", "GET", "/maps/nearby-technicians?latitude=12.9716&longitude=77.5946&radius_km=30",
            "Find online technicians in proximity", "customer", [200],
            headers=cust["headers"]
        )

    def test_jobs_suite(self):
        print("\n" + "="*80)
        print("PHASE 13: JOBS & RECRUITMENT APIS (/jobs)")
        print("="*80)
        comp = self.context["company"]
        tech = self.context["technician"]
        cust = self.context["customer"]

        resp_job = self.run_case(
            "JOB_CREATE", "POSITIVE", "POST", "/jobs/",
            "Company creates hiring job posting", "company", [201],
            headers=comp["headers"],
            json_data={
                "title": "Lead HVAC Specialist",
                "description": "Full-time residential maintenance technician needed.",
                "requirements": "3+ years field experience, own transport, clean background.",
                "is_active": True,
            }
        )
        job_id = resp_job.json()["id"] if resp_job and resp_job.status_code == 201 else 1

        self.run_case(
            "JOB_CREATE_FORBIDDEN", "ROLE_403", "POST", "/jobs/",
            "Customer role attempting job creation", "customer", [403],
            headers=cust["headers"],
            json_data={"title": "Unauthorized Job"}
        )
        self.run_case(
            "JOB_LIST_ACTIVE", "POSITIVE", "GET", "/jobs/",
            "Technicians list available open jobs", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "JOB_LIST_MY_COMP", "POSITIVE", "GET", "/jobs/my",
            "Company lists their own job postings", "company", [200],
            headers=comp["headers"]
        )
        self.run_case(
            "JOB_GET_ID", "POSITIVE", "GET", f"/jobs/{job_id}",
            "Get job posting details by ID", "technician", [200],
            headers=tech["headers"]
        )
        resp_app = self.run_case(
            "JOB_APPLY", "POSITIVE", "POST", f"/jobs/{job_id}/apply",
            "Technician submits application for job post", "technician", [201],
            headers=tech["headers"],
            json_data={"cover_letter": "I have 5+ years of verified HVAC experience in Bengaluru."}
        )
        app_id = resp_app.json()["id"] if resp_app and resp_app.status_code == 201 else 1

        self.run_case(
            "JOB_APPLY_DUPLICATE", "VALIDATION_422_400", "POST", f"/jobs/{job_id}/apply",
            "Technician duplicate application on same job", "technician", [400],
            headers=tech["headers"],
            json_data={"cover_letter": "Duplicate"}
        )
        self.run_case(
            "JOB_LIST_APPLICANTS", "POSITIVE", "GET", f"/jobs/{job_id}/applications",
            "Company reviews candidate applications", "company", [200],
            headers=comp["headers"]
        )
        self.run_case(
            "JOB_UPDATE_APP_STATUS", "POSITIVE", "PUT", f"/jobs/applications/{app_id}/status",
            "Company shortlists candidate application", "company", [200],
            headers=comp["headers"],
            json_data={"status": "shortlisted"}
        )
        self.run_case(
            "JOB_TECH_MY_APPS", "POSITIVE", "GET", "/jobs/applications/my",
            "Technician views submitted applications", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "JOB_UPDATE", "POSITIVE", "PUT", f"/jobs/{job_id}",
            "Company updates job post details", "company", [200],
            headers=comp["headers"],
            json_data={"title": "Senior Lead HVAC Specialist", "is_active": True}
        )

    def test_media_suite(self):
        print("\n" + "="*80)
        print("PHASE 14: MEDIA & CLOUDINARY FILE ASSETS (/media)")
        print("="*80)
        cust = self.context["customer"]

        fake_img = io.BytesIO(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4")
        resp_media = self.run_case(
            "MEDIA_UPLOAD", "POSITIVE", "POST", "/media/upload",
            "Upload image file to Cloudinary media store", "customer", [201],
            headers=cust["headers"],
            data={"folder": "homiq/audits"},
            files={"file": ("audit_asset.png", fake_img, "image/png")}
        )
        pub_id = resp_media.json().get("public_id", "homiq/audits/sample") if resp_media and resp_media.status_code == 201 else "homiq/audits/sample"

        self.run_case(
            "MEDIA_GET_DETAILS", "POSITIVE", "GET", f"/media/{pub_id}",
            "Get Cloudinary optimized URLs and thumbnail", "anonymous", [200]
        )
        self.run_case(
            "MEDIA_DELETE", "POSITIVE", "DELETE", f"/media/{pub_id}",
            "Delete media asset from Cloudinary", "customer", [200],
            headers=cust["headers"]
        )

    def test_reports_and_analytics_suite(self):
        print("\n" + "="*80)
        print("PHASE 15: REPORTS & ANALYTICS APIS (/reports, /analytics)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]
        tech = self.context["technician"]

        self.run_case(
            "ANALYTICS_ADMIN", "POSITIVE", "GET", "/analytics/admin",
            "Get full platform analytics suite", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ANALYTICS_CUST", "POSITIVE", "GET", "/analytics/customer",
            "Get customer personal booking and spend analytics", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "ANALYTICS_TECH", "POSITIVE", "GET", "/analytics/technician",
            "Get technician personal earnings & completion metrics", "technician", [200],
            headers=tech["headers"]
        )
        self.run_case(
            "REPORT_DAILY", "POSITIVE", "GET", "/reports/daily",
            "Get daily business report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "REPORT_WEEKLY", "POSITIVE", "GET", "/reports/weekly",
            "Get weekly business report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "REPORT_MONTHLY", "POSITIVE", "GET", "/reports/monthly",
            "Get monthly business report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "REPORT_YEARLY", "POSITIVE", "GET", "/reports/yearly",
            "Get yearly business report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "REPORT_EXPORT_CSV", "POSITIVE", "GET", "/reports/export?format=csv&period=monthly",
            "Export financial/booking reports as CSV", "admin", [200],
            headers=admin["headers"]
        )

    def test_search_and_recommendations_suite(self):
        print("\n" + "="*80)
        print("PHASE 16: SEARCH, AUTOCOMPLETE & RECOMMENDATION ENGINE (/search, /recommendations)")
        print("="*80)
        cust = self.context["customer"]

        self.run_case(
            "SEARCH_GLOBAL", "POSITIVE", "GET", "/search?q=cleaning&limit=10",
            "Global unified platform search", "anonymous", [200]
        )
        self.run_case(
            "SEARCH_SERVICES", "POSITIVE", "GET", "/search/services?q=AC&sort_by=popular",
            "Search service catalog with filters", "anonymous", [200]
        )
        self.run_case(
            "SEARCH_TECHS", "POSITIVE", "GET", "/search/technicians?city=Bengaluru&sort_by=rating_desc",
            "Search technicians by city and rating", "anonymous", [200]
        )
        self.run_case(
            "SEARCH_BOOKINGS", "POSITIVE", "GET", "/search/bookings",
            "Search user bookings by keyword/status", "customer", [200],
            headers=cust["headers"],
            code_changed="Fixed total_amount in search_bookings in app/services/search.py"
        )
        self.run_case(
            "SEARCH_SUGGESTIONS", "POSITIVE", "GET", "/search/suggestions?q=cle",
            "Live autocomplete prefix search", "anonymous", [200]
        )
        self.run_case(
            "SEARCH_RECENT", "POSITIVE", "GET", "/search/recent",
            "Get recent user search history", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "RECOM_UNIFIED", "POSITIVE", "GET", "/recommendations",
            "Get AI/heuristic unified recommendations", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "RECOM_SERVICES", "POSITIVE", "GET", "/recommendations/services",
            "Get trending & popular service recommendations", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "RECOM_TECHS", "POSITIVE", "GET", "/recommendations/technicians",
            "Get top-rated technician recommendations", "customer", [200],
            headers=cust["headers"]
        )

    def test_security_and_sessions_suite(self):
        print("\n" + "="*80)
        print("PHASE 17: SECURITY, ACTIVE SESSIONS & AUDIT LOGS (/security)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]

        self.run_case(
            "SEC_SESSIONS_GET", "POSITIVE", "GET", "/security/sessions",
            "List active user device sessions", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "SEC_LOGOUT_ALL", "POSITIVE", "DELETE", "/security/logout-all",
            "Revoke all active device sessions", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "SEC_AUDIT_LOGS", "POSITIVE", "GET", "/security/audit-logs?limit=25",
            "Query security and login audit trail", "admin", [200],
            headers=admin["headers"]
        )

    def test_tasks_and_scheduler_suite(self):
        print("\n" + "="*80)
        print("PHASE 18: BACKGROUND TASKS & CELERY SCHEDULER (/tasks, /scheduler)")
        print("="*80)
        admin = self.context["admin"]

        self.run_case(
            "TASK_GET_STATUS", "POSITIVE", "GET", "/tasks/status/mock_audit_task_id",
            "Get async background task execution status", "admin", [200],
            headers=admin["headers"],
            code_changed="Safeguarded Celery AsyncResult fallback in app/api/tasks/router.py"
        )
        self.run_case(
            "TASK_RETRY", "POSITIVE", "POST", "/tasks/retry/mock_audit_task_id",
            "Re-queue or retry background task", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "TASK_SCHEDULER_JOBS", "POSITIVE", "GET", "/scheduler/jobs",
            "List active Celery Beat cron tasks", "admin", [200],
            headers=admin["headers"]
        )

    def test_monitoring_and_health_suite(self):
        print("\n" + "="*80)
        print("PHASE 19: MONITORING, PROMETHEUS & HEALTH APIS (/health, /metrics, /dashboard)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]

        self.run_case(
            "HEALTH_BASIC", "POSITIVE", "GET", "/health",
            "Basic liveness probe", "anonymous", [200]
        )
        self.run_case(
            "HEALTH_DETAIL", "POSITIVE", "GET", "/health/detail",
            "Database, Redis, and WebSocket connectivity health check", "anonymous", [200, 503]
        )
        self.run_case(
            "METRICS_PROMETHEUS", "POSITIVE", "GET", "/metrics",
            "Prometheus text format metrics export", "anonymous", [200]
        )
        self.run_case(
            "DASHBOARD_ROOT_CUST", "POSITIVE", "GET", "/dashboard",
            "Role-aware root dashboard (Customer view)", "customer", [200],
            headers=cust["headers"]
        )
        self.run_case(
            "DASHBOARD_ROOT_ADMIN", "POSITIVE", "GET", "/dashboard",
            "Role-aware root dashboard (Admin view)", "admin", [200],
            headers=admin["headers"]
        )

    def test_admin_control_suite(self):
        print("\n" + "="*80)
        print("PHASE 20: ADMIN PANEL FULL MANAGEMENT & CONTROL (/admin/*)")
        print("="*80)
        admin = self.context["admin"]
        cust = self.context["customer"]
        tech = self.context["technician"]
        booking_id = self.context.get("booking_id", 1)
        tech_db_id = self.context.get("technician_db_id", 1)
        doc_id = self.context.get("tech_doc_id", 1)
        cat_id = self.context.get("category_id", 1)
        svc_id = self.context.get("service_id", 1)
        cp_id = self.context.get("coupon_id", 1)

        self.run_case(
            "ADM_DASHBOARD", "POSITIVE", "GET", "/admin/dashboard",
            "Admin control center summary statistics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_USER_LIST", "POSITIVE", "GET", "/admin/users",
            "List all platform users with role filters", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_USER_GET", "POSITIVE", "GET", f"/admin/users/{cust['user_id']}",
            "Get deep user profile and booking history", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_USER_SUSPEND", "POSITIVE", "PATCH", f"/admin/users/{cust['user_id']}/suspend",
            "Admin temporarily suspends customer account", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_USER_ACTIVATE", "POSITIVE", "PATCH", f"/admin/users/{cust['user_id']}/activate",
            "Admin reactivates customer account", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_TECH_LIST", "POSITIVE", "GET", "/admin/technicians",
            "List technicians for administrative management", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_TECH_DOCS", "POSITIVE", "GET", f"/admin/technicians/{tech_db_id}/documents",
            "List verification documents for technician", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_DOC_APPROVE", "POSITIVE", "PATCH", f"/admin/documents/{doc_id}/approve",
            "Admin approves technician document", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_TECH_APPROVE", "POSITIVE", "PATCH", f"/admin/technicians/{tech_db_id}/approve",
            "Admin verifies and approves technician profile", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_TECH_SUSPEND", "POSITIVE", "PATCH", f"/admin/technicians/{tech_db_id}/suspend",
            "Admin sets technician availability to false", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_TECH_ACTIVATE", "POSITIVE", "PATCH", f"/admin/technicians/{tech_db_id}/activate",
            "Admin sets technician availability to true", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_BOOKING_LIST", "POSITIVE", "GET", "/admin/bookings",
            "List all bookings with status filters", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_BOOKING_GET", "POSITIVE", "GET", f"/admin/bookings/{booking_id}",
            "Get booking details (Admin override)", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_BOOKING_LOGS", "POSITIVE", "GET", f"/admin/bookings/{booking_id}/logs",
            "Get booking lifecycle audit log entries", "admin", [200],
            headers=admin["headers"],
            code_changed="Added get_booking_history_logs to BookingService in app/services/booking.py"
        )
        self.run_case(
            "ADM_CAT_LIST", "POSITIVE", "GET", "/admin/categories",
            "Admin category management listing", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_CAT_DISABLE", "POSITIVE", "PATCH", f"/admin/categories/{cat_id}/disable",
            "Admin disables category", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_CAT_ENABLE", "POSITIVE", "PATCH", f"/admin/categories/{cat_id}/enable",
            "Admin enables category", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_SVC_DISABLE", "POSITIVE", "PATCH", f"/admin/services/{svc_id}/disable",
            "Admin disables service", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_SVC_ENABLE", "POSITIVE", "PATCH", f"/admin/services/{svc_id}/enable",
            "Admin enables service", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_COUPON_LIST", "POSITIVE", "GET", "/admin/coupons",
            "Admin coupon management listing", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_INVOICE_LIST", "POSITIVE", "GET", "/admin/invoices",
            "Admin invoice management listing", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_REVIEW_LIST", "POSITIVE", "GET", "/admin/reviews",
            "Admin review moderation listing", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_REP_OVERVIEW", "POSITIVE", "GET", "/admin/reports",
            "Admin report overview summary", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_REP_REV", "POSITIVE", "GET", "/admin/reports/revenue",
            "Admin revenue report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_REP_BOOK", "POSITIVE", "GET", "/admin/reports/bookings",
            "Admin bookings report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_REP_TECH", "POSITIVE", "GET", "/admin/reports/technicians",
            "Admin technician report", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_OVERVIEW", "POSITIVE", "GET", "/admin/analytics/overview",
            "Admin analytics overview metrics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_GROWTH", "POSITIVE", "GET", "/admin/analytics/growth",
            "Admin platform growth metrics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_CUST", "POSITIVE", "GET", "/admin/analytics/customers",
            "Admin customer analytics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_BOOK", "POSITIVE", "GET", "/admin/analytics/bookings",
            "Admin booking analytics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_SVC", "POSITIVE", "GET", "/admin/analytics/service",
            "Admin service analytics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_TECH", "POSITIVE", "GET", "/admin/analytics/technician",
            "Admin technician analytics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_ANALYTICS_REV", "POSITIVE", "GET", "/admin/analytics/revenue",
            "Admin revenue analytics", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_SETTINGS_GET", "POSITIVE", "GET", "/admin/settings",
            "Get global platform business settings", "admin", [200],
            headers=admin["headers"]
        )
        self.run_case(
            "ADM_SETTINGS_PUT", "POSITIVE", "PUT", "/admin/settings",
            "Update platform commission and tax settings", "admin", [200],
            headers=admin["headers"],
            json_data={"commission_percentage": 15.0, "tax_percentage": 18.0}
        )

    def test_websocket_chat_suite(self):
        print("\n" + "="*80)
        print("PHASE 21: WEBSOCKET & CHAT HISTORY (/chat, /ws)")
        print("="*80)
        cust = self.context["customer"]
        booking_id = self.context.get("booking_id", 1)

        self.run_case(
            "CHAT_HISTORY_GET", "POSITIVE", "GET", f"/chat/{booking_id}/history",
            "Get stored chat conversation history for booking", "customer", [200],
            headers=cust["headers"]
        )

    def generate_report(self):
        elapsed = time.time() - self.start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = sum(1 for r in self.results if not r.passed)
        pass_rate = round((passed_tests / total_tests) * 100, 2) if total_tests > 0 else 0.0

        category_counts: Dict[str, Dict[str, int]] = {}
        for r in self.results:
            if r.category not in category_counts:
                category_counts[r.category] = {"total": 0, "passed": 0, "failed": 0}
            category_counts[r.category]["total"] += 1
            if r.passed:
                category_counts[r.category]["passed"] += 1
            else:
                category_counts[r.category]["failed"] += 1

        print("\n" + "="*80)
        print("HOMIQ BACKEND - FULL-SPECTRUM MASTER TEST REPORT")
        print("="*80)
        print(f"Total Test Cases Executed: {total_tests}")
        print(f"Passed:                    {passed_tests}")
        print(f"Failed:                    {failed_tests}")
        print(f"Pass Rate:                 {pass_rate}%")
        print(f"Total Duration:            {elapsed:.2f}s")
        print("-" * 80)
        print("BREAKDOWN BY TEST CATEGORY:")
        for cat, counts in sorted(category_counts.items()):
            p_rate = round((counts["passed"] / counts["total"]) * 100, 1) if counts["total"] else 0
            print(f"  - {cat:<24} | Total: {counts['total']:>3} | Passed: {counts['passed']:>3} | Failed: {counts['failed']:>2} ({p_rate}%)")
        print("="*80)

        report_data = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "pass_rate_percent": pass_rate,
                "duration_seconds": round(elapsed, 2),
                "timestamp": datetime.datetime.now().isoformat(),
            },
            "category_breakdown": category_counts,
            "results": [asdict(r) for r in self.results],
        }

        report_json_path = os.path.join(BASE_DIR, "full_spectrum_test_report.json")
        with open(report_json_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2)
        print(f"\n[+] Saved JSON Full-Spectrum Test Report to: {report_json_path}")

        return report_data

    def run_all(self) -> int:
        self.setup_actors()
        self.test_auth_suite()
        self.test_customer_suite()
        self.test_technician_suite()
        self.test_company_suite()
        self.test_services_suite()
        self.test_bookings_and_lifecycle_suite()
        self.test_payments_suite()
        self.test_coupons_suite()
        self.test_invoices_suite()
        self.test_reviews_suite()
        self.test_notifications_suite()
        self.test_maps_suite()
        self.test_jobs_suite()
        self.test_media_suite()
        self.test_reports_and_analytics_suite()
        self.test_search_and_recommendations_suite()
        self.test_security_and_sessions_suite()
        self.test_tasks_and_scheduler_suite()
        self.test_monitoring_and_health_suite()
        self.test_admin_control_suite()
        self.test_websocket_chat_suite()

        report = self.generate_report()
        return 0 if report["summary"]["failed"] == 0 else 1


if __name__ == "__main__":
    runner = FullSpectrumAPITester()
    sys.exit(runner.run_all())
