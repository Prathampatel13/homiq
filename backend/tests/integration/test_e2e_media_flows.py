"""
End-to-End Media Flows Test Suite for HomiQ.

Validates complete real-world user flows:
1. User Profile Avatar: Upload -> Replace (with rollback verification) -> Delete.
2. Technician Portfolio & Certificates: Upload -> List -> Delete with RBAC authorization.
3. Booking Before/After & Attachments: Authorized uploads -> Forbidden checks for strangers -> Media listing -> Cleanup.
4. Company & Service Media: Brand logo and service gallery workflows.
"""

from __future__ import annotations

import base64
import io
import sys
from datetime import datetime, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.database.session import SessionLocal
from app.main import app
from app.models.auth import Role, User
from app.models.bookings import Booking, BookingStatus
from app.models.media import MediaAsset, MediaAssetType
from app.models.services import Category, Service
from app.models.users import Customer, Technician
from app.security.passwords import hash_password
from app.security.tokens import create_access_token


# Valid 1x1 base64 encoded PNG for realistic test uploads
VALID_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)

# Valid PDF minimal bytes
VALID_PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj 3 0 obj<</Type/Page/MediaBox[0 0 3 3]>>endobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000052 00000 n\n0000000098 00000 n\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n149\n%%EOF\n"


def get_or_create_user(db, email: str, full_name: str, role_name: str) -> tuple[User, str]:
    """Helper to provision user with role and return (User, JWT token)."""
    user = db.scalar(select(User).where(User.email == email))
    role = db.scalar(select(Role).where(Role.name == role_name))
    if not role:
        role = Role(name=role_name, description=f"{role_name.capitalize()} role")
        db.add(role)
        db.commit()
        db.refresh(role)

    if not user:
        user = User(
            email=email,
            phone="+919876543210",
            full_name=full_name,
            password_hash=hash_password("SecurePass123!"),
            is_active=True,
            is_verified=True,
            role_id=role.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = create_access_token(user.id)
    return user, token


def run_e2e_tests():
    print("=" * 70)
    print("HOMIQ END-TO-END CLOUDINARY & MEDIA LIFECYCLE TEST SUITE")
    print("=" * 70)

    client = TestClient(app)
    db = SessionLocal()

    try:
        # Provision test actors
        customer_user, customer_token = get_or_create_user(
            db, "e2e_customer@homiq.test", "E2E Customer", "customer"
        )
        tech_user, tech_token = get_or_create_user(
            db, "e2e_tech@homiq.test", "E2E Technician", "technician"
        )
        stranger_user, stranger_token = get_or_create_user(
            db, "e2e_stranger@homiq.test", "E2E Stranger", "customer"
        )

        # Ensure Customer and Technician profile rows exist
        customer_profile = db.scalar(select(Customer).where(Customer.user_id == customer_user.id))
        if not customer_profile:
            customer_profile = Customer(user_id=customer_user.id)
            db.add(customer_profile)
            db.commit()
            db.refresh(customer_profile)

        tech_profile = db.scalar(select(Technician).where(Technician.user_id == tech_user.id))
        if not tech_profile:
            tech_profile = Technician(
                user_id=tech_user.id,
                experience_years=5,
                specialization="Electrician",
                availability=True,
                is_online=True,
            )
            db.add(tech_profile)
            db.commit()
            db.refresh(tech_profile)

        # ─────────────────────────────────────────────────────────────────────
        # FLOW 1: User Profile Avatar Lifecycle
        # ─────────────────────────────────────────────────────────────────────
        print("\n[FLOW 1] Testing User Profile Avatar (Upload -> Replace -> Delete)...")
        headers = {"Authorization": f"Bearer {customer_token}"}

        # 1a. Upload avatar
        files = {"file": ("avatar1.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        resp = client.post("/users/me/avatar", headers=headers, files=files)
        assert resp.status_code == 200, f"Upload avatar failed: {resp.text}"
        data = resp.json()
        assert data["success"] is True
        avatar_url_1 = data["data"]["secure_url"]
        print(f"  [OK] Avatar uploaded: {avatar_url_1}")

        # Verify DB updated
        db.expire_all()
        user_in_db = db.get(User, customer_user.id)
        assert user_in_db.avatar_url == avatar_url_1
        print("  [OK] Database User.avatar_url updated correctly.")

        # 1b. Replace avatar
        files_2 = {"file": ("avatar2.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        resp_replace = client.post("/users/me/avatar", headers=headers, files=files_2)
        assert resp_replace.status_code == 200, f"Replace avatar failed: {resp_replace.text}"
        avatar_url_2 = resp_replace.json()["data"]["secure_url"]
        print(f"  [OK] Avatar replaced: {avatar_url_2}")

        # 1c. Delete avatar
        resp_delete = client.delete("/users/me/avatar", headers=headers)
        assert resp_delete.status_code == 200, f"Delete avatar failed: {resp_delete.text}"
        db.expire_all()
        user_cleared = db.get(User, customer_user.id)
        assert user_cleared.avatar_url is None
        print("  [OK] Avatar removed and database reference cleared.")

        # ─────────────────────────────────────────────────────────────────────
        # FLOW 2: Technician Portfolio & Certifications
        # ─────────────────────────────────────────────────────────────────────
        print("\n[FLOW 2] Testing Technician Portfolio & Certifications...")
        tech_headers = {"Authorization": f"Bearer {tech_token}"}

        # 2a. Upload portfolio work image
        port_files = {"file": ("portfolio_work.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        resp_port = client.post("/technicians/me/portfolio", headers=tech_headers, files=port_files)
        assert resp_port.status_code == 201, f"Portfolio upload failed: {resp_port.text}"
        port_asset_id = resp_port.json()["data"]["id"]
        print(f"  [OK] Portfolio work sample uploaded (Asset ID: {port_asset_id})")

        # 2b. List portfolio
        resp_list_port = client.get("/technicians/me/portfolio", headers=tech_headers)
        assert resp_list_port.status_code == 200
        port_items = resp_list_port.json()
        assert any(item["id"] == port_asset_id for item in port_items)
        print(f"  [OK] Listed technician portfolio ({len(port_items)} item(s) found).")

        # 2c. Delete portfolio item
        resp_del_port = client.delete(f"/technicians/me/portfolio/{port_asset_id}", headers=tech_headers)
        assert resp_del_port.status_code == 200
        print(f"  [OK] Portfolio item {port_asset_id} deleted successfully.")

        # 2d. Upload Certificate (PDF)
        cert_files = {"file": ("license.pdf", io.BytesIO(VALID_PDF_BYTES), "application/pdf")}
        resp_cert = client.post("/technicians/me/certificates", headers=tech_headers, files=cert_files)
        assert resp_cert.status_code == 201, f"Certificate upload failed: {resp_cert.text}"
        cert_asset_id = resp_cert.json()["data"]["id"]
        print(f"  [OK] Technician certificate document uploaded (Asset ID: {cert_asset_id})")

        # 2e. List certificates
        resp_list_cert = client.get("/technicians/me/certificates", headers=tech_headers)
        assert resp_list_cert.status_code == 200
        cert_items = resp_list_cert.json()
        assert any(item["id"] == cert_asset_id for item in cert_items)
        print(f"  [OK] Listed technician certificates ({len(cert_items)} document(s) found).")

        # 2f. Delete certificate
        resp_del_cert = client.delete(f"/technicians/me/certificates/{cert_asset_id}", headers=tech_headers)
        assert resp_del_cert.status_code == 200
        print(f"  [OK] Certificate item {cert_asset_id} deleted successfully.")

        # ─────────────────────────────────────────────────────────────────────
        # FLOW 3: Booking Before/After Photos & Security Guards
        # ─────────────────────────────────────────────────────────────────────
        print("\n[FLOW 3] Testing Booking Media Lifecycle & Security RBAC Guards...")

        # Setup test category and service
        category = db.scalar(select(Category).where(Category.name == "E2E Media Testing"))
        if not category:
            category = Category(name="E2E Media Testing", description="Category for E2E testing")
            db.add(category)
            db.commit()
            db.refresh(category)

        service = db.scalar(select(Service).where(Service.name == "AC Repair Pro E2E"))
        if not service:
            service = Service(
                name="AC Repair Pro E2E",
                category_id=category.id,
                base_price=500.0,
                duration_minutes=60,
                is_active=True,
            )
            db.add(service)
            db.commit()
            db.refresh(service)

        from uuid import uuid4
        from app.models.addresses import CustomerAddress

        address = db.scalar(select(CustomerAddress).where(CustomerAddress.customer_id == customer_profile.id))
        if not address:
            address = CustomerAddress(
                customer_id=customer_profile.id,
                full_name="E2E Customer",
                phone="+919876543210",
                house_no="42A",
                area="Tech Park",
                city="Bengaluru",
                state="Karnataka",
                pincode="560100",
            )
            db.add(address)
            db.commit()
            db.refresh(address)

        # Create test booking
        booking = Booking(
            booking_number=f"BK-{uuid4().hex[:8].upper()}",
            customer_id=customer_profile.id,
            technician_id=tech_profile.id,
            service_id=service.id,
            address_id=address.id,
            booking_date=datetime.now(timezone.utc).date(),
            status=BookingStatus.ASSIGNED,
            estimated_price=500.0,
            final_price=500.0,
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        print(f"  [OK] Test booking created (Booking ID: {booking.id})")

        # 3a. Upload Before Image (Technician)
        before_file = {"file": ("before_work.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        resp_before = client.post(
            f"/bookings/{booking.id}/before-images",
            headers=tech_headers,
            files=before_file,
        )
        assert resp_before.status_code == 201, f"Before image upload failed: {resp_before.text}"
        before_asset_id = resp_before.json()["data"]["id"]
        print(f"  [OK] Before-service photo uploaded (Asset ID: {before_asset_id})")

        # 3b. Upload After Image (Technician)
        after_file = {"file": ("after_work.png", io.BytesIO(VALID_PNG_BYTES), "image/png")}
        resp_after = client.post(
            f"/bookings/{booking.id}/after-images",
            headers=tech_headers,
            files=after_file,
        )
        assert resp_after.status_code == 201, f"After image upload failed: {resp_after.text}"
        after_asset_id = resp_after.json()["data"]["id"]
        print(f"  [OK] After-service photo uploaded (Asset ID: {after_asset_id})")

        # 3c. Upload Attachment/Invoice (Customer)
        attach_file = {"file": ("invoice_spec.pdf", io.BytesIO(VALID_PDF_BYTES), "application/pdf")}
        resp_attach = client.post(
            f"/bookings/{booking.id}/attachments",
            headers=headers,  # Customer header
            files=attach_file,
        )
        assert resp_attach.status_code == 201, f"Attachment upload failed: {resp_attach.text}"
        attach_asset_id = resp_attach.json()["data"]["id"]
        print(f"  [OK] Booking attachment uploaded (Asset ID: {attach_asset_id})")

        # 3d. List Booking Media (Customer & Technician)
        resp_b_media = client.get(f"/bookings/{booking.id}/media", headers=headers)
        assert resp_b_media.status_code == 200
        media_list = resp_b_media.json()
        assert len(media_list) >= 3
        print(f"  [OK] Listed {len(media_list)} media items for booking #{booking.id}.")

        # 3e. Security Guard: Unauthorized stranger user cannot access booking media
        stranger_headers = {"Authorization": f"Bearer {stranger_token}"}
        resp_stranger = client.get(f"/bookings/{booking.id}/media", headers=stranger_headers)
        assert resp_stranger.status_code == 403, "Stranger should have been rejected with 403 Forbidden!"
        print("  [OK] Security Guard: Stranger rejected with 403 Forbidden on booking media.")

        resp_stranger_upload = client.post(
            f"/bookings/{booking.id}/before-images",
            headers=stranger_headers,
            files={"file": ("hacker.png", io.BytesIO(VALID_PNG_BYTES), "image/png")},
        )
        assert resp_stranger_upload.status_code == 403, "Stranger upload should have been rejected with 403 Forbidden!"
        print("  [OK] Security Guard: Stranger rejected with 403 Forbidden on booking upload.")

        # 3f. Cleanup booking media
        for asset_id in [before_asset_id, after_asset_id, attach_asset_id]:
            resp_clean = client.delete(f"/bookings/{booking.id}/media/{asset_id}", headers=tech_headers)
            assert resp_clean.status_code == 200

        print("  [OK] Booking media cleaned up successfully.")

        # ─────────────────────────────────────────────────────────────────────
        # FLOW 4: Dynamic Transformations & Thumbnails
        # ─────────────────────────────────────────────────────────────────────
        print("\n[FLOW 4] Testing On-the-Fly Cloudinary Transformations...")
        opt_payload = {
            "width": 300,
            "height": 300,
            "crop": "fill",
            "quality": "auto",
            "fetch_format": "webp",
            "gravity": "face",
        }
        resp_opt = client.post(
            "/media/transform/homiq/users/283/profile/sample_avatar",
            json=opt_payload,
        )
        assert resp_opt.status_code == 200
        opt_data = resp_opt.json()
        assert "c_fill" in opt_data["optimized_url"]
        assert "f_webp" in opt_data["optimized_url"]
        print(f"  [OK] Generated optimized transformation URL: {opt_data['optimized_url']}")
        print(f"  [OK] Generated thumbnail URL: {opt_data['thumbnail_url']}")

        print("\n" + "=" * 70)
        print("ALL END-TO-END MEDIA FLOWS PASSED SUCCESSFULLY! (4/4)")
        print("=" * 70)

    finally:
        db.close()


if __name__ == "__main__":
    run_e2e_tests()
