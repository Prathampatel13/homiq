import React, { useState } from 'react';
import { 
  CreditCard, 
  ShieldCheck, 
  X, 
  CheckCircle2, 
  AlertCircle, 
  Loader2, 
  Lock
} from 'lucide-react';
import { paymentsApi } from '../../api/payments';
import { Booking } from '../../types';

export interface PaymentModalProps {
  booking: Booking;
  amount: number;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const PaymentModal: React.FC<PaymentModalProps> = ({
  booking,
  amount,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  if (!isOpen) return null;

  const handlePay = async () => {
    try {
      setLoading(true);
      setError(null);

      const orderRes = await paymentsApi.createOrder(booking.id);

      const options = {
        key: import.meta.env.VITE_RAZORPAY_KEY_ID,
        amount: orderRes.amount,
        currency: orderRes.currency,
        name: "HomiQ",
        description: `Payment for Booking #${booking.booking_number || booking.id}`,
        order_id: orderRes.id,
        handler: async function (response: any) {
          try {
            await paymentsApi.verifyPayment({
              razorpay_order_id: response.razorpay_order_id,
              razorpay_payment_id: response.razorpay_payment_id,
              razorpay_signature: response.razorpay_signature,
            });
            setSuccess(true);
            setTimeout(() => {
              onSuccess();
              onClose();
            }, 1800);
          } catch (err: any) {
            console.error('Verification failure:', err);
            setError(err?.response?.data?.detail || 'Payment verification failed.');
          }
        },
        modal: {
          ondismiss: function() {
            setError('Payment cancelled by user.');
          }
        },
        theme: {
          color: "#0f172a"
        }
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on('payment.failed', function (response: any) {
        console.error('Payment failed:', response.error);
        setError(response.error.description || 'Payment failed.');
      });
      rzp.open();
    } catch (err: any) {
      console.error('Payment failure:', err);
      setError(err?.response?.data?.detail || 'Payment authorization failed. Please try again.');
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
            <CreditCard className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">Secure Payment Gateway</h3>
            <p className="text-xs text-slate-400 font-mono">HomiQ Escrow Assurance</p>
          </div>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-white">Payment Confirmed</h4>
            <p className="text-xs text-slate-400">
              Amount of ₹{amount.toFixed(2)} securely authorized. Digital tax invoice generated.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="p-5 rounded-2xl bg-dark-850 border border-dark-750 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Service Description</span>
                <span className="text-white font-medium">{booking.service?.name || 'Home Service'}</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span>Booking Reference</span>
                <span className="font-mono text-slate-300">#{booking.booking_number || booking.id}</span>
              </div>
              <div className="pt-3 border-t border-dark-750 flex items-center justify-between">
                <span className="text-xs font-semibold text-white">Total Payable</span>
                <span className="text-xl font-bold font-mono text-white">₹{amount.toFixed(2)}</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-dark-800/60 border border-dark-750 text-xs text-slate-400 flex items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-sage-400 shrink-0" />
              <p className="leading-relaxed">
                Funds held securely under HomiQ 100% Satisfaction Guarantee until service completion is verified.
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={handlePay}
              disabled={loading}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-2 shadow-subtle hover:shadow-metallic disabled:opacity-40"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Processing Secure Payment...</span>
                </>
              ) : (
                <>
                  <Lock className="w-4 h-4" />
                  <span>Pay ₹{amount.toFixed(2)} Securely</span>
                </>
              )}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
