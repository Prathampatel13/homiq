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
    <div className="p-4 rounded-2xl bg-dark-850/50 border border-dark-750 mb-6">
      <button 
        onClick={() => setExpanded(!expanded)}
        className="flex items-center justify-between w-full hover:opacity-80 transition-opacity"
      >
        <div className="flex items-center gap-2">
          <History className="w-4 h-4 text-sage-400" />
          <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider">Customer History</span>
        </div>
        <span className="text-xs text-slate-500 font-mono underline decoration-slate-700 underline-offset-2">
          {expanded ? 'Hide' : 'View Past Bookings'}
        </span>
      </button>

      {expanded && (
        <div className="mt-4 space-y-3 pt-4 border-t border-dark-750/50">
          {loading ? (
            <div className="flex items-center gap-2 text-xs text-slate-400 py-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading history...</span>
            </div>
          ) : error ? (
            <div className="flex items-center gap-2 text-xs text-rose-400/80 bg-rose-500/10 p-2 rounded-lg border border-rose-500/20">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{error}</span>
            </div>
          ) : history.length === 0 ? (
            <p className="text-xs text-slate-400 italic py-2">No past bookings found for this customer.</p>
          ) : (
            <div className="space-y-2">
              {history.map((hJob) => (
                <div key={hJob.id} className="flex flex-col gap-2 p-3 rounded-xl bg-dark-900 border border-dark-750">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-semibold text-white">{hJob.service?.name || 'Service Order'}</span>
                    <StatusBadge status={hJob.status} size="sm" />
                  </div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
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
