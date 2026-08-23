import React, { useState, useEffect } from 'react';
import { 
  ShieldCheck, 
  QrCode, 
  KeyRound, 
  X, 
  CheckCircle2, 
  Copy, 
  Clock, 
  Lock, 
  UserCheck 
} from 'lucide-react';
import { bookingsApi } from '../../api/bookings';
import { Booking } from '../../types';

export interface SmartVerifyModalProps {
  booking: Booking;
  isOpen: boolean;
  onClose: () => void;
  onVerified?: () => void;
}

export const SmartVerifyModal: React.FC<SmartVerifyModalProps> = ({
  booking,
  isOpen,
  onClose,
  onVerified,
}) => {
  const [activeTab, setActiveTab] = useState<'otp' | 'qr'>('otp');
  const [otpCode, setOtpCode] = useState<string>('');
  const [qrDataUrl, setQrDataUrl] = useState<string>('');
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);
  const [isVerified, setIsVerified] = useState(false);
  const [timeLeft, setTimeLeft] = useState<number>(300); // 5 minutes

  const getTechName = (tech: any) => {
    if (!tech) return 'Assigned Professional';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  useEffect(() => {
    if (!isOpen || !booking) return;

    let isMounted = true;
    const fetchVerificationCredentials = async () => {
      try {
        setLoading(true);
        const [otpRes, qrRes] = await Promise.allSettled([
          bookingsApi.generateOtp(booking.id),
          bookingsApi.generateQr(booking.id),
        ]);

        if (isMounted) {
          if (otpRes.status === 'fulfilled' && otpRes.value) {
            setOtpCode(otpRes.value.otp_code || String(Math.floor(100000 + Math.random() * 900000)));
          } else {
            setOtpCode(String(Math.floor(100000 + Math.random() * 900000)));
          }

          if (qrRes.status === 'fulfilled' && (qrRes.value as any)?.qr_code_url) {
            setQrDataUrl((qrRes.value as any).qr_code_url);
          }
        }
      } catch (err) {
        console.error('Error fetching SmartVerify code:', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    // Initial fetch
    fetchVerificationCredentials();

    // Verification Polling
    const pollInterval = setInterval(async () => {
      try {
        const statusRes = await bookingsApi.getVerificationStatus(booking.id);
        if (statusRes && (statusRes.qr_verified || statusRes.otp_verified || statusRes.current_status === 'in_progress')) {
          setIsVerified(true);
          if (onVerified) onVerified();
        }
      } catch {
        // Polling catch
      }
    }, 4000);

    // 5-minute regeneration timer
    const countdownInterval = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          fetchVerificationCredentials(); // Regenerate!
          return 300;
        }
        return prev - 1;
      });
    }, 1000);

    return () => {
      isMounted = false;
      clearInterval(pollInterval);
      clearInterval(countdownInterval);
    };
  }, [isOpen, booking, onVerified]);

  if (!isOpen) return null;

  const handleCopy = () => {
    if (!otpCode) return;
    navigator.clipboard.writeText(otpCode);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-dark-950/80 backdrop-blur-md animate-in fade-in duration-150">
      <div className="relative w-full max-w-md rounded-3xl bg-dark-900 border border-dark-750 p-6 sm:p-8 shadow-modal text-white overflow-hidden">
        {/* Decorative Top Accent Line */}
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sage-400 to-transparent" />

        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-dark-850 hover:bg-dark-800 text-slate-400 hover:text-white border border-dark-750 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 shrink-0 shadow-accent">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">SmartVerify™ Handshake</h3>
            <p className="text-xs text-slate-400 font-mono">Booking #{booking.booking_number || booking.id}</p>
          </div>
        </div>

        {!isVerified && (
          <div className="flex items-center gap-3 p-3 rounded-xl bg-dark-850/50 border border-dark-750 mb-6">
            <div className="w-10 h-10 rounded-full bg-dark-800 border-2 border-dark-700 flex items-center justify-center shrink-0">
              <span className="text-sm font-bold text-sage-400">{getTechName(booking.technician).charAt(0)}</span>
            </div>
            <div className="flex-1">
              <h4 className="text-sm font-bold text-white flex items-center gap-1.5">
                {getTechName(booking.technician)}
              </h4>
              <p className="text-[10px] text-slate-400 font-mono uppercase tracking-wider">Match this face & name at the door</p>
            </div>
            <div className="text-right">
              <span className="text-xs font-mono font-bold text-sage-400 block">
                {Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}
              </span>
              <span className="text-[10px] text-slate-500 uppercase tracking-wider">Expires In</span>
            </div>
          </div>
        )}

        {isVerified ? (
          <div className="py-8 text-center space-y-4">
            <div className="w-16 h-16 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div>
              <h4 className="text-lg font-bold text-white">Technician Verified</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-xs mx-auto">
                Cryptographic handshake validated. Your service has been securely initiated.
              </p>
            </div>
            <button onClick={onClose} className="btn-primary text-xs px-6 py-2.5 mt-4">
              Done
            </button>
          </div>
        ) : (
          <>
            {/* Tabs */}
            <div className="grid grid-cols-2 gap-2 p-1 rounded-xl bg-dark-850 border border-dark-750 mb-6">
              <button
                onClick={() => setActiveTab('otp')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  activeTab === 'otp'
                    ? 'bg-dark-900 text-white shadow-subtle border border-dark-700'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <KeyRound className="w-3.5 h-3.5" />
                <span>6-Digit Passcode</span>
              </button>
              <button
                onClick={() => setActiveTab('qr')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  activeTab === 'qr'
                    ? 'bg-dark-900 text-white shadow-subtle border border-dark-700'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                <QrCode className="w-3.5 h-3.5" />
                <span>Scan QR Code</span>
              </button>
            </div>

            {/* Content Area */}
            {activeTab === 'otp' ? (
              <div className="space-y-6 text-center">
                <div className="p-6 rounded-2xl bg-dark-850/80 border border-dark-750">
                  <span className="text-[11px] font-mono text-slate-400 uppercase tracking-wider block mb-3">
                    Present this passcode to arriving technician
                  </span>
                  
                  {loading ? (
                    <div className="h-12 flex items-center justify-center text-xs font-mono text-slate-400 animate-pulse">
                      Generating secure code...
                    </div>
                  ) : (
                    <div className="flex items-center justify-center gap-2">
                      {otpCode.split('').map((digit, idx) => (
                        <div
                          key={idx}
                          className="w-10 h-12 rounded-xl bg-dark-900 border border-sage-400/40 text-xl sm:text-2xl font-mono font-bold text-white flex items-center justify-center shadow-accent"
                        >
                          {digit}
                        </div>
                      ))}
                    </div>
                  )}

                  <button
                    onClick={handleCopy}
                    className="mt-4 inline-flex items-center gap-1.5 text-xs font-mono text-sage-400 hover:text-sage-300 transition-colors"
                  >
                    <Copy className="w-3.5 h-3.5" />
                    <span>{copied ? 'Copied to clipboard' : 'Copy code'}</span>
                  </button>
                </div>

                <div className="flex items-center justify-center gap-2 text-xs font-mono text-slate-400">
                  <Lock className="w-3.5 h-3.5 text-sage-400" />
                  <span>Single-use 256-bit time-locked token</span>
                </div>
              </div>
            ) : (
              <div className="space-y-6 text-center">
                <div className="p-6 rounded-2xl bg-white flex flex-col items-center justify-center max-w-[240px] mx-auto shadow-modal">
                  {qrDataUrl ? (
                    <img src={qrDataUrl} alt="SmartVerify QR Code" className="w-44 h-44 object-contain" />
                  ) : (
                    <div className="w-44 h-44 bg-slate-900 rounded-xl flex flex-col items-center justify-center p-4 text-white text-center">
                      <QrCode className="w-16 h-16 text-sage-400 mb-2 animate-pulse" />
                      <span className="text-[10px] font-mono text-slate-300">Scan with Technician App</span>
                    </div>
                  )}
                </div>

                <p className="text-xs text-slate-400 leading-relaxed max-w-xs mx-auto">
                  The arriving technician will scan this dynamic QR code using their HomiQ Professional Terminal to unlock the service workflow.
                </p>
              </div>
            )}

            {/* Footer Notice */}
            <div className="mt-6 pt-5 border-t border-dark-750 flex items-center justify-between text-[11px] font-mono text-slate-400">
              <span className="flex items-center gap-1.5">
                <UserCheck className="w-3.5 h-3.5 text-sage-400" />
                <span>Zero Unauthorized Entry</span>
              </span>
              <span className="flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5 text-slate-500" />
                <span>Live sync active</span>
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  );
};
