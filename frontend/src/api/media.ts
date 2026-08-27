import api from './axios';

export type MediaAssetType =
  | 'profile_avatar'
  | 'company_logo'
  | 'service_image'
  | 'service_gallery'
  | 'technician_portfolio'
  | 'technician_certificate'
  | 'identity_document'
  | 'booking_before'
  | 'booking_after'
  | 'booking_attachment'
  | 'complaint_attachment'
  | 'review_image'
  | 'property_image'
  | 'job_resume'
  | 'job_document';

export interface MediaAssetResponse {
  id: number;
  owner_id: number;
  owner_type: string;
  asset_type: MediaAssetType;
  cloudinary_asset_id?: string;
  cloudinary_public_id: string;
  secure_url: string;
  thumbnail_url?: string;
  resource_type: string;
  format: string;
  width?: number;
  height?: number;
  file_size: number;
  created_at: string;
  updated_at: string;
}

export interface MediaAssetListResponse {
  total: number;
  items: MediaAssetResponse[];
}

export const mediaApi = {
  uploadMedia: async (data: {
    file: File;
    asset_type: MediaAssetType;
    owner_id?: number;
    owner_type?: string;
  }): Promise<MediaAssetResponse> => {
    const formData = new FormData();
    formData.append('file', data.file);
    formData.append('asset_type', data.asset_type);
    if (data.owner_id !== undefined) formData.append('owner_id', data.owner_id.toString());
    if (data.owner_type !== undefined) formData.append('owner_type', data.owner_type);

    const response = await api.post<MediaAssetResponse>('/media/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  getOwnerMedia: async (
    ownerType: string,
    ownerId: number,
    assetType?: MediaAssetType
  ): Promise<MediaAssetListResponse> => {
    const params = assetType ? { asset_type: assetType } : {};
    const response = await api.get<MediaAssetListResponse>(`/media/owner/${ownerType}/${ownerId}`, {
      params,
    });
    return response.data;
  },

  deleteMedia: async (publicId: string): Promise<any> => {
    const response = await api.delete(`/media/${encodeURIComponent(publicId)}`);
    return response.data;
  },
};
