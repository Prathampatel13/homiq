import api from './axios';
import { User, UserRole } from '../types';

export interface LoginRequest {
  email?: string;
  phone?: string;
  password?: string;
  role?: UserRole;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  phone: string;
  password?: string;
  role: UserRole;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authApi = {
  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const res = await api.post('/auth/login', credentials);
    return res.data;
  },

  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    const res = await api.post('/auth/register', data);
    return res.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await api.get('/auth/me');
    return res.data;
  },
};
