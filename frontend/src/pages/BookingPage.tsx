import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Calendar, Clock, MapPin, Tag, ShieldCheck, CreditCard, CheckCircle2 } from 'lucide-react';
import { bookingApi } from '../api/booking';
import { servicesApi } from '../api/services';
import { Service } from '../types';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';

export const BookingPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const serviceIdParam = searchParams.get('service_id');
  const navigate = useNavigate();

  const [service, setService] = useState<Service | null>(null);
  const [bookingDate, setBookingDate] = useState(new Date().toISOString().split('T')[0]);
  const [preferredTime, setPreferredTime] = useState('10:00 AM');
  const [houseNo, setHouseNo] = useState('12B');
  const [area, setArea] = useState('Bandra West');
  const [city, setCity] = useState('Mumbai');
  const [pincode, setPincode] = useState('400050');
  const [promoCode, setPromoCode] = useState('');
  const [discountAmount, setDiscountAmount] = useState(0);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  useEffect(() => {
    if (serviceIdParam) {
      servicesApi.getServiceById(Number(serviceIdParam))
        .then(setService)
        .catch(() => {
          // Fallback service
          setService({
            id: Number(serviceIdParam),
            category_id: 1,
            name: 'Complete Electrical & Appliance Repair',
            description: 'Professional diagnostic inspection and wiring repair.',
            price: 499,
            duration_minutes: 60,
            rating_avg: 4.9,
            total_reviews: 120,
            is_active: true,
          });
        });
    }
  }, [serviceIdParam]);

  const basePrice = service?.price || 499;
  const taxAmount = Math.round(basePrice * 0.18);
  const finalPrice = basePrice + taxAmount - discountAmount;

  const handleApplyPromo = () => {
    if (promoCode.toUpperCase() === 'HOMIQ100') {
      setDiscountAmount(100);
      setErrorMessage('');
    } else {
      setErrorMessage('Invalid promo code. Try "HOMIQ100"');
    }
  };

  const handleCreateBookingSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMessage('');

    try {
      await bookingApi.createBooking({
        service_id: service?.id || 1,
        address_id: 1,
        booking_date: bookingDate,
        preferred_time: preferredTime,
        promo_code: promoCode,
      });

      navigate('/customer/dashboard');
    } catch (err: any) {
      setErrorMessage(
        err.response?.data?.detail || 'Failed to complete booking. Please try again.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-8">
      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white">Complete Your Booking</h1>
        <p className="text-slate-400 text-sm">Select service date, delivery address, and payment method.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Main Form */}
        <div className="md:col-span-2 space-y-6">
          <form onSubmit={handleCreateBookingSubmit} className="space-y-6">
            {/* Address Card */}
            <Card className="space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <MapPin className="w-5 h-5 text-brand-400" />
                Service Address
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <Input label="House / Flat No." value={houseNo} onChange={(e) => setHouseNo(e.target.value)} required />
                <Input label="Area / Locality" value={area} onChange={(e) => setArea(e.target.value)} required />
                <Input label="City" value={city} onChange={(e) => setCity(e.target.value)} required />
                <Input label="Pincode" value={pincode} onChange={(e) => setPincode(e.target.value)} required />
              </div>
            </Card>

            {/* Date & Time Slot */}
            <Card className="space-y-4">
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                <Calendar className="w-5 h-5 text-brand-400" />
                Date & Time Schedule
              </h3>

              <div className="grid grid-cols-2 gap-4">
                <Input label="Preferred Date" type="date" value={bookingDate} onChange={(e) => setBookingDate(e.target.value)} required />
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-slate-300">Time Slot</label>
                  <select
                    value={preferredTime}
                    onChange={(e) => setPreferredTime(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-900 border border-slate-800 rounded-xl text-white text-sm focus:outline-none focus:ring-2 focus:ring-brand-500"
                  >
                    <option>09:00 AM</option>
                    <option>10:00 AM</option>
                    <option>02:00 PM</option>
                    <option>04:00 PM</option>
                  </select>
                </div>
              </div>
            </Card>

            {/* Submit Button */}
            <Button type="submit" variant="primary" size="lg" isLoading={isLoading} className="w-full">
              Confirm & Book Service (₹{finalPrice})
            </Button>
          </form>
        </div>

        {/* Price Breakdown Sidebar */}
        <div className="space-y-6">
          <Card className="space-y-4">
            <h3 className="text-base font-bold text-white">Order Summary</h3>
            <div className="text-sm font-semibold text-brand-400">{service?.name || 'Home Maintenance Service'}</div>

            <div className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800">
              <div className="flex justify-between">
                <span>Base Service Price</span>
                <span>₹{basePrice}</span>
              </div>
              <div className="flex justify-between">
                <span>GST Tax (18%)</span>
                <span>₹{taxAmount}</span>
              </div>
              {discountAmount > 0 && (
                <div className="flex justify-between text-emerald-400 font-semibold">
                  <span>Coupon Discount</span>
                  <span>-₹{discountAmount}</span>
                </div>
              )}
              <div className="flex justify-between text-base font-extrabold text-white pt-2 border-t border-slate-800">
                <span>Total Amount</span>
                <span>₹{finalPrice}</span>
              </div>
            </div>

            {/* Promo Code Input */}
            <div className="pt-2">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Promo Code"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-900 border border-slate-800 rounded-xl text-xs text-white focus:outline-none"
                />
                <Button type="button" variant="secondary" size="sm" onClick={handleApplyPromo}>
                  Apply
                </Button>
              </div>
              {errorMessage && <div className="text-[10px] text-rose-400 mt-1">{errorMessage}</div>}
            </div>

            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-[10px] space-y-1">
              <div className="font-bold flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" /> Razorpay Escrow Protected
              </div>
              <p>Funds released to technician only after SmartVerify QR scanning.</p>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
