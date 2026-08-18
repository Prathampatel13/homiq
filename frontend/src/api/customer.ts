import api from './axios';
import { CustomerAddress, User } from '../types';

export interface CustomerProfile extends User {
  city?: string;
  state?: string;
  postal_code?: string;
  preferred_language?: string;
  addresses?: CustomerAddress[];
}

export interface CustomerDashboardStats {
  total_bookings: number;
  completed_bookings: number;
  active_bookings: number;
  total_spent: number;
  saved_addresses_count: number;
  unread_notifications_count: number;
}

export const customerApi = {
  getProfile: async (): Promise<CustomerProfile> => {
    const response = await api.get<CustomerProfile>('/customer/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<CustomerProfile>): Promise<CustomerProfile> => {
    const response = await api.put<CustomerProfile>('/customer/profile', data);
    return response.data;
  },

  uploadAvatar: async (file: File): Promise<{ avatar_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ avatar_url: string }>('/customer/profile/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },

  getAddresses: async (): Promise<CustomerAddress[]> => {
    const response = await api.get<CustomerAddress[]>('/customer/addresses');
    return response.data;
  },

  getAddress: async (id: number): Promise<CustomerAddress> => {
    const response = await api.get<CustomerAddress>(`/customer/addresses/${id}`);
    return response.data;
  },

  createAddress: async (address: Omit<CustomerAddress, 'id' | 'customer_id'>): Promise<CustomerAddress> => {
    const response = await api.post<CustomerAddress>('/customer/addresses', address);
    return response.data;
  },

  updateAddress: async (id: number, address: Partial<CustomerAddress>): Promise<CustomerAddress> => {
    const response = await api.put<CustomerAddress>(`/customer/addresses/${id}`, address);
    return response.data;
  },

  setDefaultAddress: async (id: number): Promise<CustomerAddress> => {
    const response = await api.put<CustomerAddress>(`/customer/addresses/${id}/default`);
    return response.data;
  },

  deleteAddress: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/customer/addresses/${id}`);
    return response.data;
  },

  getDashboard: async (): Promise<CustomerDashboardStats> => {
    const response = await api.get<CustomerDashboardStats>('/customer/dashboard');
    return response.data;
  },
};
