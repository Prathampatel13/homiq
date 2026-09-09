import React, { useState } from 'react';
import { 
  X, 
  Calendar, 
  Clock, 
  MapPin, 
  UserCheck, 
  ShieldCheck, 
  CreditCard, 
  Phone, 
  CheckCircle2,
  XCircle
} from 'lucide-react';
import { Booking } from '../../types';
import { StatusBadge } from '../ui/StatusBadge';
import { BookingMediaSection } from '../media/BookingMediaSection';
import { CustomerHistorySection } from '../bookings/CustomerHistorySection';
import { useAuthStore } from '../../store/useAuthStore';
import { bookingsApi } from '../../api/bookings';
import { triggerLocalSync } from '../../services/realtime';

export interface BookingDetailsModalProps {
  booking: Booking | null;
  isOpen: boolean;
  onClose: () => void;
  onOpenVerify?: () => void;
  onOpenPayment?: () => void;
  onOpenReview?: () => void;
  onBookingUpdated?: () => void;
}

export const BookingDetailsModal: React.FC<BookingDetailsModalProps> = ({
  booking,
  isOpen,
  onClose,
  onOpenVerify,
  onOpenPayment,
  onOpenReview,
  onBookingUpdated,
}) => {
  const { user } = useAuthStore();
  const [cancelling, setCancelling] = useState(false);
  if (!isOpen || !booking) return null;

  const getTechName = (tech: any) => {
    if (!tech) return 'Unassigned';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  const handleCancelBooking = async () => {
    if (!window.confirm('Are you sure you want to cancel this booking? This will remove the dispatch request.')) {
      return;
    }
    try {
      setCancelling(true);
      await bookingsApi.cancelBooking(booking.id, 'Cancelled by customer');
      triggerLocalSync();
      if (onBookingUpdated) {
        onBookingUpdated();
      }
      onClose();
    } catch (err: any) {
      alert(err?.response?.data?.detail || 'Failed to cancel booking. Please try again.');
    } finally {
      setCancelling(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-2xl rounded-3xl bg-white border border-slate-200 p-6 sm:p-8 shadow-modal text-slate-900 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 border border-slate-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-6 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-3">
              <h3 className="text-xl font-bold text-slate-900 tracking-tight">
                {booking.service?.name || 'Service Order'}
              </h3>
              <StatusBadge status={booking.status} size="sm" />
            </div>
            <p className="text-xs font-mono text-slate-500 mt-1">
              Booking Reference: #{booking.booking_number || booking.id}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xs text-slate-500 block">Total Amount</span>
            <span className="text-xl font-bold font-mono text-slate-900">
              ₹{(booking.final_price || booking.total_amount || booking.estimated_price || 0).toFixed(2)}
            </span>
          </div>
        </div>

        {/* Grid Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {/* Schedule */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="text-[11px] font-mono text-sage-700 uppercase tracking-wider block font-semibold">Schedule & Time</span>
            <div className="flex items-center gap-2 text-xs text-slate-700">
              <Calendar className="w-4 h-4 text-slate-500" />
              <span>{booking.booking_date ? new Date(booking.booking_date).toLocaleDateString(undefined, { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' }) : 'Scheduled'}</span>
            </div>
            {booking.preferred_time && (
              <div className="flex items-center gap-2 text-xs text-slate-700">
                <Clock className="w-4 h-4 text-slate-500" />
                <span>Slot: {booking.preferred_time}</span>
              </div>
            )}
          </div>

          {/* Service Location */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="text-[11px] font-mono text-sage-700 uppercase tracking-wider block font-semibold">Service Address</span>
            <div className="flex items-start gap-2 text-xs text-slate-700">
              <MapPin className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
              <span>
                {booking.address 
                  ? `${booking.address.house_no}, ${booking.address.area}, ${booking.address.city || ''}` 
                  : 'Address details on record'}
              </span>
            </div>
          </div>

          {/* Assigned Technician */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="text-[11px] font-mono text-sage-700 uppercase tracking-wider block font-semibold">Assigned Master Tech</span>
            {booking.technician ? (
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2.5">
                  <div className="w-8 h-8 rounded-lg bg-sage-100 border border-sage-200 flex items-center justify-center text-sage-800 text-xs font-bold">
                    {getTechName(booking.technician).charAt(0)}
                  </div>
                  <div>
                    <p className="text-xs font-semibold text-slate-900">{getTechName(booking.technician)}</p>
                    <span className="text-[10px] font-mono text-slate-500">Verified Professional</span>
                  </div>
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">Dispatching certified specialist for your area...</p>
            )}
          </div>

          {/* Live Fulfillment State */}
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 space-y-2">
            <span className="text-[11px] font-mono text-sage-700 uppercase tracking-wider block font-semibold">Service State</span>
            <div className="flex items-center justify-between">
              <span className="text-xs text-slate-800 capitalize font-semibold">
                {booking.status === 'arrived' ? 'Technician Arrived' : booking.status === 'in_progress' ? 'Service Ongoing' : booking.status}
              </span>
              <StatusBadge status={booking.status} size="sm" />
            </div>
            
            <div className="border-t border-slate-200 pt-2 mt-2 flex items-center justify-between">
              <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block">Payment</span>
              <span className={`text-xs font-semibold uppercase ${booking.payment_status === 'paid' ? 'text-emerald-600' : booking.payment_status === 'refunded' ? 'text-orange-600' : 'text-amber-600'}`}>
                {booking.payment_status || 'PENDING'}
              </span>
            </div>
          </div>
        </div>

        {/* Customer Notes if present */}
        {booking.customer_note && (
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 mb-6">
            <span className="text-[11px] font-mono text-slate-500 uppercase block mb-1 font-semibold">Special Instructions</span>
            <p className="text-xs text-slate-700">{booking.customer_note}</p>
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
        <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-slate-100">
          {/* Cancel Booking Action for Customer */}
          {['pending', 'assigned', 'accepted', 'arrived', 'on_the_way'].includes(booking.status) ? (
            <button
              onClick={handleCancelBooking}
              disabled={cancelling}
              className="px-4 py-2.5 rounded-xl text-xs bg-rose-50 hover:bg-rose-100 text-rose-700 border border-rose-200 font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <XCircle className="w-4 h-4" />
              <span>{cancelling ? 'Cancelling...' : 'Cancel Booking'}</span>
            </button>
          ) : <div />}

          <div className="flex items-center gap-3">
            {onOpenPayment && ['confirmed', 'in_progress'].includes(booking.status) && booking.payment_status !== 'paid' && (
              <button
                onClick={() => {
                  onClose();
                  onOpenPayment();
                }}
                className="btn-primary text-xs px-4 py-2.5 flex items-center gap-1.5 font-semibold"
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
                <CheckCircle2 className="w-4 h-4 text-sage-600" />
                <span>Leave Review</span>
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
    </div>
  );
};
