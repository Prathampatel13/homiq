import api from './axios';
import { User } from '../types';

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  login: async (credentials: { email: string; password: string }): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', credentials);
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

  resetPassword: async (token: string, new_password: string): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/auth/reset-password', {
      token,
      new_password,
    });
    return response.data;
  },
};
