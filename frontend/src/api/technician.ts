import api from './axios';
import { Booking, TechnicianProfile } from '../types';

export interface TechnicianDashboardStats {
  today_jobs_count: number;
  active_jobs_count: number;
  completed_jobs_count: number;
  total_earnings: number;
  rating_avg: number;
  total_reviews: number;
  is_online: boolean;
  availability: boolean;
}

export interface VerificationDocument {
  id: number;
  technician_id: number;
  doc_type: string;
  file_url: string;
  is_verified: boolean;
  created_at: string;
}

export const technicianApi = {
  getProfile: async (): Promise<TechnicianProfile> => {
    const response = await api.get<TechnicianProfile>('/technician/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<TechnicianProfile>): Promise<TechnicianProfile> => {
    const response = await api.put<TechnicianProfile>('/technician/profile', data);
    return response.data;
  },

  uploadImage: async (file: File): Promise<{ image_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ image_url: string }>('/technician/profile/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadGovtId: async (file: File): Promise<{ govt_id_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ govt_id_url: string }>('/technician/profile/government-id', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  uploadDocument: async (doc_type: string, file: File): Promise<VerificationDocument> => {
    const formData = new FormData();
    formData.append('doc_type', doc_type);
    formData.append('file', file);
    const response = await api.post<VerificationDocument>('/technician/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getDocuments: async (): Promise<VerificationDocument[]> => {
    const response = await api.get<VerificationDocument[]>('/technician/documents');
    return response.data;
  },

  setOnline: async (): Promise<{ message: string; is_online: boolean }> => {
    const response = await api.patch<{ message: string; is_online: boolean }>('/technician/online');
    return response.data;
  },

  setOffline: async (): Promise<{ message: string; is_online: boolean }> => {
    const response = await api.patch<{ message: string; is_online: boolean }>('/technician/offline');
    return response.data;
  },

  setAvailability: async (availability: boolean, is_online: boolean): Promise<TechnicianProfile> => {
    const response = await api.put<TechnicianProfile>('/technician/availability', {
      availability,
      is_online,
    });
    return response.data;
  },

  getBookingHistory: async (params?: { offset?: number; limit?: number }): Promise<{ items: Booking[]; total: number }> => {
    const response = await api.get<{ items: Booking[]; total: number }>('/technician/history', { params });
    return response.data;
  },

  getCustomerHistory: async (customerId: number, params?: { offset?: number; limit?: number }): Promise<{ items: Booking[]; total: number }> => {
    const response = await api.get<{ items: Booking[]; total: number }>(`/technician/customers/${customerId}/history`, { params });
    return response.data;
  },

  getMyJobs: async (params?: { status?: string; offset?: number; limit?: number }): Promise<Booking[] | { items: Booking[]; total: number }> => {
    const response = await api.get<Booking[] | { items: Booking[]; total: number }>('/technician/jobs', { params });
    return response.data;
  },

  getMyBookings: async (): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/technician/bookings');
    return response.data;
  },

  getActiveBookings: async (): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/technician/bookings/active');
    return response.data;
  },

  getHistory: async (): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/technician/history');
    return response.data;
  },

  getEarnings: async (): Promise<{ total_earnings: number; pending_payout: number; completed_jobs: number }> => {
    const response = await api.get<{ total_earnings: number; pending_payout: number; completed_jobs: number }>('/technician/earnings');
    return response.data;
  },

  getDashboard: async (): Promise<TechnicianDashboardStats> => {
    const response = await api.get<TechnicianDashboardStats>('/technician/dashboard');
    return response.data;
  },

  // Lifecycle status actions
  acceptBooking: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/accept`, { reason });
    return response.data;
  },

  rejectBooking: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/reject`, { reason });
    return response.data;
  },

  startTrip: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/start-trip`, { reason });
    return response.data;
  },

  markArrived: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/arrived`, { reason });
    return response.data;
  },

  startService: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/start-service`, { reason });
    return response.data;
  },

  completeService: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.patch<Booking>(`/technician/bookings/${id}/complete`, { reason });
    return response.data;
  },
};
