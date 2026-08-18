import api from './axios';
import { JobApplication, JobPost } from '../types';

export const jobsApi = {
  getJobs: async (params?: { offset?: number; limit?: number; search?: string }): Promise<JobPost[]> => {
    const response = await api.get<JobPost[]>('/jobs/', { params });
    return response.data;
  },

  getMyJobs: async (): Promise<JobPost[]> => {
    const response = await api.get<JobPost[]>('/jobs/my');
    return response.data;
  },

  getJob: async (id: number): Promise<JobPost> => {
    const response = await api.get<JobPost>(`/jobs/${id}`);
    return response.data;
  },

  createJob: async (data: {
    title: string;
    description: string;
    requirements?: string;
    location?: string;
    salary_range?: string;
    is_active?: boolean;
  }): Promise<JobPost> => {
    const response = await api.post<JobPost>('/jobs/', data);
    return response.data;
  },

  updateJob: async (id: number, data: Partial<JobPost>): Promise<JobPost> => {
    const response = await api.put<JobPost>(`/jobs/${id}`, data);
    return response.data;
  },

  deleteJob: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/jobs/${id}`);
    return response.data;
  },

  applyJob: async (jobId: number, cover_letter?: string): Promise<JobApplication> => {
    const response = await api.post<JobApplication>(`/jobs/${jobId}/apply`, { cover_letter });
    return response.data;
  },

  getJobApplications: async (jobId: number): Promise<JobApplication[]> => {
    const response = await api.get<JobApplication[]>(`/jobs/${jobId}/applications`);
    return response.data;
  },

  getMyApplications: async (): Promise<JobApplication[]> => {
    const response = await api.get<JobApplication[]>('/jobs/applications/my');
    return response.data;
  },

  updateApplicationStatus: async (applicationId: number, status: string): Promise<JobApplication> => {
    const response = await api.put<JobApplication>(`/jobs/applications/${applicationId}/status`, { status });
    return response.data;
  },
};
