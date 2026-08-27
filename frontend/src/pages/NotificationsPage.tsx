import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Bell, CheckCircle2, Circle, ArrowLeft, Trash2, Clock } from 'lucide-react';
import { notificationsApi } from '../api/notifications';
import { NotificationItem } from '../types';

export const NotificationsPage: React.FC = () => {
  const navigate = useNavigate();
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchNotifications = async () => {
    try {
      setIsLoading(true);
      const res = await notificationsApi.getNotifications({ limit: 100 });
      const items = Array.isArray(res) ? res : res.items;
      setNotifications(items);
    } catch (err) {
      console.error('Failed to fetch notifications', err);
      setError('Failed to load notifications. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkAllRead = async () => {
    try {
      await notificationsApi.markAllRead();
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
    } catch (err) {
      console.error('Failed to mark all as read', err);
    }
  };

  const handleMarkRead = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (err) {
      console.error('Failed to mark as read', err);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await notificationsApi.deleteNotification(id);
      setNotifications(prev => prev.filter(n => n.id !== id));
    } catch (err) {
      console.error('Failed to delete notification', err);
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins || 1} mins ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays === 1) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex items-center gap-4 mb-8">
        <button 
          onClick={() => navigate(-1)}
          className="p-2 rounded-xl bg-dark-900 border border-dark-800 hover:bg-dark-800 transition-colors text-slate-300"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">All Notifications</h1>
          <p className="text-sm text-slate-400 mt-1">View all your alerts, booking updates, and messages</p>
        </div>
      </div>

      <div className="bg-dark-900 rounded-3xl border border-dark-800 overflow-hidden shadow-card">
        <div className="flex items-center justify-between p-4 sm:p-6 border-b border-dark-800 bg-dark-950/50">
          <div className="flex items-center gap-2">
            <Bell className="w-5 h-5 text-sage-400" />
            <h2 className="text-base font-bold text-white">Inbox</h2>
          </div>
          {notifications.some(n => !n.is_read) && (
            <button 
              onClick={handleMarkAllRead}
              className="text-xs font-semibold text-sage-400 hover:text-sage-300 transition-colors flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4" />
              Mark all as read
            </button>
          )}
        </div>

        <div className="divide-y divide-dark-800">
          {isLoading ? (
            <div className="p-8 text-center text-slate-400 text-sm">Loading notifications...</div>
          ) : error ? (
            <div className="p-8 text-center text-rose-400 text-sm">{error}</div>
          ) : notifications.length === 0 ? (
            <div className="p-12 text-center flex flex-col items-center">
              <div className="w-16 h-16 rounded-full bg-dark-800 flex items-center justify-center mb-4">
                <Bell className="w-6 h-6 text-slate-500" />
              </div>
              <h3 className="text-lg font-bold text-white mb-2">No notifications</h3>
              <p className="text-sm text-slate-400">You're all caught up! New updates will appear here.</p>
            </div>
          ) : (
            notifications.map((notification) => (
              <div 
                key={notification.id} 
                className={`p-4 sm:p-6 transition-colors group ${
                  notification.is_read ? 'bg-dark-900' : 'bg-dark-850 hover:bg-dark-800'
                }`}
              >
                <div className="flex gap-4 sm:gap-6">
                  <div className="shrink-0 mt-1">
                    {notification.is_read ? (
                      <Circle className="w-2.5 h-2.5 text-dark-600 fill-current" />
                    ) : (
                      <div className="w-2.5 h-2.5 rounded-full bg-sage-400 shadow-[0_0_8px_rgba(74,222,128,0.5)]" />
                    )}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2 mb-1">
                      <h4 className={`text-base font-semibold truncate ${
                        notification.is_read ? 'text-slate-300' : 'text-white'
                      }`}>
                        {notification.title}
                      </h4>
                      <span className="text-xs font-mono text-slate-500 flex items-center gap-1 shrink-0">
                        <Clock className="w-3.5 h-3.5" />
                        {formatDate(notification.created_at)}
                      </span>
                    </div>
                    <p className={`text-sm leading-relaxed ${
                      notification.is_read ? 'text-slate-500' : 'text-slate-300'
                    }`}>
                      {notification.message}
                    </p>
                    
                    {!notification.is_read && (
                      <button 
                        onClick={() => handleMarkRead(notification.id)}
                        className="mt-3 text-xs font-semibold text-sage-400 hover:text-sage-300"
                      >
                        Mark as read
                      </button>
                    )}
                  </div>

                  <button 
                    onClick={() => handleDelete(notification.id)}
                    className="shrink-0 text-slate-600 hover:text-rose-400 opacity-0 group-hover:opacity-100 transition-all p-2 rounded-lg hover:bg-rose-500/10"
                    title="Delete notification"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
