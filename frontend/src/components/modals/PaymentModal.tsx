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

      // 1. Create order
      const orderData = await paymentsApi.createOrder(booking.id);

      // 2. Auto-settle if free/discounted
      if (orderData.status === 'paid' || orderData.status === 'PAID') {
        setSuccess(true);
        setTimeout(() => {
          onSuccess();
          onClose();
        }, 1800);
        return;
      }

      // 3. Initialize Razorpay Checkout
      const options = {
        key: orderData.key_id,
        amount: orderData.amount,
        currency: orderData.currency,
        name: 'HomiQ Services',
        description: `Payment for Booking #${booking.booking_number || booking.id}`,
        order_id: orderData.id,
        handler: async (response: any) => {
          try {
            setLoading(true);
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
            setError(err?.response?.data?.detail || 'Payment verification failed.');
            setLoading(false);
          }
        },
        theme: {
          color: '#10b981', // emerald-500
        },
      };

      const rzp = new (window as any).Razorpay(options);
      rzp.on('payment.failed', function (response: any) {
        setError(response.error.description || 'Payment failed.');
      });
      rzp.open();
      
    } catch (err: any) {
      console.error('Payment failure:', err);
      setError(err?.response?.data?.detail || 'Failed to initialize payment.');
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm animate-in fade-in duration-150">
      <div className="relative w-full max-w-md rounded-3xl bg-white border border-slate-200 p-6 sm:p-8 shadow-modal text-slate-900">
        <button
          onClick={onClose}
          className="absolute top-5 right-5 p-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-500 hover:text-slate-900 border border-slate-200 transition-colors"
        >
          <X className="w-4 h-4" />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-sage-50 border border-sage-200 flex items-center justify-center text-sage-600 shrink-0">
            <CreditCard className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900 tracking-tight">Secure Payment Gateway</h3>
            <p className="text-xs text-slate-500 font-mono">HomiQ Escrow Assurance</p>
          </div>
        </div>

        {success ? (
          <div className="py-8 text-center space-y-3">
            <div className="w-14 h-14 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mx-auto">
              <CheckCircle2 className="w-7 h-7" />
            </div>
            <h4 className="text-base font-bold text-slate-900">Payment Confirmed</h4>
            <p className="text-xs text-slate-600">
              Amount of ₹{amount.toFixed(2)} securely authorized. Digital tax invoice generated.
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-600">
                <span>Service Description</span>
                <span className="text-slate-900 font-semibold">{booking.service?.name || 'Home Service'}</span>
              </div>
              <div className="flex items-center justify-between text-xs text-slate-600">
                <span>Booking Reference</span>
                <span className="font-mono text-slate-800">#{booking.booking_number || booking.id}</span>
              </div>
              <div className="pt-3 border-t border-slate-200 flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-900">Total Payable</span>
                <span className="text-xl font-bold font-mono text-slate-900">₹{amount.toFixed(2)}</span>
              </div>
            </div>

            <div className="p-4 rounded-xl bg-sage-50 border border-sage-200 text-xs text-slate-600 flex items-center gap-3">
              <ShieldCheck className="w-5 h-5 text-sage-600 shrink-0" />
              <p className="leading-relaxed">
                Funds held securely under HomiQ 100% Satisfaction Guarantee until service completion is verified.
              </p>
            </div>

            {error && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <button
              onClick={handlePay}
              disabled={loading}
              className="w-full btn-primary text-xs py-3 font-semibold flex items-center justify-center gap-2 shadow-subtle hover:shadow-accent disabled:opacity-40"
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
