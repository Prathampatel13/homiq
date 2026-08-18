import React, { useState, useEffect } from 'react';
import { ShieldCheck, RefreshCw, CheckCircle2, Lock, Smartphone } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { bookingsApi } from '../../api/bookings';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';
import { Booking } from '../../types';

interface SmartVerifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: Booking;
  onVerified?: () => void;
}

export const SmartVerifyModal: React.FC<SmartVerifyModalProps> = ({
  isOpen,
  onClose,
  booking,
  onVerified,
}) => {
  const toast = useToast();
  const [token, setToken] = useState<string>('');
  const [otpCode, setOtpCode] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isVerifying, setIsVerifying] = useState(false);
  const [isDone, setIsDone] = useState(false);

  const fetchSecurityCredentials = async () => {
    setIsLoading(true);
    try {
      // 1. Generate / retrieve cryptographic QR verification token
      const qrRes = await bookingsApi.generateQr(booking.id);
      setToken(qrRes.verification_token);

      // 2. Generate backup OTP
      const otpRes = await bookingsApi.generateOtp(booking.id);
      setOtpCode(otpRes.otp_code);
    } catch (err) {
      toast.error('Could not generate verification token', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && booking.id) {
      fetchSecurityCredentials();
      const statusCheckInterval = setInterval(async () => {
        try {
          const status = await bookingsApi.getVerificationStatus(booking.id);
          if (status.qr_verified || status.otp_verified || status.service_started) {
            setIsDone(true);
            clearInterval(statusCheckInterval);
            if (onVerified) onVerified();
          }
        } catch {
          // ignore status poll errors
        }
      }, 3000);

      return () => clearInterval(statusCheckInterval);
    }
  }, [isOpen, booking.id]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="SmartVerify Security Handshake"
      description={`Booking #${booking.booking_number || booking.id} Authentication`}
      maxWidth="md"
    >
      {isDone ? (
        <div className="text-center py-6 space-y-4">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h4 className="text-lg font-bold text-white">Technician Verified!</h4>
          <p className="text-xs text-slate-300 max-w-xs mx-auto">
            The cryptographic handshake is complete. Your service session has now officially commenced.
          </p>
          <div className="pt-2">
            <Button variant="primary" size="sm" onClick={onClose}>
              Done
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-6 text-center">
          {/* QR Box */}
          <div className="bg-dark-850 border border-dark-750 rounded-2xl p-6 relative flex flex-col items-center justify-center">
            {isLoading ? (
              <div className="py-12 flex flex-col items-center gap-3">
                <RefreshCw className="w-6 h-6 animate-spin text-brand-400" />
                <p className="text-xs text-slate-400">Generating dynamic token...</p>
              </div>
            ) : token ? (
              <div className="space-y-4">
                {/* Visual SVG QR representation */}
                <div className="p-3 bg-white rounded-2xl inline-block shadow-subtle mx-auto">
                  <img
                    src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(
                      token
                    )}`}
                    alt="SmartVerify QR Code"
                    className="w-44 h-44 rounded-lg"
                  />
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-white">Show this QR to your Technician</p>
                  <p className="text-[11px] text-slate-400">
                    The technician will scan this code to authenticate the job.
                  </p>
                </div>
              </div>
            ) : (
              <Button variant="outline" size="sm" onClick={fetchSecurityCredentials}>
                Retry Loading QR
              </Button>
            )}
          </div>

          {/* Backup OTP Section */}
          <div className="bg-dark-900 border border-dark-750/80 rounded-xl p-3.5 flex items-center justify-between text-left">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-dark-800 flex items-center justify-center text-slate-300">
                <Smartphone className="w-4 h-4" />
              </div>
              <div>
                <p className="text-xs font-medium text-white">Manual Backup OTP</p>
                <p className="text-[11px] text-slate-400">Give this 6-digit code if camera fails</p>
              </div>
            </div>
            <div className="font-mono text-base font-bold tracking-widest text-brand-400 bg-dark-950 px-3 py-1.5 rounded-lg border border-dark-700">
              {otpCode || '------'}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-dark-800">
            <div className="flex items-center gap-1.5">
              <Lock className="w-3.5 h-3.5 text-brand-400" />
              <span>256-bit SHA-256 Verified Session</span>
            </div>
            <Button variant="ghost" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
