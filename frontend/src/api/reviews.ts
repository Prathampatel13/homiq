import api from './axios';
import { Review } from '../types';

export const reviewsApi = {
  getReviews: async (params?: { offset?: number; limit?: number }): Promise<Review[] | { items: Review[]; total: number }> => {
    const response = await api.get<Review[] | { items: Review[]; total: number }>('/reviews/', { params });
    return response.data;
  },

  getReview: async (id: number): Promise<Review> => {
    const response = await api.get<Review>(`/reviews/${id}`);
    return response.data;
  },

  createReview: async (data: {
    booking_id: number;
    technician_id: number;
    rating: number;
    comment: string;
  }): Promise<Review> => {
    const response = await api.post<Review>('/reviews/', data);
    return response.data;
  },

  updateReview: async (id: number, data: { rating?: number; comment?: string }): Promise<Review> => {
    const response = await api.put<Review>(`/reviews/${id}`, data);
    return response.data;
  },

  getTechnicianReviews: async (technicianId: number): Promise<Review[]> => {
    const response = await api.get<Review[]>(`/reviews/technician/${technicianId}`);
    return response.data;
  },

  getTechnicianSummary: async (technicianId: number): Promise<{
    rating_avg: number;
    total_reviews: number;
    rating_breakdown?: Record<string, number>;
  }> => {
    const response = await api.get<{ rating_avg: number; total_reviews: number; rating_breakdown?: Record<string, number> }>(
      `/reviews/technician/${technicianId}/summary`
    );
    return response.data;
  },
};
