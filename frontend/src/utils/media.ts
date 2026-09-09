import React from 'react';

export const FALLBACK_IMAGES = {
  before: '/assets/services/electrical.jpg',
  after: '/assets/hero_ac.jpg',
  service: '/assets/services/ac.jpg',
  plumbing: '/assets/services/plumbing.jpg',
  cleaning: '/assets/services/cleaning.jpg',
  carpentry: '/assets/services/carpentry.jpg',
  security: '/assets/services/security.jpg',
  general: '/assets/services/ac.jpg',
  avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80',
};

export type FallbackImageType = keyof typeof FALLBACK_IMAGES;

/**
 * Cleanly transforms any media URL (backend relative path, legacy mock, external)
 * into a valid, displayable image URL with reliable fallbacks.
 */
export const getSafeMediaUrl = (
  url?: string | null,
  type: FallbackImageType = 'general'
): string => {
  const fallback = FALLBACK_IMAGES[type] || FALLBACK_IMAGES.general;

  if (!url || typeof url !== 'string' || !url.trim()) {
    return fallback;
  }

  const trimmed = url.trim();

  // Legacy fake Cloudinary URLs that have no backing file in storage
  if (trimmed.includes('homiq-cloud') || trimmed.includes('res.cloudinary.com/homiq-cloud')) {
    return fallback;
  }

  // If it's a relative path from backend storage (e.g. /uploads/...)
  if (trimmed.startsWith('/uploads') || trimmed.startsWith('uploads/')) {
    const backendBase = (import.meta.env.VITE_API_BASE_URL || 'https://homiq-backend-af73.onrender.com').replace(/\/$/, '');
    const cleanPath = trimmed.startsWith('/') ? trimmed : `/${trimmed}`;
    return `${backendBase}${cleanPath}`;
  }

  // If it's a frontend public asset (starts with /assets/ or /)
  if (trimmed.startsWith('/')) {
    return trimmed;
  }

  // If it's a valid remote URL
  if (trimmed.startsWith('http://') || trimmed.startsWith('https://')) {
    return trimmed;
  }

  return fallback;
};

/**
 * Safe image onError handler to prevent any broken image icon or alt-only rendering.
 */
export const handleImageError = (
  e: React.SyntheticEvent<HTMLImageElement, Event>,
  type: FallbackImageType = 'general'
) => {
  const target = e.currentTarget;
  const fallback = FALLBACK_IMAGES[type] || FALLBACK_IMAGES.general;
  if (!target.dataset.fallbackApplied) {
    target.dataset.fallbackApplied = 'true';
    target.src = fallback;
  }
};
