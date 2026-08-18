import React, { useState } from 'react';
import { CreditCard, Tag, ShieldCheck, CheckCircle2, Lock } from 'lucide-react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { paymentsApi } from '../../api/payments';
import { couponsApi } from '../../api/coupons';
import { useToast } from '../ui/Toast';
import { extractErrorMessage } from '../../api/axios';
import { Booking } from '../../types';

interface PaymentModalProps {
  isOpen: boolean;
  onClose: () => void;
  booking: Booking;
  onPaymentSuccess?: () => void;
}

export const PaymentModal: React.FC<PaymentModalProps> = ({
  isOpen,
  onClose,
  booking,
  onPaymentSuccess,
}) => {
  const toast = useToast();
  const [couponCode, setCouponCode] = useState('');
  const [discountAmount, setDiscountAmount] = useState(booking.discount_amount || 0);
  const [isApplyingCoupon, setIsApplyingCoupon] = useState(false);
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);

  const basePrice = booking.final_price || booking.base_price || booking.estimated_price || (booking.service?.price ?? 499);
  const finalPrice = Math.max(0, basePrice - discountAmount);

  const handleApplyCoupon = async () => {
    if (!couponCode.trim()) return;
    setIsApplyingCoupon(true);
    try {
      const res = await couponsApi.applyCoupon(couponCode.trim().toUpperCase(), basePrice, booking.id);
      if (res.is_valid) {
        setDiscountAmount(res.discount_amount);
        toast.success('Coupon Applied!', `You saved ₹${res.discount_amount}`);
      } else {
        toast.error('Invalid Coupon', res.message || 'Coupon could not be applied.');
      }
    } catch (err) {
      toast.error('Coupon Error', extractErrorMessage(err));
    } finally {
      setIsApplyingCoupon(false);
    }
  };

  const handlePayNow = async () => {
    setIsProcessingPayment(true);
    try {
      // 1. Create order on backend
      const order = await paymentsApi.createOrder(booking.id);

      // 2. Simulated / Razorpay gateway checkout verification
      const verifyRes = await paymentsApi.verifyPayment({
        razorpay_order_id: order.id || `order_sim_${Date.now()}`,
        razorpay_payment_id: `pay_${Date.now()}`,
        razorpay_signature: 'simulated_signature_verified',
      });

      toast.success('Payment Successful', 'Receipt generated and service booked.');
      setIsCompleted(true);
      if (onPaymentSuccess) onPaymentSuccess();
    } catch (err) {
      toast.error('Payment Failed', extractErrorMessage(err));
    } finally {
      setIsProcessingPayment(false);
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Secure Checkout"
      description={`Invoice for Booking #${booking.booking_number || booking.id}`}
      maxWidth="md"
    >
      {isCompleted ? (
        <div className="text-center py-6 space-y-4">
          <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center justify-center mx-auto">
            <CheckCircle2 className="w-8 h-8" />
          </div>
          <h4 className="text-lg font-bold text-white">Payment Confirmed!</h4>
          <p className="text-xs text-slate-300 max-w-xs mx-auto">
            ₹{finalPrice.toFixed(2)} received successfully. Your service specialist is confirmed.
          </p>
          <div className="pt-2">
            <Button variant="primary" size="sm" onClick={onClose}>
              View Booking
            </Button>
          </div>
        </div>
      ) : (
        <div className="space-y-5">
          {/* Service Price Breakdown */}
          <div className="p-4 bg-dark-850 border border-dark-750 rounded-2xl space-y-3">
            <div className="flex justify-between items-center text-xs text-slate-300">
              <span>{booking.service?.name || 'Home Maintenance Service'}</span>
              <span className="font-mono font-medium text-white">₹{basePrice.toFixed(2)}</span>
            </div>

            {discountAmount > 0 && (
              <div className="flex justify-between items-center text-xs text-emerald-400">
                <span>Promotional Discount</span>
                <span className="font-mono font-medium">- ₹{discountAmount.toFixed(2)}</span>
              </div>
            )}

            <div className="flex justify-between items-center text-xs text-slate-400">
              <span>GST / Taxes (Included)</span>
              <span className="font-mono">₹0.00</span>
            </div>

            <div className="pt-3 border-t border-dark-750 flex justify-between items-center">
              <span className="text-sm font-semibold text-white">Total Amount Due</span>
              <span className="text-lg font-bold text-brand-400 font-mono">₹{finalPrice.toFixed(2)}</span>
            </div>
          </div>

          {/* Coupon Code Box */}
          <div className="flex items-center gap-2">
            <div className="flex-1">
              <Input
                placeholder="Enter Promo / Coupon Code"
                leftIcon={Tag}
                value={couponCode}
                onChange={(e) => setCouponCode(e.target.value)}
                className="uppercase"
              />
            </div>
            <Button
              variant="outline"
              size="md"
              type="button"
              onClick={handleApplyCoupon}
              isLoading={isApplyingCoupon}
              disabled={!couponCode.trim()}
            >
              Apply
            </Button>
          </div>

          {/* Payment Method Details */}
          <div className="p-3.5 bg-dark-900 border border-dark-750 rounded-xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-dark-800 flex items-center justify-center text-slate-300">
                <CreditCard className="w-4 h-4 text-brand-400" />
              </div>
              <div>
                <p className="text-xs font-semibold text-white">Instant Online Payment</p>
                <p className="text-[11px] text-slate-400">UPI, Cards, NetBanking, Wallets</p>
              </div>
            </div>
            <div className="flex items-center gap-1 text-[11px] text-slate-400">
              <Lock className="w-3 h-3 text-emerald-400" />
              <span>Razorpay Secured</span>
            </div>
          </div>

          <div className="flex items-center justify-end gap-3 pt-3 border-t border-dark-750">
            <Button variant="outline" size="sm" type="button" onClick={onClose} disabled={isProcessingPayment}>
              Cancel
            </Button>
            <Button
              variant="primary"
              size="sm"
              type="button"
              onClick={handlePayNow}
              isLoading={isProcessingPayment}
              leftIcon={ShieldCheck}
            >
              Pay ₹{finalPrice.toFixed(2)}
            </Button>
          </div>
        </div>
      )}
    </Modal>
  );
};
