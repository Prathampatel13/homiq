import api from './axios';
import { CompanyProfile } from '../types';

export const companyApi = {
  getProfile: async (): Promise<CompanyProfile> => {
    const response = await api.get<CompanyProfile>('/company/profile');
    return response.data;
  },

  updateProfile: async (data: Partial<CompanyProfile>): Promise<CompanyProfile> => {
    const response = await api.put<CompanyProfile>('/company/profile', data);
    return response.data;
  },

  listCompanies: async (params?: { offset?: number; limit?: number }): Promise<CompanyProfile[]> => {
    const response = await api.get<CompanyProfile[]>('/company/', { params });
    return response.data;
  },
};
