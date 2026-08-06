import api from './axios';
import { ServiceCategory, Service } from '../types';

export const servicesApi = {
  getCategories: async (): Promise<ServiceCategory[]> => {
    const res = await api.get('/services/categories');
    return res.data;
  },

  getServices: async (categoryId?: number): Promise<Service[]> => {
    const params = categoryId ? { category_id: categoryId } : {};
    const res = await api.get('/services/', { params });
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.items || []);
    return rawList.map((item: any) => ({
      ...item,
      price: item.price !== undefined ? item.price : (item.base_price || 499),
      rating_avg: item.rating_avg !== undefined ? item.rating_avg : 4.8,
      total_reviews: item.total_reviews !== undefined ? item.total_reviews : 42,
    }));
  },

  getServiceById: async (id: number): Promise<Service> => {
    const res = await api.get(`/services/${id}`);
    return res.data;
  },

  searchServices: async (query: string): Promise<Service[]> => {
    const res = await api.get('/search/services', { params: { query } });
    const rawList = Array.isArray(res.data) ? res.data : (res.data?.items || []);
    return rawList.map((item: any) => ({
      ...item,
      price: item.price !== undefined ? item.price : (item.base_price || 499),
      rating_avg: item.rating_avg !== undefined ? item.rating_avg : 4.8,
      total_reviews: item.total_reviews !== undefined ? item.total_reviews : 42,
    }));
  },
};
