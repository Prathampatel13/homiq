import api from './axios';
import { Service, ServiceCategory } from '../types';

export const servicesApi = {
  getCategories: async (params?: { offset?: number; limit?: number; _t?: number }): Promise<ServiceCategory[]> => {
    const response = await api.get<ServiceCategory[]>('/services/categories', { params: { ...params, _t: Date.now() } });
    return response.data;
  },

  getCategory: async (id: number): Promise<ServiceCategory> => {
    const response = await api.get<ServiceCategory>(`/services/categories/${id}`);
    return response.data;
  },

  createCategory: async (data: Omit<ServiceCategory, 'id'>): Promise<ServiceCategory> => {
    const response = await api.post<ServiceCategory>('/services/categories', data);
    return response.data;
  },

  updateCategory: async (id: number, data: Partial<ServiceCategory>): Promise<ServiceCategory> => {
    const response = await api.put<ServiceCategory>(`/services/categories/${id}`, data);
    return response.data;
  },

  deleteCategory: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/services/categories/${id}`);
    return response.data;
  },

  getServices: async (params?: {
    category_id?: number;
    min_price?: number;
    max_price?: number;
    search?: string;
    offset?: number;
    limit?: number;
    _t?: number;
  }): Promise<Service[]> => {
    const response = await api.get('/services/', { params: { ...params, _t: Date.now() } });
    return response.data;
  },

  getService: async (id: number): Promise<Service> => {
    const response = await api.get<Service>(`/services/${id}`);
    return response.data;
  },

  createService: async (data: Omit<Service, 'id'>): Promise<Service> => {
    const response = await api.post<Service>('/services/', data);
    return response.data;
  },

  updateService: async (id: number, data: Partial<Service>): Promise<Service> => {
    const response = await api.put<Service>(`/services/${id}`, data);
    return response.data;
  },

  deleteService: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/services/${id}`);
    return response.data;
  },

  uploadImage: async (serviceId: number, file: File): Promise<{ image_url: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post<{ image_url: string }>(`/services/${serviceId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  },
};
