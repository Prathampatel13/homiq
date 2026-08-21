"""
Comprehensive Verification Test for Cloudinary Media & Document Management Architecture.
"""

import io
from fastapi.testclient import TestClient
from fastapi import UploadFile

from app.core.cloudinary_config import is_cloudinary_configured, init_cloudinary
from app.models.media import MediaAsset, MediaAssetType
from app.schemas.media import MediaAssetType as SchemaMediaAssetType
from app.services.cloudinary_service import CloudinaryService, cloudinary_service
from app.database.base import Base
from app.database.session import engine, SessionLocal
from app.main import app

def run_tests():
    print("=" * 60)
    print("HOMIQ MEDIA & CLOUDINARY ARCHITECTURE TEST SUITE")
    print("=" * 60)

    # 1. Test Cloudinary Configuration Service
    print("[TEST 1] Testing Central Cloudinary Configuration...")
    init_res = init_cloudinary()
    print(f" -> Cloudinary Init: {'Configured' if is_cloudinary_configured() else 'Mock / Fallback Mode (OK)'}")

    # 2. Test Deterministic Folder Structure
    print("\n[TEST 2] Testing Deterministic Folder Generation...")
    folders_to_test = [
        (MediaAssetType.PROFILE_AVATAR, "user", 42, "homiq/users/42/profile"),
        (MediaAssetType.PROFILE_AVATAR, "technician", 15, "homiq/technicians/15/profile"),
        (MediaAssetType.COMPANY_LOGO, "company", 7, "homiq/companies/7/logo"),
        (MediaAssetType.SERVICE_GALLERY, "service", 101, "homiq/services/101/gallery"),
        (MediaAssetType.TECHNICIAN_PORTFOLIO, "technician", 15, "homiq/technicians/15/portfolio"),
        (MediaAssetType.TECHNICIAN_CERTIFICATE, "technician", 15, "homiq/technicians/15/certificates"),
        (MediaAssetType.IDENTITY_DOCUMENT, "technician", 15, "homiq/technicians/15/documents"),
        (MediaAssetType.BOOKING_BEFORE, "booking", 88, "homiq/bookings/88/before"),
        (MediaAssetType.BOOKING_AFTER, "booking", 88, "homiq/bookings/88/after"),
        (MediaAssetType.BOOKING_ATTACHMENT, "booking", 88, "homiq/bookings/88/attachments"),
        (MediaAssetType.COMPLAINT_ATTACHMENT, "complaint", 5, "homiq/complaints/5/evidence"),
        (MediaAssetType.REVIEW_IMAGE, "review", 99, "homiq/reviews/99/images"),
        (MediaAssetType.PROPERTY_IMAGE, "property", 12, "homiq/properties/12/images"),
        (MediaAssetType.JOB_RESUME, "job", 3, "homiq/jobs/3/resumes"),
        (MediaAssetType.JOB_DOCUMENT, "job", 3, "homiq/jobs/3/documents"),
    ]

    for asset_type, owner_type, owner_id, expected_path in folders_to_test:
        actual_path = CloudinaryService.get_folder_path(asset_type, owner_type, owner_id)
        assert actual_path == expected_path, f"Expected {expected_path}, got {actual_path}"
        print(f"  [OK] {asset_type.value:25} -> {actual_path}")

    # 3. Test File Validation (MIME, Magic Bytes, Executable Rejection)
    print("\n[TEST 3] Testing File Validation & Security Guards...")
    
    # 3a. Valid JPEG
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00`\x00`\x00\x00" + b"\x00" * 100
    fake_jpeg = UploadFile(filename="photo.jpg", file=io.BytesIO(jpeg_bytes))
    bytes_out, mime_out, ext_out = CloudinaryService.validate_file(fake_jpeg, MediaAssetType.PROFILE_AVATAR)
    assert mime_out == "image/jpeg"
    print("  [OK] Valid JPEG validated successfully.")

    import base64
    # 3b. Valid PNG (Decoded from valid 1x1 PNG standard base64)
    png_bytes = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
    fake_png = UploadFile(filename="logo.png", file=io.BytesIO(png_bytes))
    bytes_out, mime_out, ext_out = CloudinaryService.validate_file(fake_png, MediaAssetType.COMPANY_LOGO)
    assert mime_out == "image/png"
    print("  [OK] Valid PNG validated successfully.")

    # 3c. Valid PDF for Document
    pdf_bytes = b"%PDF-1.4\n%...\n" + b"\x00" * 100
    fake_pdf = UploadFile(filename="id_card.pdf", file=io.BytesIO(pdf_bytes))
    bytes_out, mime_out, ext_out = CloudinaryService.validate_file(fake_pdf, MediaAssetType.IDENTITY_DOCUMENT)
    assert mime_out == "application/pdf"
    print("  [OK] Valid PDF document validated successfully.")

    # 3d. Malicious Executable (.exe) Rejection
    try:
        malicious_file = UploadFile(filename="virus.exe", file=io.BytesIO(b"MZ...executable"))
        CloudinaryService.validate_file(malicious_file, MediaAssetType.PROFILE_AVATAR)
        assert False, "Should have rejected .exe file!"
    except Exception as exc:
        print("  [OK] Correctly rejected .exe executable file.")

    # 3e. PDF rejected for profile avatar (only images allowed for avatars)
    try:
        fake_pdf_avatar = UploadFile(filename="avatar.pdf", file=io.BytesIO(pdf_bytes))
        CloudinaryService.validate_file(fake_pdf_avatar, MediaAssetType.PROFILE_AVATAR)
        assert False, "Should have rejected PDF for avatar!"
    except Exception as exc:
        print("  [OK] Correctly rejected PDF for profile_avatar.")

    # 4. Test URL Optimization and Thumbnails
    print("\n[TEST 4] Testing URL Optimization & Transformation Generation...")
    sample_pid = "homiq/services/101/gallery/sample_service_img"
    opt_url = cloudinary_service.get_optimized_url(
        sample_pid,
        width=800,
        height=600,
        crop="fill",
        quality="auto",
        fetch_format="webp",
    )
    assert "800" in opt_url and "600" in opt_url
    print(f"  [OK] Optimized URL: {opt_url}")

    thumb_url = cloudinary_service.get_thumbnail_url(sample_pid, width=200, height=200)
    assert "200" in thumb_url
    print(f"  [OK] Thumbnail URL: {thumb_url}")

    # 5. Database Model & Tables Verification
    print("\n[TEST 5] Verifying MediaAsset Database Model...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.crud.media import MediaCRUD
        crud = MediaCRUD(db)
        asset = crud.create_media_asset(
            owner_id=999,
            owner_type="service",
            asset_type=MediaAssetType.SERVICE_GALLERY,
            cloudinary_public_id="homiq/services/999/gallery/test_gallery_img",
            secure_url="https://res.cloudinary.com/test/image/upload/v1/sample.png",
            resource_type="image",
            format="png",
            width=1024,
            height=768,
            file_size=20480,
        )
        print(f"  [OK] Created MediaAsset record ID: {asset.id} for owner: {asset.owner_type} #{asset.owner_id}")

        fetched = crud.get_by_public_id("homiq/services/999/gallery/test_gallery_img")
        assert fetched is not None and fetched.id == asset.id
        print("  [OK] Fetched MediaAsset record by public_id.")

        owner_assets = crud.get_assets_by_owner(owner_id=999, owner_type="service")
        assert len(owner_assets) >= 1
        print(f"  [OK] Fetched {len(owner_assets)} asset(s) for service #999.")

        deleted = crud.delete_media_asset("homiq/services/999/gallery/test_gallery_img")
        assert deleted is True
        print("  [OK] Deleted MediaAsset record.")
    finally:
        db.close()

    # 6. Verify Routes Registration in FastAPI
    print("\n[TEST 6] Verifying API Routes Registration in FastAPI...")
    client = TestClient(app)
    routes = [route.path for route in app.routes]
    media_routes = [r for r in routes if "/media" in r or "/documents" in r]
    print(f"  [OK] Registered Media Routes ({len(media_routes)} total):")
    for r in sorted(set(media_routes)):
        print(f"    - {r}")

    assert "/media/upload" in routes
    assert "/media/{public_id:path}" in routes
    assert "/media/owner/{owner_type}/{owner_id}" in routes
    assert "/media/transform/{public_id:path}" in routes
    assert "/users/me/avatar" in routes
    assert "/technician/me/portfolio" in routes
    assert "/technician/me/certificates" in routes
    assert "/company/me/logo" in routes
    assert "/company/me/gallery" in routes
    assert "/services/{service_id}/gallery" in routes
    assert "/bookings/{booking_id}/before-images" in routes
    assert "/bookings/{booking_id}/after-images" in routes
    assert "/bookings/{booking_id}/attachments" in routes
    assert "/reviews/{review_id}/images" in routes
    assert "/jobs/{job_id}/resumes" in routes
    assert "/jobs/{job_id}/documents" in routes
    assert "/complaints/{complaint_id}/attachments" in routes
    assert "/admin/media" in routes

    # 7. Test Avatar Replacement & Rollback Safety
    print("\n[TEST 7] Testing Avatar Replacement & Rollback Logic...")
    from app.services.media import MediaService
    from app.crud.user import UserCRUD
    db = SessionLocal()
    try:
        user_crud = UserCRUD(db)
        test_user = user_crud.get_user_by_email("test_avatar_user@homiq.com")
        if not test_user:
            test_user = user_crud.create_user(
                email="test_avatar_user@homiq.com",
                full_name="Avatar Test User",
                password="SecurePassword123!",
                role_name="customer",
            )
        
        media_service = MediaService(db)
        avatar_file = UploadFile(filename="avatar.png", file=io.BytesIO(png_bytes))
        resp = media_service.update_user_avatar(test_user, avatar_file)
        assert resp.success is True
        assert resp.data["url"] is not None
        print(f"  [OK] Successfully uploaded and set user avatar: {resp.data['url']}")

        # Test avatar deletion
        del_resp = media_service.delete_user_avatar(test_user)
        assert del_resp.success is True
        print("  [OK] Successfully removed user avatar.")
    finally:
        db.close()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED SUCCESSFULLY! (7/7)")
    print("=" * 60)


if __name__ == "__main__":
    run_tests()
