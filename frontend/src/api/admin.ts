import api from './axios';
import { AdminSettings, AnalyticsOverview, Booking, BookingStatusLog, TechnicianProfile, User } from '../types';

export interface AdminDashboardData {
  total_users: number;
  total_customers: number;
  total_technicians: number;
  total_bookings: number;
  total_revenue: number;
  recent_bookings: Booking[];
  pending_verifications_count: number;
}

export interface AdminTechnicianDoc {
  id: number;
  technician_id: number;
  doc_type: string;
  file_url: string;
  is_verified: boolean;
  created_at: string;
}

export const adminApi = {
  getDashboard: async (): Promise<AdminDashboardData> => {
    const response = await api.get<AdminDashboardData>('/admin/dashboard');
    return response.data;
  },

  getUsers: async (params?: { role?: string; is_active?: boolean; offset?: number; limit?: number }): Promise<User[]> => {
    const response = await api.get<User[]>('/admin/users', { params });
    return response.data;
  },

  getUser: async (id: number): Promise<User & { bookings?: Booking[] }> => {
    const response = await api.get<User & { bookings?: Booking[] }>(`/admin/users/${id}`);
    return response.data;
  },

  suspendUser: async (id: number): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${id}/suspend`);
    return response.data;
  },

  activateUser: async (id: number): Promise<User> => {
    const response = await api.patch<User>(`/admin/users/${id}/activate`);
    return response.data;
  },

  deleteUser: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/admin/users/${id}`);
    return response.data;
  },

  getTechnicians: async (params?: { is_verified?: boolean; offset?: number; limit?: number }): Promise<TechnicianProfile[]> => {
    const response = await api.get<TechnicianProfile[]>('/admin/technicians', { params });
    return response.data;
  },

  getTechnicianDocs: async (technicianId: number): Promise<AdminTechnicianDoc[]> => {
    const response = await api.get<AdminTechnicianDoc[]>(`/admin/technicians/${technicianId}/documents`);
    return response.data;
  },

  approveDoc: async (docId: number): Promise<AdminTechnicianDoc> => {
    const response = await api.patch<AdminTechnicianDoc>(`/admin/documents/${docId}/approve`);
    return response.data;
  },

  rejectDoc: async (docId: number): Promise<AdminTechnicianDoc> => {
    const response = await api.patch<AdminTechnicianDoc>(`/admin/documents/${docId}/reject`);
    return response.data;
  },

  approveTechnician: async (technicianId: number): Promise<TechnicianProfile> => {
    const response = await api.patch<TechnicianProfile>(`/admin/technicians/${technicianId}/approve`);
    return response.data;
  },

  rejectTechnician: async (technicianId: number): Promise<TechnicianProfile> => {
    const response = await api.patch<TechnicianProfile>(`/admin/technicians/${technicianId}/reject`);
    return response.data;
  },

  suspendTechnician: async (technicianId: number): Promise<TechnicianProfile> => {
    const response = await api.patch<TechnicianProfile>(`/admin/technicians/${technicianId}/suspend`);
    return response.data;
  },

  activateTechnician: async (technicianId: number): Promise<TechnicianProfile> => {
    const response = await api.patch<TechnicianProfile>(`/admin/technicians/${technicianId}/activate`);
    return response.data;
  },

  getBookings: async (params?: { status?: string; offset?: number; limit?: number }): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/admin/bookings', { params });
    return response.data;
  },

  getBooking: async (id: number): Promise<Booking> => {
    const response = await api.get<Booking>(`/admin/bookings/${id}`);
    return response.data;
  },

  getBookingLogs: async (id: number): Promise<BookingStatusLog[]> => {
    const response = await api.get<BookingStatusLog[]>(`/admin/bookings/${id}/logs`);
    return response.data;
  },

  assignTechnician: async (bookingId: number, technicianId: number): Promise<Booking> => {
    const response = await api.put<Booking>(`/admin/bookings/${bookingId}/assign`, {
      technician_id: technicianId,
    });
    return response.data;
  },

  reassignTechnician: async (bookingId: number, technicianId: number): Promise<Booking> => {
    const response = await api.put<Booking>(`/admin/bookings/${bookingId}/reassign`, {
      technician_id: technicianId,
    });
    return response.data;
  },

  updateBookingStatus: async (bookingId: number, status: string, admin_note?: string): Promise<Booking> => {
    const response = await api.put<Booking>(`/admin/bookings/${bookingId}/status`, {
      status,
      admin_note,
    });
    return response.data;
  },

  overrideBookingStatus: async (bookingId: number, status: string, admin_note?: string): Promise<Booking> => {
    const response = await api.put<Booking>(`/admin/bookings/${bookingId}/override-status`, {
      status,
      admin_note,
    });
    return response.data;
  },

  forceCancelBooking: async (bookingId: number, reason?: string): Promise<Booking> => {
    const response = await api.post<Booking>(`/admin/bookings/${bookingId}/force-cancel`, { reason });
    return response.data;
  },

  // Analytics & Reports
  getOverviewAnalytics: async (): Promise<AnalyticsOverview> => {
    const response = await api.get<AnalyticsOverview>('/admin/analytics/overview');
    return response.data;
  },

  getGrowthAnalytics: async (): Promise<any> => {
    const response = await api.get<any>('/admin/analytics/growth');
    return response.data;
  },

  getCustomerAnalytics: async (): Promise<any> => {
    const response = await api.get<any>('/admin/analytics/customers');
    return response.data;
  },

  getBookingAnalytics: async (): Promise<any> => {
    const response = await api.get<any>('/admin/analytics/bookings');
    return response.data;
  },

  getRevenueAnalytics: async (): Promise<any> => {
    const response = await api.get<any>('/admin/analytics/revenue');
    return response.data;
  },

  getReports: async (): Promise<any> => {
    const response = await api.get<any>('/admin/reports');
    return response.data;
  },

  getRevenueReport: async (params?: { start_date?: string; end_date?: string }): Promise<any> => {
    const response = await api.get<any>('/admin/reports/revenue', { params });
    return response.data;
  },

  getSettings: async (): Promise<AdminSettings> => {
    const response = await api.get<AdminSettings>('/admin/settings');
    return response.data;
  },

  updateSettings: async (settings: Partial<AdminSettings>): Promise<AdminSettings> => {
    const response = await api.put<AdminSettings>('/admin/settings', settings);
    return response.data;
  },
};
