import React, { useEffect, useState } from 'react';
import { bookingsApi } from '../api/bookings';
import { technicianApi } from '../api/technician';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole, Booking } from '../types';
import { Clock, Calendar, MapPin, User, CheckCircle2, AlertCircle } from 'lucide-react';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { StatusBadge } from '../components/ui/StatusBadge';

export const HistoryPage: React.FC = () => {
  const { user, getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();
  const [history, setHistory] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        setLoading(true);
        if (role === UserRole.TECHNICIAN) {
          const res = await technicianApi.getHistory();
          // Filter to show only completed or cancelled (historical) if getHistory returns everything
          // Backend get_history endpoint usually filters by completed/cancelled
          setHistory(Array.isArray(res) ? res : ((res as any)?.items || []));
        } else if (role === UserRole.CUSTOMER) {
          const res = await bookingsApi.getBookings();
          // Customers might want to see only past bookings in history
          const allBookings = Array.isArray(res) ? res : ((res as any)?.items || []);
          const pastBookings = allBookings.filter((b: Booking) => ['completed', 'cancelled'].includes(b.status));
          setHistory(pastBookings);
        } else {
          // Fallback
          const res = await bookingsApi.getBookings();
          setHistory(Array.isArray(res) ? res : ((res as any)?.items || []));
        }
      } catch (err) {
        console.error('Failed to fetch history:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [role]);

  if (loading) return <LoadingState message="Loading History..." />;

  return (
    <div className="min-h-screen bg-dark-950 py-8 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Service History</h1>
          <p className="text-sm text-slate-400 mt-1">
            {role === UserRole.TECHNICIAN 
              ? 'View your past completed and cancelled service jobs.'
              : 'View your past service bookings.'}
          </p>
        </div>

        {history.length === 0 ? (
          <EmptyState
            title="No History Found"
            description="You don't have any completed or past services yet."
            icon={Clock}
          />
        ) : (
          <div className="space-y-4">
            {history.map((job) => (
              <div 
                key={job.id} 
                className="p-6 rounded-3xl bg-dark-900 border border-dark-750 hover:border-dark-700 transition-colors shadow-card flex flex-col md:flex-row md:items-center justify-between gap-6"
              >
                <div className="space-y-3 flex-1">
                  <div className="flex items-center gap-3">
                    <span className="text-base font-bold text-white">
                      {job.service?.name || 'Service Booking'}
                    </span>
                    <StatusBadge status={job.status} size="sm" />
                  </div>
                  
                  <div className="flex flex-col sm:flex-row sm:items-center gap-3 text-xs text-slate-400 font-mono">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3.5 h-3.5" />
                      <span>{job.booking_date ? new Date(job.booking_date).toLocaleDateString() : 'N/A'}</span>
                    </div>
                    <div className="hidden sm:block text-slate-600">•</div>
                    <div className="flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{job.preferred_time || 'N/A'}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 text-xs text-slate-300 pt-1">
                    <User className="w-3.5 h-3.5 text-sage-400 shrink-0" />
                    <span className="font-semibold">
                      {role === UserRole.TECHNICIAN ? (job.customer?.full_name || 'Customer') : ((job.technician as any)?.full_name || (job.technician as any)?.user?.full_name || 'Technician')}
                    </span>
                  </div>
                </div>

                <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-2 pt-4 md:pt-0 border-t md:border-t-0 border-dark-800">
                  <span className="text-xs text-slate-400 font-mono uppercase">
                    {role === UserRole.TECHNICIAN ? 'Earned' : 'Paid'}
                  </span>
                  <span className="text-xl font-bold text-white font-mono">
                    ₹{((job.final_price || job.total_amount || job.estimated_price || 0) * (role === UserRole.TECHNICIAN ? 0.8 : 1)).toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
