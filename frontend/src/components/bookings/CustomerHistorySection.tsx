import React, { useEffect, useState } from 'react';
import { Booking } from '../../types';
import { technicianApi } from '../../api/technician';
import { StatusBadge } from '../ui/StatusBadge';
import { Calendar, History, Loader2, AlertCircle } from 'lucide-react';

export interface CustomerHistorySectionProps {
  customerId: number;
}

export const CustomerHistorySection: React.FC<CustomerHistorySectionProps> = ({ customerId }) => {
  const [history, setHistory] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (!expanded) return;

    const fetchHistory = async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await technicianApi.getCustomerHistory(customerId, { limit: 5 });
        setHistory(Array.isArray(res.items) ? res.items : []);
      } catch (err: any) {
        console.error('Failed to fetch customer history:', err);
        setError('Could not load history. You may not have permission.');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [customerId, expanded]);

  return (
    <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 mb-6">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full hover:opacity-80 transition-opacity"
      >
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-sage-600" />
          <span className="text-[11px] font-mono text-slate-700 uppercase tracking-wider font-bold">Customer History</span>
        </div>
        <span className="text-xs text-sage-600 font-semibold underline decoration-sage-300 underline-offset-2">
          {expanded ? 'Hide' : 'View Past Bookings'}
        </span>
      </button>

      {expanded && (
        <div className="mt-4 space-y-3 pt-4 border-t border-slate-200">
          {loading ? (
            <div className="flex items-center gap-2 text-xs text-slate-500 py-2 font-medium">
              <Loader2 className="w-4 h-4 animate-spin text-sage-600" />
              <span>Loading history...</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 text-xs text-rose-700 bg-rose-50 p-2 rounded-lg border border-rose-200">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-600" />
              <span>{error}</span>
            </div>
          ) : history.length === 0 ? (
            <p className="text-xs text-slate-500 italic py-2">No past bookings found for this customer.</p>
          ) : (
            <div className="space-y-2">
              {history.map((hJob) => (
                <div key={hJob.id} className="flex flex-col gap-2 p-3 rounded-xl bg-white border border-slate-200 shadow-subtle">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-slate-900">{hJob.service?.name || 'Service Order'}</span>
                    <StatusBadge status={hJob.status} size="sm" />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-500 font-mono">
                    <div className="flex items-center gap-1.5">
                      <Calendar className="w-3 h-3" />
                      <span>{new Date(hJob.booking_date).toLocaleDateString()}</span>
                    </div>
                    <span>#{hJob.booking_number || hJob.id}</span>
                  </div>
                </div>
              ))}
              {history.length >= 5 && (
                <p className="text-[10px] text-slate-500 text-center pt-2">Showing latest 5 bookings</p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
