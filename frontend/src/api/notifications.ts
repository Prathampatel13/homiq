import api from './axios';
import { NotificationItem } from '../types';

export const notificationsApi = {
  getNotifications: async (params?: { offset?: number; limit?: number }): Promise<NotificationItem[] | { items: NotificationItem[]; total: number }> => {
    const response = await api.get<NotificationItem[] | { items: NotificationItem[]; total: number }>('/notifications/', { params });
    return response.data;
  },

  getUnread: async (): Promise<{ unread_count: number; notifications: NotificationItem[] }> => {
    const response = await api.get<{ unread_count: number; notifications: NotificationItem[] }>('/notifications/unread');
    return response.data;
  },

  markRead: async (id: number): Promise<NotificationItem> => {
    const response = await api.patch<NotificationItem>(`/notifications/${id}/read`);
    return response.data;
  },

  markAllRead: async (): Promise<{ message: string }> => {
    const response = await api.put<{ message: string }>('/notifications/read-all');
    return response.data;
  },

  readMultiple: async (notification_ids: number[]): Promise<{ message: string }> => {
    const response = await api.post<{ message: string }>('/notifications/read-multiple', { notification_ids });
    return response.data;
  },

  deleteNotification: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/notifications/${id}`);
    return response.data;
  },
};
