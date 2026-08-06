import api from './axios';
import { Review } from '../types';

export interface CreateReviewPayload {
  booking_id: number;
  rating: number;
  comment: string;
}

export const reviewsApi = {
  createReview: async (payload: CreateReviewPayload): Promise<Review> => {
    const res = await api.post('/reviews/', payload);
    return res.data;
  },

  getTechnicianReviews: async (technicianId: number): Promise<Review[]> => {
    const res = await api.get(`/reviews/technician/${technicianId}`);
    return res.data;
  },

  getServiceReviews: async (serviceId: number): Promise<Review[]> => {
    const res = await api.get(`/reviews/service/${serviceId}`);
    return res.data;
  },
};
