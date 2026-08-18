import api from './axios';
import { Coupon } from '../types';

export interface CouponValidationResult {
  is_valid: boolean;
  code: string;
  discount_amount: number;
  final_amount: number;
  message?: string;
}

export const couponsApi = {
  getCoupons: async (): Promise<Coupon[] | { items: Coupon[]; total: number }> => {
    const response = await api.get<Coupon[] | { items: Coupon[]; total: number }>('/coupons/');
    return response.data;
  },

  getCoupon: async (id: number): Promise<Coupon> => {
    const response = await api.get<Coupon>(`/coupons/${id}`);
    return response.data;
  },

  getCouponByCode: async (code: string): Promise<Coupon> => {
    const response = await api.get<Coupon>(`/coupons/code/${code}`);
    return response.data;
  },

  validateCoupon: async (code: string, amount: number, booking_id?: number): Promise<CouponValidationResult> => {
    const response = await api.post<CouponValidationResult>('/coupons/validate', {
      code,
      amount,
      booking_id,
    });
    return response.data;
  },

  applyCoupon: async (code: string, amount: number, booking_id: number): Promise<CouponValidationResult> => {
    const response = await api.post<CouponValidationResult>('/coupons/apply', {
      code,
      amount,
      booking_id,
    });
    return response.data;
  },

  createCoupon: async (data: Omit<Coupon, 'id'>): Promise<Coupon> => {
    const response = await api.post<Coupon>('/coupons/', data);
    return response.data;
  },

  updateCoupon: async (id: number, data: Partial<Coupon>): Promise<Coupon> => {
    const response = await api.put<Coupon>(`/coupons/${id}`, data);
    return response.data;
  },

  deleteCoupon: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/coupons/${id}`);
    return response.data;
  },
};
