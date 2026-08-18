import api from './axios';
import { Invoice, Payment } from '../types';

export interface RazorpayOrderResponse {
  id: string; // Razorpay order_id
  amount: number;
  currency: string;
  payment_id: number;
  key_id?: string;
}

export const paymentsApi = {
  createOrder: async (booking_id: number): Promise<RazorpayOrderResponse> => {
    const response = await api.post<RazorpayOrderResponse>('/payments/create-order', { booking_id });
    return response.data;
  },

  verifyPayment: async (data: {
    razorpay_order_id: string;
    razorpay_payment_id: string;
    razorpay_signature: string;
  }): Promise<{ message: string; status: string; payment_id?: number }> => {
    const response = await api.post<{ message: string; status: string; payment_id?: number }>('/payments/verify', data);
    return response.data;
  },

  getPayments: async (params?: { offset?: number; limit?: number }): Promise<Payment[]> => {
    const response = await api.get<Payment[]>('/payments/', { params });
    return response.data;
  },

  getPayment: async (id: number): Promise<Payment> => {
    const response = await api.get<Payment>(`/payments/${id}`);
    return response.data;
  },

  getHistory: async (): Promise<Payment[]> => {
    const response = await api.get<Payment[]>('/payments/history');
    return response.data;
  },

  getInvoiceByPayment: async (paymentId: number): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/payments/invoice/${paymentId}`);
    return response.data;
  },

  refundPayment: async (paymentId: number, reason?: string): Promise<{ message: string; status: string }> => {
    const response = await api.post<{ message: string; status: string }>(`/payments/${paymentId}/refund`, { reason });
    return response.data;
  },
};
