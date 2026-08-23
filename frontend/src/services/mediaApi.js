/**
 * HomiQ Centralized Media & Cloudinary API Service.
 * 
 * Interacts with FastAPI backend for secure uploads, file validation,
 * transformations, and asset management.
 */

const API_BASE_URL = import.meta.env?.VITE_API_BASE_URL || import.meta.env?.VITE_API_URL || 'http://localhost:8000';

/**
 * Generic helper for authenticated multipart/form-data uploads.
 */
async function uploadMultipart(endpoint, formData, token = null) {
  const authToken = token || localStorage.getItem('homiq_access_token') || localStorage.getItem('token') || sessionStorage.getItem('token');
  const headers = {};
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Upload failed');
  }
  return data;
}

/**
 * Generic helper for authenticated JSON API requests.
 */
async function authenticatedRequest(endpoint, method = 'GET', body = null, token = null) {
  const authToken = token || localStorage.getItem('homiq_access_token') || localStorage.getItem('token') || sessionStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json' };
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const options = { method, headers };
  if (body) {
    options.body = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data?.detail || data?.message || 'Request failed');
  }
  return data;
}

// ── 1. USER PROFILE AVATAR ───────────────────────────────────────────────

export async function uploadAvatar(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/users/me/avatar', formData);
}

export async function deleteAvatar() {
  return authenticatedRequest('/users/me/avatar', 'DELETE');
}

// ── 2. TECHNICIAN MEDIA ──────────────────────────────────────────────────

export async function uploadTechnicianAvatar(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/technicians/me/avatar', formData);
}

export async function uploadPortfolio(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/technicians/me/portfolio', formData);
}

export async function listPortfolio() {
  return authenticatedRequest('/technicians/me/portfolio', 'GET');
}

export async function deletePortfolio(assetId) {
  return authenticatedRequest(`/technicians/me/portfolio/${assetId}`, 'DELETE');
}

export async function uploadCertificate(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/technicians/me/certificates', formData);
}

export async function listCertificates() {
  return authenticatedRequest('/technicians/me/certificates', 'GET');
}

export async function deleteCertificate(assetId) {
  return authenticatedRequest(`/technicians/me/certificates/${assetId}`, 'DELETE');
}

export async function uploadVerificationDocument(docType, file) {
  const formData = new FormData();
  formData.append('doc_type', docType);
  formData.append('file', file);
  return uploadMultipart('/technician/documents', formData);
}

// ── 3. COMPANY MEDIA ─────────────────────────────────────────────────────

export async function uploadCompanyLogo(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/company/me/logo', formData);
}

export async function uploadCompanyGallery(file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart('/company/me/gallery', formData);
}

export async function listCompanyGallery(companyId = null) {
  const endpoint = companyId ? `/company/${companyId}/gallery` : '/company/me/gallery';
  return authenticatedRequest(endpoint, 'GET');
}

// ── 4. SERVICE MEDIA ─────────────────────────────────────────────────────

export async function uploadServiceGallery(serviceId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/services/${serviceId}/gallery`, formData);
}

export async function listServiceGallery(serviceId) {
  return authenticatedRequest(`/services/${serviceId}/gallery`, 'GET');
}

// ── 5. BOOKING MEDIA ─────────────────────────────────────────────────────

export async function uploadBookingBeforeImage(bookingId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/bookings/${bookingId}/before-images`, formData);
}

export async function uploadBookingAfterImage(bookingId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/bookings/${bookingId}/after-images`, formData);
}

export async function uploadBookingAttachment(bookingId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/bookings/${bookingId}/attachments`, formData);
}

export async function listBookingMedia(bookingId) {
  return authenticatedRequest(`/bookings/${bookingId}/media`, 'GET');
}

// ── 6. COMPLAINTS & REVIEWS ──────────────────────────────────────────────

export async function uploadComplaintAttachment(complaintId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/complaints/${complaintId}/attachments`, formData);
}

export async function uploadReviewImage(reviewId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/reviews/${reviewId}/images`, formData);
}

// ── 7. JOB & RECRUITMENT ─────────────────────────────────────────────────

export async function uploadJobResume(jobId, file) {
  const formData = new FormData();
  formData.append('file', file);
  return uploadMultipart(`/jobs/${jobId}/resumes`, formData);
}

// ── 8. CLOUDINARY URL TRANSFORMATION ─────────────────────────────────────

export async function getTransformedImageUrl(publicId, options = {}) {
  const { width = 400, height = 400, crop = 'fill', quality = 'auto', fetch_format = 'webp' } = options;
  return authenticatedRequest(`/media/transform/${encodeURIComponent(publicId)}`, 'POST', {
    width,
    height,
    crop,
    quality,
    fetch_format,
    gravity: 'auto',
  });
}
