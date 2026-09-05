import React, { useState } from 'react';
import { ShieldCheck, KeyRound, X, AlertCircle, Loader2 } from 'lucide-react';
import { bookingsApi } from '../../api/bookings';
import { technicianApi } from '../../api/technician';
import { Booking } from '../../types';
import { getErrorMessage } from '../../api/axios';

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
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    if (code.length < 6) {
      setError('Please enter the full 6-digit customer PIN.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      try {
        await technicianApi.verifyCode(booking.id, code);
      } catch {
        await bookingsApi.verifyCode(booking.id, code);
      }
      onVerified();
      onClose();
    } catch (err: any) {
      setError(getErrorMessage(err, 'Invalid verification PIN. Please verify with the customer.'));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

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
            <h3 className="text-base font-bold text-white tracking-tight">Security PIN Verification</h3>
            <p className="text-xs text-slate-400 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleVerify} className="space-y-6">
          <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
            <label className="block text-xs font-semibold text-slate-200">
              Enter Customer's 6-Digit PIN
            </label>
            <input
              type="text"
              value={code}
              onChange={(e) => {
                setCode(e.target.value.replace(/[^0-9a-zA-Z]/g, ''));
                setError(null);
              }}
              placeholder="6-Digit PIN"
              className="w-full text-center tracking-[0.2em] text-xl font-mono font-bold bg-dark-900 border border-dark-750 focus:border-sage-400 rounded-xl py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-sage-400/50"
              autoFocus
            />
          </div>

          <button
            type="submit"
            disabled={loading || code.length < 6}
            className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
            <span>Verify & Start Service</span>
          </button>
        </form>
      </div>
    </div>
  );
};
