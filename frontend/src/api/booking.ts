import api from './axios';
import { Booking, BookingStatus } from '../types';

export interface CreateBookingPayload {
  service_id: number;
  address_id: number;
  booking_date: string;
  preferred_time: string;
  promo_code?: string;
  special_instructions?: string;
}

export const bookingApi = {
  createBooking: async (payload: CreateBookingPayload): Promise<Booking> => {
    const res = await api.post('/bookings/', payload);
    return res.data;
  },

  getCustomerBookings: async (): Promise<Booking[]> => {
    const res = await api.get('/bookings/customer');
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  getTechnicianBookings: async (): Promise<Booking[]> => {
    const res = await api.get('/bookings/technician');
    return Array.isArray(res.data) ? res.data : (res.data?.items || []);
  },

  getBookingById: async (id: number): Promise<Booking> => {
    const res = await api.get(`/bookings/${id}`);
    return res.data;
  },

  acceptBooking: async (id: number): Promise<Booking> => {
    const res = await api.post(`/bookings/${id}/accept`);
    return res.data;
  },

  updateBookingStatus: async (id: number, status: BookingStatus): Promise<Booking> => {
    const res = await api.post(`/bookings/${id}/status`, { status });
    return res.data;
  },

  verifyQR: async (bookingId: number, qrCode: string): Promise<{ success: boolean; message: string }> => {
    const res = await api.post('/tracking/verify-qr', { booking_id: bookingId, qr_code: qrCode });
    return res.data;
  },
};
