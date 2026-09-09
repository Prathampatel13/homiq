import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  X, 
  CheckCircle2, 
  Copy,
  UserCheck,
  Clock
} from 'lucide-react';
import { bookingsApi } from '../../api/bookings';
import { Booking } from '../../types';

export interface SmartVerifyModalProps {
  booking: Booking;
  isOpen: boolean;
  onClose: () => void;
  onVerified: () => void;
}

export const SmartVerifyModal: React.FC<SmartVerifyModalProps> = ({
  booking,
  isOpen,
  onClose,
  onVerified,
}) => {
  const [details, setDetails] = useState<{ verification_code: string; qr_data: string; is_verified: boolean } | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchDetails = async () => {
    try {
      const res = await bookingsApi.getVerificationDetails(booking.id);
      setDetails(res);
      if (res.is_verified || booking.status === 'confirmed' || booking.status === 'in_progress') {
        onVerified();
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    fetchDetails();
    const interval = setInterval(fetchDetails, 3000);
    return () => clearInterval(interval);
  }, [isOpen, booking.id]);

  const handleCopy = () => {
    if (!details?.verification_code) return;
    navigator.clipboard.writeText(details.verification_code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (!isOpen) return null;

  const isVerified = details?.is_verified || booking.status === 'confirmed' || booking.status === 'in_progress';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md rounded-3xl bg-white border border-slate-200 p-6 sm:p-8 shadow-modal text-slate-900 overflow-hidden">
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sage-500 to-transparent" />

        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 border border-slate-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sage-50 border border-sage-200 flex items-center justify-center text-sage-600 shrink-0 shadow-subtle">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">SmartVerify™ Code</h3>
            <p className="text-xs text-slate-500 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {isVerified ? (
          <div className="py-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-slate-900">Technician Verified</h4>
              <p className="text-xs text-slate-600 mt-1 max-w-xs mx-auto">
                Service has been securely initiated. You can now pay at any time.
              </p>
            </div>
            <button onClick={onClose} className="btn-primary text-xs w-full py-3 mt-4">
              Close
            </button>
          </div>
        ) : (
          <div className="space-y-6 text-center">
            <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200">
              <span className="text-[11px] font-mono text-slate-500 uppercase tracking-wider block mb-2 font-semibold">
                Security Arrival Verification PIN
              </span>
              
              {!details ? (
                <div className="h-16 flex items-center justify-center text-xs font-mono text-slate-400 animate-pulse">
                  Generating secure PIN...
                </div>
              ) : (
                <>
                  <div className="flex flex-col items-center justify-center gap-3 py-2">
                    <p className="text-xs text-slate-600">
                      Share this 6-digit PIN with your technician to verify their arrival:
                    </p>
                    
                    <div className="flex items-center justify-center gap-2 mt-2">
                      {details.verification_code.split('').map((digit, idx) => (
                        <div
                          key={idx}
                          className="w-11 h-13 sm:w-12 sm:h-14 rounded-2xl bg-white border border-sage-300 text-2xl sm:text-3xl font-mono font-extrabold text-emerald-700 flex items-center justify-center shadow-subtle"
                        >
                          {digit}
                        </div>
                      ))}
                    </div>
                  </div>

                  <button
                    onClick={handleCopy}
                    className="mt-4 inline-flex items-center gap-1.5 text-xs font-mono text-sage-600 hover:text-sage-700 font-semibold transition-colors"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>{copied ? 'Copied to clipboard' : 'Copy PIN'}</span>
                  </button>
                </>
              )}
            </div>
            <p className="text-[11px] text-slate-500 italic">Waiting for technician to verify...</p>
          </div>
        )}

        <div className="mt-6 pt-5 border-t border-slate-100 flex items-center justify-between text-[11px] font-mono text-slate-500">
          <span className="flex items-center gap-1.5">
            <UserCheck className="w-3.5 h-3.5 text-sage-600" />
            <span>Secure Handshake</span>
          </span>
          <span className="flex items-center gap-1.5">
            <Clock className="w-3.5 h-3.5 text-slate-400" />
            <span>Live sync active</span>
          </span>
        </div>
      </div>
    </div>
  );
};
