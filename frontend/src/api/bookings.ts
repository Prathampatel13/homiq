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

  // SmartVerify Cryptographic Flows
  generateQr: async (id: number): Promise<{ verification_token: string; qr_code_url?: string; expires_in?: number }> => {
    const response = await api.post<{ verification_token: string; qr_code_url?: string; expires_in?: number }>(`/bookings/${id}/generate-qr`);
    return response.data;
  },

  getQr: async (id: number): Promise<{ verification_token: string; qr_code_url?: string; is_valid: boolean }> => {
    const response = await api.get<{ verification_token: string; qr_code_url?: string; is_valid: boolean }>(`/bookings/${id}/qr`);
    return response.data;
  },

  scanQr: async (id: number, verification_token: string): Promise<Booking> => {
    const response = await api.post<Booking>(`/bookings/${id}/scan-qr`, { verification_token });
    return response.data;
  },

  generateOtp: async (id: number): Promise<{ otp_code: string; expires_in?: number }> => {
    const response = await api.post<{ otp_code: string; expires_in?: number }>(`/bookings/${id}/generate-otp`);
    return response.data;
  },

  verifyOtp: async (id: number, otp_code: string): Promise<Booking> => {
    const response = await api.post<Booking>(`/bookings/${id}/verify-otp`, { otp_code });
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
