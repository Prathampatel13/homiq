import api from './axios';
import { Invoice } from '../types';

export const invoicesApi = {
  getInvoices: async (params?: { offset?: number; limit?: number }): Promise<Invoice[] | { items: Invoice[]; total: number }> => {
    const response = await api.get<Invoice[] | { items: Invoice[]; total: number }>('/invoices/', { params });
    return response.data;
  },

  getInvoice: async (id: number): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/invoices/${id}`);
    return response.data;
  },

  getInvoiceByNumber: async (invoiceNumber: string): Promise<Invoice> => {
    const response = await api.get<Invoice>(`/invoices/number/${invoiceNumber}`);
    return response.data;
  },

  createInvoice: async (data: {
    booking_id: number;
    subtotal: number;
    discount_amount?: number;
    tax_percentage?: number;
    total_amount: number;
    amount_paid?: number;
    notes?: string;
  }): Promise<Invoice> => {
    const response = await api.post<Invoice>('/invoices/', data);
    return response.data;
  },

  updateInvoice: async (id: number, data: Partial<Invoice>): Promise<Invoice> => {
    const response = await api.put<Invoice>(`/invoices/${id}`, data);
    return response.data;
  },

  issueInvoice: async (id: number): Promise<Invoice> => {
    const response = await api.post<Invoice>(`/invoices/${id}/issue`);
    return response.data;
  },
};
