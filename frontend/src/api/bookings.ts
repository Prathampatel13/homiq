import api from './axios';
import { Booking, BookingStatusLog, TechnicianProfile, VerificationStatus } from '../types';

export interface CreateBookingPayload {
  service_id: number;
  address_id: number;
  booking_date: string; // YYYY-MM-DD
  preferred_time: string; // HH:MM:SS or HH:MM
  estimated_price?: number;
  customer_note?: string;
}

export const bookingsApi = {
  getBookings: async (params?: { status?: string; offset?: number; limit?: number }): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/bookings/', { params });
    return response.data;
  },

  getBooking: async (id: number): Promise<Booking> => {
    const response = await api.get<Booking>(`/bookings/${id}`);
    return response.data;
  },

  createBooking: async (payload: CreateBookingPayload): Promise<Booking> => {
    const response = await api.post<Booking>('/bookings/', payload);
    return response.data;
  },

  updateBooking: async (id: number, data: { customer_note?: string }): Promise<Booking> => {
    const response = await api.put<Booking>(`/bookings/${id}`, data);
    return response.data;
  },

  rescheduleBooking: async (id: number, data: { booking_date: string; preferred_time: string }): Promise<Booking> => {
    const response = await api.put<Booking>(`/bookings/${id}/reschedule`, data);
    return response.data;
  },

  cancelBooking: async (id: number, reason?: string): Promise<Booking> => {
    const response = await api.post<Booking>(`/bookings/${id}/cancel`, { reason });
    return response.data;
  },

  generatePin: async (id: number): Promise<{ message: string; pin_expires_at: string; pin_code: string }> => {
    const response = await api.post<{ message: string; pin_expires_at: string; pin_code: string }>(`/bookings/${id}/generate-pin`);
    return response.data;
  },

  verifyPin: async (id: number, pin: string): Promise<{ message: string; verified_at: string }> => {
    const response = await api.post<{ message: string; verified_at: string }>(`/bookings/${id}/verify-pin`, { pin });
    return response.data;
  },

  generateQr: async (id: number): Promise<{ verification_token: string; qr_code_data: string; expires_at: string }> => {
    const response = await api.post<{ verification_token: string; qr_code_data: string; expires_at: string }>(`/bookings/${id}/qr`);
    return response.data;
  },

  getQr: async (id: number): Promise<{ verification_token: string; qr_code_data: string; expires_at: string }> => {
    const response = await api.get<{ verification_token: string; qr_code_data: string; expires_at: string }>(`/bookings/${id}/qr`);
    return response.data;
  },

  scanQr: async (id: number, verification_token: string): Promise<{ message: string; status: string }> => {
    const response = await api.post<{ message: string; status: string }>(`/bookings/${id}/scan-qr`, { verification_token });
    return response.data;
  },

  customerConfirm: async (id: number): Promise<{ message: string; verification_status: string }> => {
    const response = await api.post<{ message: string; verification_status: string }>(`/bookings/${id}/customer-confirm`);
    return response.data;
  },

  technicianConfirm: async (id: number): Promise<{ message: string; verification_status: string }> => {
    const response = await api.post<{ message: string; verification_status: string }>(`/bookings/${id}/technician-confirm`);
    return response.data;
  },

  getVerificationStatus: async (id: number): Promise<VerificationStatus> => {
    const response = await api.get<VerificationStatus>(`/bookings/${id}/verification-status`);
    return response.data;
  },

  getHistoryLogs: async (id: number): Promise<BookingStatusLog[]> => {
    const response = await api.get<BookingStatusLog[]>(`/bookings/${id}/history`);
    return response.data;
  },

  getAssignedTechnician: async (id: number): Promise<TechnicianProfile> => {
    const response = await api.get<TechnicianProfile>(`/bookings/${id}/technician`);
    return response.data;
  },
};
