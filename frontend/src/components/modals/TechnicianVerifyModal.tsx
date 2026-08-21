import React, { useState } from 'react';
import { 
  ShieldCheck, 
  KeyRound, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Loader2
} from 'lucide-react';
import { bookingsApi } from '../../api/bookings';
import { Booking } from '../../types';

export interface TechnicianVerifyModalProps {
  booking: Booking;
  isOpen: boolean;
  onClose: () => void;
  onVerified: () => void;
}

export const TechnicianVerifyModal: React.FC<TechnicianVerifyModalProps> = ({
  booking,
  isOpen,
  onClose,
  onVerified,
}) => {
  const [otpCode, setOtpCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (otpCode.length < 4) {
      setError('Please enter the complete passcode provided by the customer.');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      await bookingsApi.verifyOtp(booking.id, otpCode);
      setSuccess(true);
      setTimeout(() => {
        onVerified();
        onClose();
      }, 1500);
    } catch (err: any) {
      console.error('OTP Verification failed:', err);
      setError(err?.response?.data?.detail || 'Invalid verification passcode. Please check with customer.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/85 backdrop-blur-md animate-in fade-in duration-150">
      <div className="relative w-full max-w-md rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Customer SmartVerify™</h3>
            <p className="text-xs text-slate-400 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-white">Verification Successful</h4>
            <p className="text-xs text-slate-400">Customer handshake validated. Service status updated to in progress.</p>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
              <label className="block text-xs font-semibold text-slate-200">
                Enter Customer 6-Digit Passcode
              </label>
              <input
                type="text"
                maxLength={6}
                value={otpCode}
                onChange={(e) => {
                  setOtpCode(e.target.value.replace(/[^0-9]/g, ''));
                  setError(null);
                }}
                placeholder="• • • • • •"
                className="w-full text-center tracking-[0.5em] text-2xl font-mono font-bold bg-dark-900 border border-dark-750 focus:border-sage-400 rounded-xl py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-sage-400/50"
                autoFocus
              />
              <p className="text-[11px] text-slate-400 leading-normal">
                Request the 6-digit passcode displayed on the customer's HomiQ Command Center screen.
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              type="submit"
              disabled={loading || otpCode.length < 4}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-2 shadow-subtle hover:shadow-accent disabled:opacity-40"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Validating Passcode...</span>
                </>
              ) : (
                <>
                  <KeyRound className="w-4 h-4" />
                  <span>Validate & Start Service</span>
                </>
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};
