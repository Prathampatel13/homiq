import React from 'react';
import { 
  X, 
  Calendar, 
  Clock, 
  MapPin, 
  UserCheck, 
  ShieldCheck, 
  CreditCard, 
  Phone, 
  CheckCircle2
} from 'lucide-react';
import { Booking } from '../../types';
import { StatusBadge } from '../ui/StatusBadge';
import { BookingMediaSection } from '../media/BookingMediaSection';
import { CustomerHistorySection } from '../bookings/CustomerHistorySection';
import { useAuthStore } from '../../store/useAuthStore';

export interface BookingDetailsModalProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
  onOpenVerify?: () => void;
  onOpenPayment?: () => void;
  onOpenReview?: () => void;
}

export const BookingDetailsModal: React.FC<BookingDetailsModalProps> = ({
  booking,
  isOpen,
  onClose,
  onOpenVerify,
  onOpenPayment,
  onOpenReview,
}) => {
  const { user } = useAuthStore();
  if (!isOpen || !booking) return null;

  const getTechName = (tech: any) => {
    if (!tech) return 'Unassigned';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-6 border-b border-dark-750">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-bold text-white tracking-tight">
                {booking.service?.name || 'Service Order'}
              </h3>
              <StatusBadge status={booking.status} size="sm" />
            </div>
            <p className="text-xs font-mono text-slate-400 mt-1">
              Booking Reference: #{booking.booking_number || booking.id}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-400 block">Total Amount</span>
            <span className="text-xl font-bold font-mono text-white">
              ₹{(booking.final_price || booking.total_amount || booking.estimated_price || 0).toFixed(2)}
            </span>
          </div>
        </div>

        {/* Grid Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Schedule */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-2">
            <span className="text-[11px] font-mono text-sage-400 uppercase tracking-wider block">Schedule & Time</span>
            <div className="flex items-center gap-2 text-xs text-slate-200">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span>{booking.booking_date ? new Date(booking.booking_date).toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }) : 'Scheduled'}</span>
            </div>
            {booking.preferred_time && (
              <div className="flex items-center gap-2 text-xs text-slate-200">
                <Clock className="w-4 h-4 text-slate-400" />
                <span>Slot: {booking.preferred_time}</span>
              </div>
            )}
          </div>

          {/* Service Location */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-2">
            <span className="text-[11px] font-mono text-sage-400 uppercase tracking-wider block">Service Address</span>
            <div className="flex items-start gap-2 text-xs text-slate-200">
              <MapPin className="w-4 h-4 text-slate-400 shrink-0 mt-0.5" />
              <span>
                {booking.address 
                  ? `${booking.address.house_no}, ${booking.address.area}, ${booking.address.city || ''}` 
                  : 'Address details unavailable (Please refresh)'}
              </span>
            </div>
          </div>

          {/* Assigned Technician */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-2">
            <span className="text-[11px] font-mono text-sage-400 uppercase tracking-wider block">Assigned Master Tech</span>
            {booking.technician ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 text-xs font-bold">
                    {getTechName(booking.technician).charAt(0)}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-white">{getTechName(booking.technician)}</p>
                    <span className="text-[10px] font-mono text-slate-400">Verified Professional</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">Dispatching certified specialist for your area...</p>
            )}
          </div>

          {/* SmartVerify Token Status */}
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-2">
            <span className="text-[11px] font-mono text-sage-400 uppercase tracking-wider block">Security Protocol</span>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-slate-200">
                <ShieldCheck className="w-4 h-4 text-sage-400" />
                <span>SmartVerify Handshake</span>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                Active
              </span>
            </div>
          </div>
        </div>

        {/* Customer Notes if present */}
        {booking.customer_note && (
          <div className="p-4 rounded-2xl bg-dark-850/50 border border-dark-750 mb-6">
            <span className="text-[11px] font-mono text-slate-400 uppercase block mb-1">Special Instructions</span>
            <p className="text-xs text-slate-300">{booking.customer_note}</p>
          </div>
        )}

        {/* Customer History (Only for Tech/Admin) */}
        {(user?.role === 'technician' || user?.role === 'admin') && booking.customer && (
          <CustomerHistorySection customerId={booking.customer.id || booking.customer_id || (booking.customer as any).user_id} />
        )}

        {/* ── SERVICE MEDIA & SITE EVIDENCE (Before/After Photos) ── */}
        <BookingMediaSection 
          bookingId={booking.id} 
          assignedTechnicianId={(booking.technician as any)?.user_id || (booking.technician as any)?.id} 
        />


        {/* Action Buttons */}
        <div className="flex flex-wrap items-center justify-end gap-3 pt-4 border-t border-dark-750">
          {onOpenVerify && ['assigned', 'accepted', 'in_progress', 'arrived', 'on_the_way'].includes(booking.status) && (
            <button
              onClick={() => {
                onClose();
                onOpenVerify();
              }}
              className="btn-accent text-xs px-4 py-2.5 flex items-center gap-1.5"
            >
              <ShieldCheck className="w-4 h-4" />
              <span>SmartVerify Handshake</span>
            </button>
          )}

          {onOpenPayment && (
            <button
              onClick={() => {
                onClose();
                onOpenPayment();
              }}
              className="btn-primary text-xs px-4 py-2.5 flex items-center gap-1.5"
            >
              <CreditCard className="w-4 h-4" />
              <span>Pay Now</span>
            </button>
          )}

          {onOpenReview && booking.status === 'completed' && (
            <button
              onClick={() => {
                onClose();
                onOpenReview();
              }}
              className="btn-secondary text-xs px-4 py-2.5 flex items-center gap-1.5"
            >
              <CheckCircle2 className="w-4 h-4 text-sage-400" />
              <span>Leave Workmanship Review</span>
            </button>
          )}

          <button
            onClick={onClose}
            className="btn-secondary text-xs px-4 py-2.5"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
