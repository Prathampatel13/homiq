import React, { useState } from 'react';
import { ShieldCheck, QrCode, KeyRound, CheckCircle2 } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { bookingsApi } from '../../api/bookings';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';
import { Booking } from '../../types';

interface TechnicianVerifyModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: Booking;
  onSuccess: (updatedBooking: Booking) => void;
}

export const TechnicianVerifyModal: React.FC<TechnicianVerifyModalProps> = ({
  isOpen,
  onClose,
  booking,
  onSuccess,
}) => {
  const toast = useToast();
  const [activeTab, setActiveTab] = useState<'qr' | 'otp'>('qr');
  const [tokenInput, setTokenInput] = useState('');
  const [otpInput, setOtpInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleScanOrTokenSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!tokenInput.trim()) {
      toast.error('Required', 'Please enter or paste the QR verification token.');
      return;
    }

    setIsLoading(true);
    try {
      const updated = await bookingsApi.scanQr(booking.id, tokenInput.trim());
      toast.success('QR Handshake Verified', 'Customer verification authenticated.');
      onSuccess(updated);
      onClose();
    } catch (err) {
      toast.error('Verification Failed', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!otpInput.trim() || otpInput.trim().length !== 6) {
      toast.error('Invalid OTP', 'Please enter the valid 6-digit OTP code.');
      return;
    }

    setIsLoading(true);
    try {
      const updated = await bookingsApi.verifyOtp(booking.id, otpInput.trim());
      toast.success('OTP Verified', 'Service session started successfully.');
      onSuccess(updated);
      onClose();
    } catch (err) {
      toast.error('OTP Verification Failed', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Verify Customer & Start Service"
      description={`Authenticate Booking #${booking.booking_number || booking.id}`}
      maxWidth="md"
    >
      <div className="space-y-4">
        {/* Method switcher */}
        <div className="grid grid-cols-2 gap-2 p-1 bg-dark-850 rounded-xl border border-dark-750">
          <button
            type="button"
            onClick={() => setActiveTab('qr')}
            className={`flex items-center justify-center gap-2 py-2 text-xs font-medium rounded-lg transition-all ${
              activeTab === 'qr'
                ? 'bg-dark-750 text-white shadow-subtle'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <QrCode className="w-3.5 h-3.5" />
            <span>QR Scan Token</span>
          </button>
          <button
            type="button"
            onClick={() => setActiveTab('otp')}
            className={`flex items-center justify-center gap-2 py-2 text-xs font-medium rounded-lg transition-all ${
              activeTab === 'otp'
                ? 'bg-dark-750 text-white shadow-subtle'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <KeyRound className="w-3.5 h-3.5" />
            <span>Customer OTP</span>
          </button>
        </div>

        {activeTab === 'qr' ? (
          <form onSubmit={handleScanOrTokenSubmit} className="space-y-4">
            <div className="p-4 bg-dark-850 border border-dark-750 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-xs text-brand-400 font-semibold">
                <ShieldCheck className="w-4 h-4" />
                <span>Camera Scan / Token Paste</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Scan the customer's SmartVerify QR code or paste the cryptographic token string provided by the customer.
              </p>
              <Input
                placeholder="e.g. hmq_verify_7f2b9a..."
                value={tokenInput}
                onChange={(e) => setTokenInput(e.target.value)}
                autoFocus
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" type="submit" isLoading={isLoading} leftIcon={CheckCircle2}>
                Validate & Start Work
              </Button>
            </div>
          </form>
        ) : (
          <form onSubmit={handleOtpSubmit} className="space-y-4">
            <div className="p-4 bg-dark-850 border border-dark-750 rounded-xl space-y-3">
              <div className="flex items-center gap-2 text-xs text-brand-400 font-semibold">
                <KeyRound className="w-4 h-4" />
                <span>6-Digit Verification Code</span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ask the customer for the 6-digit OTP displayed on their HomiQ booking screen.
              </p>
              <Input
                placeholder="6-digit code (e.g. 842109)"
                maxLength={6}
                value={otpInput}
                onChange={(e) => setOtpInput(e.target.value.replace(/\D/g, ''))}
                className="text-center font-mono text-lg tracking-widest"
                autoFocus
              />
            </div>

            <div className="flex items-center justify-end gap-3 pt-2">
              <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isLoading}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" type="submit" isLoading={isLoading} leftIcon={CheckCircle2}>
                Verify OTP & Start Work
              </Button>
            </div>
          </form>
        )}
      </div>
    </Modal>
  );
};
