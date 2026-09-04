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

  verifyCode: async (id: number, code: string): Promise<Booking> => {
    const response = await api.post<Booking>(`/bookings/${id}/verify-code`, { code });
    return response.data;
  },

  getVerificationDetails: async (id: number): Promise<{ verification_code: string; qr_token: string; is_verified: boolean; qr_data: string }> => {
    const response = await api.get<{ verification_code: string; qr_token: string; is_verified: boolean; qr_data: string }>(`/bookings/${id}/verification-details`);
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
