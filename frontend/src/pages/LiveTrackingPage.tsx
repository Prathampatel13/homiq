import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowLeft, Navigation2, CheckCircle2 } from 'lucide-react';
import { bookingsApi } from '../api/bookings';
import { Booking } from '../types';
import { LoadingState } from '../components/ui/LoadingState';
import { LiveTrackingWidget } from '../components/ui/LiveTrackingWidget';
import { useRealTimeSync } from '../services/realtime';

export const LiveTrackingPage: React.FC = () => {
  const navigate = useNavigate();
  const [activeBooking, setActiveBooking] = useState<Booking | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchActiveBooking = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const res = await bookingsApi.getBookings({ limit: 20 });
      const bList = Array.isArray(res) ? res : (res as any)?.items || [];
      
      // Find the most recent active booking
      const active = bList.find((b: Booking) => 
        ['assigned', 'accepted', 'in_progress', 'arrived', 'start_trip', 'pending', 'confirmed', 'on_the_way'].includes(b.status)
      );
      
      setActiveBooking(active || null);
    } catch (err) {
      console.error('Failed to fetch active booking for tracking:', err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    fetchActiveBooking(false);
  }, []);

  // Real-time tracking synchronization
  useRealTimeSync(() => {
    fetchActiveBooking(true);
  }, 4000);

  if (loading) {
    return <LoadingState message="Locating active dispatch..." />;
  }

  return (
    <div className="min-h-screen bg-dark-950 py-10 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
        
        {/* Header */}
        <div className="flex items-center gap-4 pb-6 border-b border-dark-750">
          <button 
            onClick={() => navigate(-1)}
            className="p-2 rounded-xl bg-dark-900 border border-dark-800 hover:bg-dark-800 transition-colors text-slate-300 shrink-0"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2.5 h-2.5 rounded-full bg-sage-400 animate-pulse" />
              <span className="text-xs font-mono tracking-widest text-sage-400 uppercase">
                GPS LIVE TRACKING
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Dispatch Radar
            </h1>
          </div>
        </div>

        {/* Content */}
        {activeBooking ? (
          <LiveTrackingWidget booking={activeBooking} />
        ) : (
          <div className="p-12 mt-8 rounded-3xl bg-dark-900/60 border border-dark-750 text-center space-y-4">
            <div className="w-16 h-16 rounded-2xl bg-dark-850 border border-dark-750 flex items-center justify-center text-slate-400 mx-auto">
              <CheckCircle2 className="w-8 h-8 text-sage-400" />
            </div>
            <h3 className="text-xl font-bold text-white tracking-tight">NO ACTIVE DISPATCHES</h3>
            <p className="text-sm text-slate-400 max-w-md mx-auto leading-relaxed">
              You don't have any technicians currently en route. Book a service and track their live location here.
            </p>
            <button
              onClick={() => navigate('/booking/new')}
              className="btn-primary px-8 py-3 mt-4 text-sm shadow-subtle hover:shadow-metallic"
            >
              BOOK A SERVICE
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
