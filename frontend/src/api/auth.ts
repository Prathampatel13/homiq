import api from './axios';
import { User } from '../types';

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  login: async (credentials: { identifier: string; password: string }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  },

  googleLogin: async (payload: { token: string; role?: string }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/google', payload);
    return response.data;
  },

  register: async (payload: {
    email: string;
    password: string;
    full_name: string;
    phone?: string;
    role?: 'customer' | 'technician' | 'company' | string;
  }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/register', payload);
    return response.data;
  },

  refreshToken: async (token: string): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>(`/auth/refresh?refresh_token=${encodeURIComponent(token)}`);
    return response.data;
  },

  getMe: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },

  forgotPassword: async (email: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/forgot-password', { email });
    return response.data;
  },

  sendResetOtp: async (email: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/send-reset-otp', { email });
    return response.data;
  },

  verifyResetOtp: async (email: string, otp: string): Promise<{ reset_token: string; message: string }> => {
    const response = await api.post<{ reset_token: string; message: string }>('/auth/verify-reset-otp', { email, otp });
    return response.data;
  },

  resetPassword: async (token: string, new_password: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password,
    });
    return response.data;
  },
};
