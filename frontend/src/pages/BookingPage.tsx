import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Calendar as CalendarIcon,
  Clock,
  MapPin,
  Plus,
  Tag,
  ShieldCheck,
  CheckCircle2,
  ChevronRight,
  ChevronLeft,
  ArrowRight,
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { customerApi } from '../api/customer';
import { bookingsApi } from '../api/bookings';
import { couponsApi } from '../api/coupons';
import { Service, CustomerAddress } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Textarea } from '../components/ui/Textarea';
import { AddressModal } from '../components/modals/AddressModal';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { LoadingState } from '../components/ui/LoadingState';

export const BookingPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();

  const [step, setStep] = useState<number>(1);
  const [services, setServices] = useState<Service[]>([]);
  const [selectedService, setSelectedService] = useState<Service | null>(null);

  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);

  // Date & Time
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const defaultDate = tomorrow.toISOString().split('T')[0];

  const [bookingDate, setBookingDate] = useState<string>(defaultDate);
  const [preferredTime, setPreferredTime] = useState<string>('10:00:00');
  const [customerNote, setCustomerNote] = useState<string>('');

  // Coupon
  const [couponCode, setCouponCode] = useState<string>('');
  const [discountAmount, setDiscountAmount] = useState<number>(0);
  const [isApplyingCoupon, setIsApplyingCoupon] = useState<boolean>(false);

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const timeSlots = [
    { label: '09:00 AM - 11:00 AM', value: '09:00:00' },
    { label: '11:00 AM - 01:00 PM', value: '11:00:00' },
    { label: '02:00 PM - 04:00 PM', value: '14:00:00' },
    { label: '04:00 PM - 06:00 PM', value: '16:00:00' },
    { label: '06:00 PM - 08:00 PM', value: '18:00:00' },
  ];

  useEffect(() => {
    const init = async () => {
      setIsLoading(true);
      try {
        const [servicesData, addressData] = await Promise.all([
          servicesApi.getServices(),
          customerApi.getAddresses().catch(() => []),
        ]);

        setServices(servicesData);
        setAddresses(addressData);

        const initialServiceId = searchParams.get('service_id');
        if (initialServiceId) {
          const match = servicesData.find((s) => s.id === Number(initialServiceId));
          if (match) {
            setSelectedService(match);
            setStep(2); // Jump straight to address selection if service passed in URL
          }
        }

        if (addressData.length > 0) {
          const defaultAddr = addressData.find((a) => a.is_default) || addressData[0];
          setSelectedAddressId(defaultAddr.id);
        }
      } catch (err) {
        toast.error('Failed to load booking prerequisites', extractErrorMessage(err));
      } finally {
        setIsLoading(false);
      }
    };
    init();
  }, [searchParams]);

  const handleApplyCoupon = async () => {
    if (!couponCode.trim() || !selectedService) return;
    setIsApplyingCoupon(true);
    try {
      const res = await couponsApi.validateCoupon(
        couponCode.trim().toUpperCase(),
        selectedService.price || selectedService.base_price || 499
      );
      if (res.is_valid) {
        setDiscountAmount(res.discount_amount);
        toast.success('Coupon Applied!', `You saved ₹${res.discount_amount}`);
      } else {
        toast.error('Invalid Promo Code', res.message || 'Coupon criteria not met.');
      }
    } catch (err) {
      toast.error('Coupon Error', extractErrorMessage(err));
    } finally {
      setIsApplyingCoupon(false);
    }
  };

  const handleCreateBooking = async () => {
    if (!selectedService) {
      toast.error('Service Required', 'Please choose a service to book.');
      setStep(1);
      return;
    }
    if (!selectedAddressId) {
      toast.error('Address Required', 'Please select or add a delivery address.');
      setStep(2);
      return;
    }
    if (!bookingDate || !preferredTime) {
      toast.error('Schedule Required', 'Please select a date and time slot.');
      setStep(3);
      return;
    }

    setIsSubmitting(true);
    try {
      const estimatedPrice = Math.max(
        0,
        (selectedService.price || selectedService.base_price || 499) - discountAmount
      );

      const booking = await bookingsApi.createBooking({
        service_id: selectedService.id,
        address_id: selectedAddressId,
        booking_date: bookingDate,
        preferred_time: preferredTime,
        estimated_price: estimatedPrice,
        customer_note: customerNote.trim() || undefined,
      });

      toast.success('Service Booked Successfully!', `Booking #${booking.booking_number || booking.id} created.`);
      navigate('/customer/dashboard');
    } catch (err) {
      toast.error('Booking Creation Failed', extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-20">
        <LoadingState message="Preparing booking environment..." />
      </div>
    );
  }

  const basePrice = selectedService?.price || selectedService?.base_price || 499;
  const finalPrice = Math.max(0, basePrice - discountAmount);

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div>
        <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-1">
          HomiQ Fast Checkout
        </p>
        <h1 className="text-3xl font-bold text-white tracking-tight">Schedule Your Service</h1>
      </div>

      {/* Stepper Indicator */}
      <div className="grid grid-cols-4 gap-2 border-b border-dark-750 pb-4">
        {[
          { num: 1, label: '1. Service' },
          { num: 2, label: '2. Address' },
          { num: 3, label: '3. Schedule' },
          { num: 4, label: '4. Summary' },
        ].map((s) => (
          <button
            key={s.num}
            type="button"
            onClick={() => setStep(s.num)}
            className={`text-left pb-2 transition-all ${
              step === s.num
                ? 'border-b-2 border-brand-500 text-brand-400 font-semibold'
                : step > s.num
                ? 'text-slate-300'
                : 'text-slate-600'
            }`}
          >
            <span className="text-xs font-mono block">{s.label}</span>
          </button>
        ))}
      </div>

      {/* STEP 1: SERVICE SELECTION */}
      {step === 1 && (
        <div className="space-y-6">
          <h3 className="text-lg font-bold text-white">Choose a Service</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {services.map((srv) => {
              const isSelected = selectedService?.id === srv.id;
              return (
                <div
                  key={srv.id}
                  onClick={() => setSelectedService(srv)}
                  className={`p-4 rounded-2xl border cursor-pointer transition-all duration-150 flex flex-col justify-between ${
                    isSelected
                      ? 'bg-dark-850 border-brand-500 shadow-accent'
                      : 'bg-dark-900/80 border-dark-700/70 hover:border-dark-750 hover:bg-dark-850/50'
                  }`}
                >
                  <div className="space-y-2">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-semibold text-brand-400">
                        {srv.category_name || 'Home Service'}
                      </span>
                      <span className="text-sm font-bold text-white font-mono">
                        ₹{(srv.price || srv.base_price || 499).toFixed(2)}
                      </span>
                    </div>
                    <h4 className="text-sm font-bold text-white">{srv.name}</h4>
                    <p className="text-xs text-slate-400 line-clamp-2">{srv.description}</p>
                  </div>

                  <div className="mt-3 pt-3 border-t border-dark-800 flex items-center justify-between text-xs text-slate-400">
                    <span>{srv.duration_minutes || 60} mins</span>
                    <span className={isSelected ? 'text-brand-400 font-semibold' : 'text-slate-500'}>
                      {isSelected ? '✓ Selected' : 'Select'}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-end pt-4">
            <Button
              variant="primary"
              size="md"
              disabled={!selectedService}
              onClick={() => setStep(2)}
              rightIcon={ArrowRight}
            >
              Continue to Address
            </Button>
          </div>
        </div>
      )}

      {/* STEP 2: ADDRESS SELECTION */}
      {step === 2 && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold text-white">Select Service Address</h3>
            <Button
              variant="outline"
              size="sm"
              leftIcon={Plus}
              onClick={() => setIsAddressModalOpen(true)}
            >
              Add New Address
            </Button>
          </div>

          {addresses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {addresses.map((addr) => {
                const isSelected = selectedAddressId === addr.id;
                return (
                  <div
                    key={addr.id}
                    onClick={() => setSelectedAddressId(addr.id)}
                    className={`p-4 rounded-2xl border cursor-pointer transition-all duration-150 space-y-2 ${
                      isSelected
                        ? 'bg-dark-850 border-brand-500 shadow-accent'
                        : 'bg-dark-900/80 border-dark-700/70 hover:border-dark-750 hover:bg-dark-850/50'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-white">
                        <MapPin className="w-3.5 h-3.5 text-brand-400" />
                        <span>{addr.full_name}</span>
                      </div>
                      {addr.is_default && (
                        <span className="px-2 py-0.5 rounded text-[10px] bg-dark-800 text-slate-300 border border-dark-700">
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300">
                      {addr.house_no}, {addr.building ? `${addr.building}, ` : ''}{addr.area}
                    </p>
                    <p className="text-xs text-slate-400">
                      {addr.city}, {addr.state} - {addr.pincode}
                    </p>
                    <p className="text-[11px] text-slate-500 font-mono pt-1">Phone: {addr.phone}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="p-8 border border-dashed border-dark-700 rounded-2xl text-center space-y-3">
              <MapPin className="w-8 h-8 text-slate-500 mx-auto" />
              <p className="text-xs text-slate-300">No saved addresses found in your account.</p>
              <Button
                variant="primary"
                size="sm"
                onClick={() => setIsAddressModalOpen(true)}
              >
                Add Your Address
              </Button>
            </div>
          )}

          <div className="flex justify-between pt-4">
            <Button variant="outline" size="md" onClick={() => setStep(1)} leftIcon={ChevronLeft}>
              Back
            </Button>
            <Button
              variant="primary"
              size="md"
              disabled={!selectedAddressId}
              onClick={() => setStep(3)}
              rightIcon={ArrowRight}
            >
              Continue to Schedule
            </Button>
          </div>
        </div>
      )}

      {/* STEP 3: SCHEDULE */}
      {step === 3 && (
        <div className="space-y-6">
          <h3 className="text-lg font-bold text-white">Pick Date & Time Slot</h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 block">Service Date</label>
              <Input
                type="date"
                min={new Date().toISOString().split('T')[0]}
                value={bookingDate}
                onChange={(e) => setBookingDate(e.target.value)}
                leftIcon={CalendarIcon}
              />
            </div>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-300 block">Preferred Time Slot</label>
              <div className="space-y-2">
                {timeSlots.map((slot) => (
                  <button
                    key={slot.value}
                    type="button"
                    onClick={() => setPreferredTime(slot.value)}
                    className={`w-full p-3 rounded-xl border text-xs font-medium flex items-center justify-between transition-all ${
                      preferredTime === slot.value
                        ? 'bg-dark-850 border-brand-500 text-white shadow-accent'
                        : 'bg-dark-900/80 border-dark-700/70 text-slate-300 hover:border-dark-750'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <Clock className="w-3.5 h-3.5 text-brand-400" />
                      <span>{slot.label}</span>
                    </div>
                    {preferredTime === slot.value && <CheckCircle2 className="w-4 h-4 text-brand-400" />}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="space-y-2 pt-2">
            <Textarea
              label="Special Instructions / Entry Notes (Optional)"
              placeholder="e.g. Ring flat 402 bell, bring spare 1.5-ton AC capacitor..."
              rows={3}
              value={customerNote}
              onChange={(e) => setCustomerNote(e.target.value)}
            />
          </div>

          <div className="flex justify-between pt-4">
            <Button variant="outline" size="md" onClick={() => setStep(2)} leftIcon={ChevronLeft}>
              Back
            </Button>
            <Button variant="primary" size="md" onClick={() => setStep(4)} rightIcon={ArrowRight}>
              Review Booking
            </Button>
          </div>
        </div>
      )}

      {/* STEP 4: SUMMARY & CONFIRMATION */}
      {step === 4 && selectedService && (
        <div className="space-y-6">
          <h3 className="text-lg font-bold text-white">Review & Confirm</h3>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Booking Details Summary */}
            <div className="md:col-span-2 space-y-4">
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Service Selection
                </h4>
                <div className="flex justify-between items-center">
                  <p className="text-sm font-bold text-white">{selectedService.name}</p>
                  <span className="font-mono text-white font-semibold">₹{basePrice.toFixed(2)}</span>
                </div>
                <p className="text-xs text-slate-400">{selectedService.description}</p>
              </div>

              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl space-y-2">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Appointment Schedule
                </h4>
                <div className="flex items-center gap-4 text-xs text-white">
                  <div className="flex items-center gap-1.5">
                    <CalendarIcon className="w-3.5 h-3.5 text-brand-400" />
                    <span>{bookingDate}</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-brand-400" />
                    <span>{preferredTime}</span>
                  </div>
                </div>
              </div>

              {/* Promo code input */}
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl space-y-3">
                <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Promotional Coupon
                </h4>
                <div className="flex items-center gap-2">
                  <Input
                    placeholder="Enter Coupon Code"
                    leftIcon={Tag}
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    className="uppercase"
                  />
                  <Button
                    variant="outline"
                    size="md"
                    onClick={handleApplyCoupon}
                    isLoading={isApplyingCoupon}
                    disabled={!couponCode.trim()}
                  >
                    Apply
                  </Button>
                </div>
              </div>
            </div>

            {/* Price Card */}
            <div className="p-5 bg-dark-850 border border-dark-750 rounded-2xl space-y-4 h-fit">
              <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                Price Breakdown
              </h4>

              <div className="space-y-2 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span>Base Fare</span>
                  <span className="font-mono text-white">₹{basePrice.toFixed(2)}</span>
                </div>

                {discountAmount > 0 && (
                  <div className="flex justify-between text-emerald-400">
                    <span>Coupon Discount</span>
                    <span className="font-mono">- ₹{discountAmount.toFixed(2)}</span>
                  </div>
                )}

                <div className="flex justify-between text-slate-400">
                  <span>Taxes (Included)</span>
                  <span className="font-mono">₹0.00</span>
                </div>

                <div className="pt-3 border-t border-dark-750 flex justify-between items-center">
                  <span className="text-sm font-bold text-white">Final Total</span>
                  <span className="text-xl font-bold text-brand-400 font-mono">
                    ₹{finalPrice.toFixed(2)}
                  </span>
                </div>
              </div>

              <div className="pt-2">
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={handleCreateBooking}
                  isLoading={isSubmitting}
                  leftIcon={ShieldCheck}
                >
                  Confirm & Schedule
                </Button>
              </div>

              <div className="text-[10px] text-slate-500 text-center flex items-center justify-center gap-1">
                <ShieldCheck className="w-3 h-3 text-emerald-400" />
                <span>Zero Cancellation Fee up to 2 hours before</span>
              </div>
            </div>
          </div>

          <div className="flex justify-start pt-4">
            <Button variant="outline" size="md" onClick={() => setStep(3)} leftIcon={ChevronLeft}>
              Back
            </Button>
          </div>
        </div>
      )}

      {/* Address creation modal */}
      <AddressModal
        isOpen={isAddressModalOpen}
        onClose={() => setIsAddressModalOpen(false)}
        onSuccess={(newAddress) => {
          setAddresses([...addresses, newAddress]);
          setSelectedAddressId(newAddress.id);
        }}
      />
    </div>
  );
};
