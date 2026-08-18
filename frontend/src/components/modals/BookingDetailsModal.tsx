import React, { useState, useEffect } from 'react';
import { Calendar, Clock, MapPin, Phone, User, ShieldCheck, FileText, QrCode, Star, AlertTriangle, CheckCircle2 } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { StatusBadge } from '../ui/StatusBadge';
import { Booking, BookingStatusLog } from '../../types';
import { bookingsApi } from '../../api/bookings';
import { SmartVerifyModal } from './SmartVerifyModal';
import { ReviewModal } from './ReviewModal';
import { PaymentModal } from './PaymentModal';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';

interface BookingDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: Booking | null;
  onBookingUpdated?: () => void;
}

export const BookingDetailsModal: React.FC<BookingDetailsModalProps> = ({
  isOpen,
  onClose,
  booking,
  onBookingUpdated,
}) => {
  const toast = useToast();
  const [logs, setLogs] = useState<BookingStatusLog[]>([]);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);
  const [isReviewModalOpen, setIsReviewModalOpen] = useState(false);
  const [isPaymentModalOpen, setIsPaymentModalOpen] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);

  useEffect(() => {
    if (isOpen && booking?.id) {
      bookingsApi
        .getHistoryLogs(booking.id)
        .then(setLogs)
        .catch(() => setLogs([]));
    }
  }, [isOpen, booking?.id]);

  if (!booking) return null;

  const handleCancelBooking = async () => {
    if (!window.confirm('Are you sure you wish to cancel this booking?')) return;
    setIsCancelling(true);
    try {
      await bookingsApi.cancelBooking(booking.id, 'Cancelled by customer via portal');
      toast.success('Booking Cancelled', 'Your service has been cancelled.');
      if (onBookingUpdated) onBookingUpdated();
      onClose();
    } catch (err) {
      toast.error('Could not cancel', extractErrorMessage(err));
    } finally {
      setIsCancelling(false);
    }
  };

  const status = String(booking.status).toLowerCase();
  const canVerify = ['accepted', 'on_the_way', 'arrived', 'waiting_qr'].includes(status);
  const canReview = status === 'completed';
  const canCancel = ['pending', 'assigned', 'accepted'].includes(status);

  return (
    <>
      <Modal
        isOpen={isOpen}
        onClose={onClose}
        title={`Booking #${booking.booking_number || booking.id}`}
        description={`Scheduled for ${booking.booking_date} at ${booking.preferred_time}`}
        maxWidth="2xl"
      >
        <div className="space-y-6">
          {/* Header Status & Price Banner */}
          <div className="flex flex-wrap items-center justify-between gap-3 p-4 bg-dark-850 border border-dark-750 rounded-2xl">
            <div className="flex items-center gap-3">
              <StatusBadge status={booking.status} />
              <span className="text-xs text-slate-400">
                Created on {new Date(booking.created_at).toLocaleDateString()}
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block">Total Amount</span>
              <span className="text-lg font-bold text-white font-mono">
                ₹{(booking.final_price || booking.base_price || booking.estimated_price || 0).toFixed(2)}
              </span>
            </div>
          </div>

          {/* Service & Address Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Service card */}
            <div className="p-4 bg-dark-900 border border-dark-750/80 rounded-xl space-y-2">
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Service</h5>
              <p className="text-sm font-bold text-white">{booking.service?.name || 'Home Maintenance Service'}</p>
              <p className="text-xs text-slate-400 line-clamp-2">
                {booking.service?.description || 'Standard high-reliability maintenance service.'}
              </p>
              {booking.customer_note && (
                <div className="mt-2 pt-2 border-t border-dark-800 text-xs text-slate-300">
                  <span className="font-semibold text-slate-400">Special Instructions:</span> {booking.customer_note}
                </div>
              )}
            </div>

            {/* Address card */}
            <div className="p-4 bg-dark-900 border border-dark-750/80 rounded-xl space-y-2">
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5 text-brand-400" />
                <span>Service Location</span>
              </h5>
              {booking.address ? (
                <div className="text-xs text-slate-300 space-y-1">
                  <p className="font-semibold text-white">{booking.address.full_name} ({booking.address.phone})</p>
                  <p>{booking.address.house_no}, {booking.address.building ? `${booking.address.building}, ` : ''}{booking.address.area}</p>
                  <p className="text-slate-400">{booking.address.city}, {booking.address.state} - {booking.address.pincode}</p>
                </div>
              ) : (
                <p className="text-xs text-slate-500">Address recorded on booking file.</p>
              )}
            </div>
          </div>

          {/* Assigned Technician Profile */}
          {booking.technician && (
            <div className="p-4 bg-dark-850 border border-dark-750 rounded-2xl flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-dark-750 flex items-center justify-center font-bold text-brand-400">
                  <User className="w-5 h-5" />
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-bold text-white">
                      {(booking.technician as any).user?.full_name || (booking.technician as any).full_name || 'Assigned Specialist'}
                    </p>
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                      <ShieldCheck className="w-3 h-3" />
                      <span>Verified Pro</span>
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">
                    {(booking.technician as any).specialization || 'Certified Field Technician'}
                  </p>
                </div>
              </div>
              {((booking.technician as any).user?.phone || (booking.technician as any).phone) && (
                <a
                  href={`tel:${(booking.technician as any).user?.phone || (booking.technician as any).phone}`}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-dark-800 hover:bg-dark-750 text-slate-200 border border-dark-700 text-xs font-medium transition-colors"
                >
                  <Phone className="w-3.5 h-3.5 text-brand-400" />
                  <span>Call Pro</span>
                </a>
              )}
            </div>
          )}

          {/* Audit Logs / Timeline */}
          {logs.length > 0 && (
            <div className="space-y-2">
              <h5 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Status History</h5>
              <div className="p-3 bg-dark-900 border border-dark-800 rounded-xl space-y-2 max-h-36 overflow-y-auto">
                {logs.map((log) => (
                  <div key={log.id} className="flex items-start justify-between text-xs text-slate-300">
                    <div className="flex items-center gap-2">
                      <span className="w-1.5 h-1.5 rounded-full bg-brand-400"></span>
                      <span className="font-medium text-white capitalize">{log.to_status.replace(/_/g, ' ')}</span>
                      {log.note && <span className="text-slate-500 text-[11px]">— {log.note}</span>}
                    </div>
                    <span className="text-[10px] font-mono text-slate-500">
                      {new Date(log.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action CTAs */}
          <div className="flex flex-wrap items-center justify-between gap-3 pt-4 border-t border-dark-750">
            <div>
              {canCancel && (
                <Button
                  variant="danger"
                  size="sm"
                  onClick={handleCancelBooking}
                  isLoading={isCancelling}
                  leftIcon={AlertTriangle}
                >
                  Cancel Booking
                </Button>
              )}
            </div>

            <div className="flex items-center gap-2">
              {canVerify && (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => setIsVerifyModalOpen(true)}
                  leftIcon={QrCode}
                >
                  SmartVerify QR
                </Button>
              )}

              {canReview && (
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setIsReviewModalOpen(true)}
                  leftIcon={Star}
                >
                  Write Review
                </Button>
              )}

              <Button variant="outline" size="sm" onClick={onClose}>
                Close
              </Button>
            </div>
          </div>
        </div>
      </Modal>

      {/* Sub-modals */}
      {isVerifyModalOpen && (
        <SmartVerifyModal
          isOpen={isVerifyModalOpen}
          onClose={() => setIsVerifyModalOpen(false)}
          booking={booking}
          onVerified={() => {
            if (onBookingUpdated) onBookingUpdated();
          }}
        />
      )}

      {isReviewModalOpen && (
        <ReviewModal
          isOpen={isReviewModalOpen}
          onClose={() => setIsReviewModalOpen(false)}
          booking={booking}
          onSuccess={() => {
            if (onBookingUpdated) onBookingUpdated();
          }}
        />
      )}

      {isPaymentModalOpen && (
        <PaymentModal
          isOpen={isPaymentModalOpen}
          onClose={() => setIsPaymentModalOpen(false)}
          booking={booking}
          onPaymentSuccess={() => {
            if (onBookingUpdated) onBookingUpdated();
          }}
        />
      )}
    </>
  );
};
