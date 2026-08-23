# HomiQ Enterprise Cloudinary Media & Document Management Architecture

This document provides complete instructions for setting up, configuring, integrating, and operating the centralized **Cloudinary Media & Document Architecture** in HomiQ.

---

## 1. Cloudinary Account Setup & Credentials

1. **Sign Up**: Register for a free or enterprise Cloudinary account at [cloudinary.com](https://cloudinary.com).
2. **Dashboard Credentials**: In your Cloudinary Console dashboard, locate:
   - **Cloud Name** (`CLOUDINARY_CLOUD_NAME`)
   - **API Key** (`CLOUDINARY_API_KEY`)
   - **API Secret** (`CLOUDINARY_API_SECRET`)
3. **Environment Configuration**:
   Add the credentials to `homiq/backend/.env`:
   ```dotenv
   CLOUDINARY_CLOUD_NAME=your_actual_cloud_name
   CLOUDINARY_API_KEY=your_actual_api_key
   CLOUDINARY_API_SECRET=your_actual_api_secret
   ```

> [!CAUTION]
> **Zero Secret Leakage Policy**: `CLOUDINARY_API_SECRET` must **never** be hard-coded or exposed to the React frontend. Never create `VITE_CLOUDINARY_API_SECRET`. All uploads, signing, and deletions are securely proxied through FastAPI.

---

## 2. Centralized Configuration Provider

Centralized in `app/core/cloudinary_config.py` using `app/core/config.py`:
- `init_cloudinary()` validates credentials on application startup and registers the single global Cloudinary SDK configuration.
- `is_cloudinary_configured()` allows graceful fallback and unit-testing if credentials are temporarily not loaded.

---

## 3. Deterministic Folder Structure

Assets are automatically routed to deterministic folders based on the entity type and ID:

```
homiq/
├── users/
│   └── {user_id}/
│       └── profile/             # Profile avatars
├── technicians/
│   └── {technician_id}/
│       ├── profile/             # Technician avatar
│       ├── portfolio/           # Work portfolio samples
│       ├── certificates/        # Licenses & certifications
│       └── documents/           # Aadhaar / PAN / Govt ID verification
├── companies/
│   └── {company_id}/
│       ├── logo/                # Company brand logo
│       └── gallery/             # Company facility / work photos
├── services/
│   └── {service_id}/
│       └── gallery/             # Service gallery & preview images
├── bookings/
│   └── {booking_id}/
│       ├── before/              # Before-service photos
│       ├── after/               # After-service photos
│       └── attachments/         # Blueprints / job invoices
├── complaints/
│   └── {complaint_id}/
│       └── evidence/            # Customer complaint evidence
├── reviews/
│   └── {review_id}/
│       └── images/              # Verified customer review photos
└── jobs/
    └── {job_id}/
        ├── resumes/             # Technician application resumes (PDF)
        └── documents/           # Job post specifications (PDF/Image)
```

---

## 4. Supported Asset Types & Strict File Validation

| Category | Asset Type | Allowed Formats | Max File Size | Magic Byte Check |
| :--- | :--- | :--- | :--- | :--- |
| **Profile Avatars** | `profile_avatar` | JPEG, PNG, WebP | `5 MB` | Yes (`\xff\xd8\xff`, `\x89PNG`, `RIFF..WEBP`) |
| **Portfolios & Galleries** | `technician_portfolio`<br>`company_logo`, `service_gallery` | JPEG, PNG, WebP | `10 MB` | Yes |
| **Verification & Documents** | `technician_certificate`<br>`identity_document`<br>`booking_attachment`<br>`job_resume`, `job_document` | PDF, JPEG, PNG, WebP | `10 MB` | Yes (`%PDF-`, image headers) |

**Security Enforcement**:
- Executable file extensions (`.exe`, `.sh`, `.bat`, `.py`, `.js`, `.dll`, `.msi`, `.php`) are immediately rejected with `400 Bad Request`.
- Mismatched MIME types vs magic bytes trigger `415 Unsupported Media Type`.
- Oversized payloads trigger `413 Request Entity Too Large`.

---

## 5. Database Media Structure (`media_assets`)

Stored in MySQL/PostgreSQL via SQLAlchemy `MediaAsset` model:
- `id` (Integer Primary Key)
- `owner_id` (Integer, Indexed)
- `owner_type` (String, Indexed e.g., "user", "technician", "company", "service", "booking", "complaint", "review", "job")
- `asset_type` (String, Indexed e.g., "profile_avatar", "technician_portfolio", "booking_before", etc.)
- `cloudinary_asset_id` (String)
- `cloudinary_public_id` (String Unique, Indexed)
- `secure_url` (String URL)
- `resource_type` (String, "image" or "raw")
- `format` (String, "png", "jpg", "pdf", "webp")
- `width`, `height` (Integer dimensions for images)
- `file_size` (BigInteger bytes)
- `created_at`, `updated_at` (DateTime with UTC timezone)

---

## 6. Public vs. Private Asset Strategy

1. **Public Assets** (Fast CDN Delivery):
   - Service galleries, company logos, technician public portfolios, and user avatars.
   - Served directly via Cloudinary CDN edge nodes with WebP auto-formatting and dynamic thumbnail generation.
2. **Private & Sensitive Assets** (Strict RBAC Authorization):
   - Government identification documents (Aadhaar, PAN), booking before/after photos, booking invoice attachments, complaint dispute evidence, and candidate resumes.
   - Upload, retrieval, listing, and deletion are gated by FastAPI JWT dependencies (`get_current_user`, `get_current_technician`, `get_current_company`, `get_current_admin`).
   - Booking media can only be viewed/uploaded by the assigned technician, booking customer, or superuser admin.

---

## 7. Transactional Rollback & Avatar Replacement Safety

Implemented in `app.services.media.MediaService.update_user_avatar`:
1. **Upload New Asset First**: Uploads new image to Cloudinary and acquires new public ID and secure URL.
2. **Database Update with Catch-and-Rollback**: Persists the new `MediaAsset` record and updates user `avatar_url`. If database transaction fails, it immediately purges the newly uploaded Cloudinary asset to avoid orphaned files in CDN storage.
3. **Safe Deletion of Previous Asset**: Only deletes the old Cloudinary asset after database success. If old deletion fails, the new asset remains active and the failure is logged without blocking the user.

---

## 8. Complete REST API Endpoints by Domain

### User Profile
- `POST /users/me/avatar` — Upload or replace profile avatar.
- `DELETE /users/me/avatar` — Delete current avatar.
- `GET /users/me` — Returns profile with `avatar_url`.

### Technician Media
- `POST /technicians/me/avatar` & `DELETE /technicians/me/avatar` — Avatar management.
- `POST /technicians/me/portfolio` & `GET /technicians/me/portfolio` & `DELETE /technicians/me/portfolio/{asset_id}` — Portfolio gallery.
- `POST /technicians/me/certificates` & `GET /technicians/me/certificates` & `DELETE /technicians/me/certificates/{asset_id}` — Certifications.
- `POST /technician/documents` — Government ID / Aadhaar verification upload.

### Company Media
- `POST /company/me/logo` — Company brand logo.
- `POST /company/me/gallery` & `GET /company/me/gallery` & `DELETE /company/me/gallery/{asset_id}` — Gallery photos.
- `GET /company/{company_id}/gallery` — Public gallery view.

### Service Media
- `POST /services/{service_id}/image` — Service thumbnail.
- `POST /services/{service_id}/gallery` & `GET /services/{service_id}/gallery` & `DELETE /services/{service_id}/gallery/{asset_id}` — Service gallery.

### Booking Media
- `POST /bookings/{booking_id}/before-images` — Before-work photo.
- `POST /bookings/{booking_id}/after-images` — After-work photo.
- `POST /bookings/{booking_id}/attachments` — Document attachment.
- `GET /bookings/{booking_id}/media` & `DELETE /bookings/{booking_id}/media/{asset_id}` — Booking media items.

### Reviews, Complaints & Jobs
- `POST /reviews/{review_id}/images` & `GET /reviews/{review_id}/images` — Review photos.
- `POST /complaints/{complaint_id}/attachments` & `GET /complaints/{complaint_id}/attachments` — Complaint evidence.
- `POST /jobs/{job_id}/resumes` & `POST /jobs/{job_id}/documents` — Job files.

### Dynamic Transformations & Admin
- `POST /media/transform/{public_id}` — On-the-fly thumbnail and optimization generation.
- `GET /admin/media` — Filter and monitor all platform media assets.
- `DELETE /admin/media/{asset_id}` — Administrator removal.

---

## 9. Standardized API Response Format

```json
{
  "success": true,
  "message": "Profile avatar updated successfully.",
  "data": {
    "id": 42,
    "url": "https://res.cloudinary.com/homiq/image/upload/v1/homiq/users/7/profile/avatar.jpg",
    "secure_url": "https://res.cloudinary.com/homiq/image/upload/v1/homiq/users/7/profile/avatar.jpg",
    "thumbnail_url": "https://res.cloudinary.com/homiq/image/upload/c_fill,h_200,w_200/homiq/users/7/profile/avatar.jpg",
    "public_id": "homiq/users/7/profile/avatar",
    "asset_type": "profile_avatar"
  }
}
```

---

## 10. Frontend React Integration

### 1. API Client Helper (`homiq/frontend/src/services/mediaApi.js`)
```javascript
import { uploadAvatar, uploadPortfolio, deleteAvatar } from '@/services/mediaApi';

// Upload user avatar
const res = await uploadAvatar(selectedFile);
console.log('New avatar URL:', res.data.secure_url);
```

### 2. MediaUploader Component (`homiq/frontend/src/components/MediaUploader.jsx`)
```jsx
import MediaUploader from '@/components/MediaUploader';
import { uploadAvatar, deleteAvatar } from '@/services/mediaApi';

<MediaUploader
  label="Profile Photo"
  uploadFunction={uploadAvatar}
  onDeleteSuccess={deleteAvatar}
  currentImageUrl={user.avatar_url}
  accept="image/jpeg,image/png,image/webp"
  maxSizeMB={5}
  onUploadSuccess={(res) => {
    updateUserProfile({ avatar_url: res.data.secure_url });
  }}
/>
```

---

## 11. Production Deployment Configuration

When deploying the HomiQ backend to Docker, AWS ECS, Google Cloud Run, Railway, or Render:
1. Supply the 3 environment variables in your cloud secret manager / environment configuration:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
2. Run database migrations:
   ```bash
   alembic upgrade head
   ```
3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

## 12. Security Precautions & Best Practices

1. **Never commit `.env`**: `.gitignore` is configured at root and backend levels.
2. **Never expose `CLOUDINARY_API_SECRET` to the frontend**: All asset uploads, replacements, and deletions pass through FastAPI endpoints with JWT validation.
3. **Magic Byte Verification**: File extension spoofing (e.g. uploading `malware.exe` renamed as `avatar.png`) is prevented via binary signature verification.
4. **Deterministic Storage**: Folders are strictly scoped to owner IDs and asset categories.
5. **Atomic Consistency**: DB failures trigger immediate Cloudinary rollback to prevent orphaned cloud assets.

---

## 13. Automated Testing & Verification Guide

Run the automated backend test suite:
```bash
python test_media_service.py
```
This validates all 7 core modules:
1. Centralized Cloudinary configuration loading.
2. Deterministic folder resolution across all 15 asset types.
3. Magic byte inspection, file size guards, and executable rejection.
4. Dynamic URL transformations and thumbnail generation.
5. `MediaAsset` database CRUD operations.
6. FastAPI route registration (284 active endpoints).
7. Live user avatar replacement, Cloudinary upload, DB persistence, and rollback logic.
