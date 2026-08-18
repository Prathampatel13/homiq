import api from './axios';
import { Booking, Service, TechnicianProfile } from '../types';

export interface SearchResults {
  services: Service[];
  technicians: TechnicianProfile[];
  bookings?: Booking[];
  total_results?: number;
}

export const searchApi = {
  searchGlobal: async (q: string): Promise<SearchResults> => {
    const response = await api.get<SearchResults>(`/search?q=${encodeURIComponent(q)}`);
    return response.data;
  },

  searchServices: async (q: string, sort_by?: string): Promise<Service[]> => {
    const response = await api.get<Service[]>(`/search/services?q=${encodeURIComponent(q)}${sort_by ? `&sort_by=${sort_by}` : ''}`);
    return response.data;
  },

  searchTechnicians: async (params?: { city?: string; query?: string; sort_by?: string }): Promise<TechnicianProfile[]> => {
    const response = await api.get<TechnicianProfile[]>('/search/technicians', { params });
    return response.data;
  },

  searchBookings: async (q?: string): Promise<Booking[]> => {
    const response = await api.get<Booking[]>('/search/bookings', { params: q ? { q } : undefined });
    return response.data;
  },

  getSuggestions: async (q: string): Promise<string[]> => {
    const response = await api.get<string[]>(`/search/suggestions?q=${encodeURIComponent(q)}`);
    return response.data;
  },

  getRecent: async (): Promise<string[]> => {
    const response = await api.get<string[]>('/search/recent');
    return response.data;
  },

  getRecommendations: async (): Promise<{ services: Service[]; technicians: TechnicianProfile[] }> => {
    const response = await api.get<{ services: Service[]; technicians: TechnicianProfile[] }>('/recommendations');
    return response.data;
  },
};

export const chatApi = {
  getHistory: async (bookingId: number): Promise<any[]> => {
    const response = await api.get<any[]>(`/chat/${bookingId}/history`);
    return response.data;
  },
};
