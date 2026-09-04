import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  KeyRound, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Loader2,
  QrCode,
  Check
} from 'lucide-react';
import { bookingsApi } from '../../api/bookings';
import { Booking, VerificationStatus } from '../../types';
import { QRCodeSVG } from 'qrcode.react';

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
  const [pinCode, setPinCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const [status, setStatus] = useState<VerificationStatus | null>(null);
  const [qrToken, setQrToken] = useState<string | null>(null);
  const [qrData, setQrData] = useState<string | null>(null);

  const fetchStatus = async () => {
    try {
      const res = await bookingsApi.getVerificationStatus(booking.id);
      setStatus(res);
      if (res.is_fully_verified) {
        onVerified();
      }
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (!isOpen) return;
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, [isOpen, booking.id]);

  const handleVerifyPin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (pinCode.length < 6) {
      setError('Please enter the 6-digit PIN.');
      return;
    }
    try {
      setLoading(true);
      setError(null);
      await bookingsApi.verifyPin(booking.id, pinCode);
      await fetchStatus();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Invalid PIN.');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQR = async () => {
    try {
      setLoading(true);
      const res = await bookingsApi.generateQr(booking.id);
      setQrToken(res.verification_token);
      setQrData(res.qr_code_data);
      await fetchStatus();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error generating QR.');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    try {
      setLoading(true);
      await bookingsApi.technicianConfirm(booking.id);
      await fetchStatus();
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Error confirming.');
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
            <h3 className="text-base font-bold text-white tracking-tight">SmartVerify (Technician)</h3>
            <p className="text-xs text-slate-400 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {status?.is_fully_verified ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-white">Verification Complete</h4>
            <p className="text-xs text-slate-400">Dual handshake validated. Service is ready to start.</p>
            <button onClick={onClose} className="btn-primary w-full text-xs py-3 mt-4">Close</button>
          </div>
        ) : !status?.is_pin_verified ? (
          <form onSubmit={handleVerifyPin} className="space-y-6">
            <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
              <label className="block text-xs font-semibold text-slate-200">
                1. Enter Customer 6-Digit PIN
              </label>
              <input
                type="text"
                maxLength={6}
                value={pinCode}
                onChange={(e) => {
                  setPinCode(e.target.value.replace(/[^0-9]/g, ''));
                  setError(null);
                }}
                placeholder="- - - - - -"
                className="w-full text-center tracking-[0.5em] text-2xl font-mono font-bold bg-dark-900 border border-dark-750 focus:border-sage-400 rounded-xl py-3 text-white placeholder-slate-600 focus:outline-none focus:ring-1 focus:ring-sage-400/50"
                autoFocus
              />
            </div>

            <button
              type="submit"
              disabled={loading || pinCode.length < 6}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-2"
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <KeyRound className="w-4 h-4" />}
              <span>Verify PIN</span>
            </button>
          </form>
        ) : !status?.is_qr_scanned ? (
          <div className="space-y-6 text-center">
            <p className="text-sm text-sage-400 font-bold flex items-center justify-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> PIN Verified
            </p>
            <p className="text-xs text-slate-300">2. Generate and display QR Code for the customer to scan.</p>
            
            {qrData ? (
              <div className="p-4 bg-white rounded-xl inline-block">
                <QRCodeSVG value={qrData} size={150} />
              </div>
            ) : (
              <button onClick={handleGenerateQR} disabled={loading} className="btn-secondary w-full py-3">
                {loading ? "Generating..." : "Generate QR Code"}
              </button>
            )}
            
            <p className="text-[11px] text-slate-400 italic mt-4">Waiting for customer to scan...</p>
          </div>
        ) : (
          <div className="space-y-6 text-center">
            <p className="text-sm text-sage-400 font-bold flex items-center justify-center gap-2">
              <CheckCircle2 className="w-4 h-4" /> QR Scanned by Customer
            </p>
            <p className="text-xs text-slate-300">3. Final Dual Confirmation</p>
            
            {status.is_technician_confirmed ? (
              <p className="text-xs text-sage-400 italic">Waiting for customer to confirm...</p>
            ) : (
              <button onClick={handleConfirm} disabled={loading} className="btn-primary w-full py-3 mt-4">
                {loading ? "Confirming..." : "Confirm Service Start"}
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};
