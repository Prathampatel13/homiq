import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { 
  Check, 
  ChevronRight, 
  ChevronLeft, 
  Layers, 
  MapPin, 
  Calendar, 
  Clock, 
  CreditCard, 
  ShieldCheck, 
  PlusCircle, 
  AlertCircle, 
  Loader2, 
  CheckCircle2,
  Tag,
  Trash2,
  Edit2
} from 'lucide-react';
import { servicesApi } from '../api/services';
import { customerApi } from '../api/customer';
import { bookingsApi } from '../api/bookings';
import { couponsApi } from '../api/coupons';
import { paymentsApi } from '../api/payments';
import { useAuthStore } from '../store/useAuthStore';
import { Service, ServiceCategory, CustomerAddress, Booking, UserRole } from '../types';
import { AddressModal } from '../components/modals/AddressModal';
import { LoadingState } from '../components/ui/LoadingState';
import { triggerLocalSync } from '../services/realtime';
import { ServiceEmblem } from '../components/brand/ServiceEmblem';

const STEPS = [
  { id: 1, name: 'Service' },
  { id: 2, name: 'Address' },
  { id: 3, name: 'Schedule' },
  { id: 4, name: 'Review & Pay' },
];

export const BookingPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated, getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();

  useEffect(() => {
    if (role === UserRole.TECHNICIAN) {
      navigate('/provider/dashboard', { replace: true });
    }
  }, [role, navigate]);

  const [currentStep, setCurrentStep] = useState(1);
  const [services, setServices] = useState<Service[]>([]);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [loading, setLoading] = useState(true);

  // Form State
  const [selectedServices, setSelectedServices] = useState<Service[]>([]);
  const [selectedAddress, setSelectedAddress] = useState<CustomerAddress | null>(null);
  const [bookingDate, setBookingDate] = useState<string>('');
  const [preferredTime, setPreferredTime] = useState<string>('');
  const [customerNotes, setCustomerNotes] = useState<string>('');
  const [couponCode, setCouponCode] = useState<string>('');
  const [appliedCoupon, setAppliedCoupon] = useState<any>(null);
  const [couponError, setCouponError] = useState<string | null>(null);

  const [addressModalOpen, setAddressModalOpen] = useState(false);
  const [addressToEdit, setAddressToEdit] = useState<CustomerAddress | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [confirmedBooking, setConfirmedBooking] = useState<Booking | null>(null);

  // Default booking date to tomorrow in YYYY-MM-DD
  useEffect(() => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
  }, []);

  useEffect(() => {
    const loadBookingRequirements = async () => {
      setLoading(true);
      try {
        const catId = searchParams.get('category_id');
        const svcs = await servicesApi.getServices({
          limit: 1000,
          category_id: catId ? Number(catId) : undefined
        });
        const allServices = svcs as Service[];
        setServices(allServices);

        if (isAuthenticated) {
          try {
            const addrsRes = await customerApi.getAddresses();
            if (Array.isArray(addrsRes)) {
              setAddresses(addrsRes);
              if (addrsRes.length > 0) {
                const defaultAddr = addrsRes.find((a: any) => a.is_default) || addrsRes[0];
                setSelectedAddress(defaultAddr);
              } else {
                setSelectedAddress(null);
              }
            }
          } catch (addrErr) {
            console.error("Failed to load customer addresses:", addrErr);
            setAddresses([]);
            setSelectedAddress(null);
          }
        }

        // Check if pre-selected service in query
        const serviceId = searchParams.get('service_id');
        if (serviceId && allServices.length > 0) {
          const found = allServices.find((s) => s.id === Number(serviceId));
          if (found) {
            setSelectedServices([found]);
            setCurrentStep(2); // Jump to address
          }
        }
      } catch (err) {
        console.error("Failed to load booking requirements:", err);
      } finally {
        setLoading(false);
      }
    };

    loadBookingRequirements();
  }, [isAuthenticated, searchParams]);

  const handleDeleteAddress = async (e: React.MouseEvent, addressId: number) => {
    e.stopPropagation();
    if (!window.confirm('Delete this saved address?')) return;
    try {
      await customerApi.deleteAddress(addressId);
      setAddresses(prev => prev.filter(a => a.id !== addressId));
      if (selectedAddress?.id === addressId) {
        setSelectedAddress(null);
      }
    } catch (err) {
      console.error('Failed to delete address:', err);
    }
  };

  const handleApplyCoupon = async () => {
    if (!couponCode.trim() || selectedServices.length === 0) return;
    try {
      setCouponError(null);
      const baseTotal = selectedServices.reduce((sum, s) => sum + (s.price || s.base_price || 0), 0); const res = await couponsApi.validateCoupon(couponCode, baseTotal);
      setAppliedCoupon(res);
    } catch (err: any) {
      setCouponError(err?.response?.data?.detail || 'Invalid or expired coupon code.');
      setAppliedCoupon(null);
    }
  };

  const calculateFinalPrice = () => {
    if (selectedServices.length === 0) return 0; const base = selectedServices.reduce((sum, s) => sum + (s.price || s.base_price || 0), 0);
    if (appliedCoupon?.discount_amount) {
      return Math.max(0, base - appliedCoupon.discount_amount);
    }
    return base;
  };

  const handleConfirmAndPay = async () => {
    if (!isAuthenticated) {
      navigate('/login?redirect=/booking/new');
      return;
    }
    if (selectedServices.length === 0 || !selectedAddress || !bookingDate) {
      setSubmitError('Please complete all required fields.');
      return;
    }

    try {
      setSubmitting(true);
      setSubmitError(null);

      // Create multiple bookings sequentially
      const bookings = [];
      for (const svc of selectedServices) {
        const b = await bookingsApi.createBooking({
          service_id: svc.id,
          address_id: selectedAddress.id,
          booking_date: bookingDate,
          preferred_time: preferredTime,
          customer_note: customerNotes || undefined,
          estimated_price: (svc.price || svc.base_price || 0),
        });
        bookings.push(b);
      }
      const newBooking = bookings[0];
      setConfirmedBooking(newBooking);
      triggerLocalSync();

      // Auto-initiate payment order
      try {
        await paymentsApi.createOrder(newBooking.id);
      } catch {
        // Payment order fallback
      }
    } catch (err: any) {
      console.error('Booking submission failed:', err);
      // Need to import extractErrorMessage if not already imported
      // Alternatively, inline a quick check for array
      let errorMsg = 'Failed to complete booking. Please verify your selected slot.';
      if (err?.response?.data?.detail) {
        if (typeof err.response.data.detail === 'string') {
          errorMsg = err.response.data.detail;
        } else if (Array.isArray(err.response.data.detail)) {
          errorMsg = err.response.data.detail[0]?.msg || errorMsg;
        }
      }
      setSubmitError(errorMsg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleStepClick = (targetStep: number) => {
    if (targetStep === currentStep) return;
    if (targetStep < currentStep) {
      setCurrentStep(targetStep);
      return;
    }

    let canProceed = true;
    for (let i = currentStep; i < targetStep; i++) {
      if (i === 1 && selectedServices.length === 0) {
        alert('Please select a service first.');
        canProceed = false;
        break;
      }
      if (i === 2 && !selectedAddress) {
        alert('Please select an address first.');
        canProceed = false;
        break;
      }
      if (i === 3 && (!bookingDate || !preferredTime)) {
        alert('Please select a date and time.');
        canProceed = false;
        break;
      }
    }
    
    if (canProceed) {
      setCurrentStep(targetStep);
    }
  };

  if (loading) {
    return <LoadingState message="Configuring Booking Stepper..." />;
  }

  if (confirmedBooking) {
    return (
      <div className="min-h-screen bg-[#F8FAFC] py-16 text-slate-900 flex items-center justify-center px-4">
        <div className="max-w-lg w-full p-8 rounded-3xl bg-white border border-slate-200 text-center shadow-card space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center text-emerald-600 mx-auto shadow-subtle">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div>
            <span className="text-xs font-mono uppercase text-sage-600 tracking-wider font-semibold">ORDER CONFIRMED</span>
            <h2 className="text-2xl font-bold text-slate-900 mt-1">Your Booking Is Scheduled</h2>
            <p className="text-xs text-slate-500 font-mono mt-1">
              Booking Ref: #{confirmedBooking.booking_number || confirmedBooking.id}
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 text-left space-y-2 text-xs">
            <div className="flex justify-between text-slate-500">
              <span>Service</span>
              <span className="font-bold text-slate-900">{selectedServices.map(s => s.name).join(", ")}</span>
            </div>
            <div className="flex justify-between text-slate-500">
              <span>Date & Slot</span>
              <span className="text-slate-700 font-medium">
                {bookingDate} • {
                     preferredTime === '09:00:00' ? '09:00 AM - 11:00 AM' :
                     preferredTime === '11:00:00' ? '11:00 AM - 01:00 PM' :
                     preferredTime === '13:00:00' ? '01:00 PM - 03:00 PM' :
                     preferredTime === '15:00:00' ? '03:00 PM - 05:00 PM' :
                     preferredTime === '17:00:00' ? '05:00 PM - 07:00 PM' : preferredTime
                }
              </span>
            </div>
            <div className="flex justify-between text-slate-500">
              <span>Dispatch Address</span>
              <span className="text-slate-700 truncate max-w-[200px]">{selectedAddress?.house_no} {selectedAddress?.area}</span>
            </div>
            <div className="pt-2 border-t border-slate-200 flex justify-between font-bold text-slate-900">
              <span>Total Payable</span>
              <span className="font-mono text-base">₹{calculateFinalPrice().toFixed(2)}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-sage-50 border border-sage-200 text-xs text-slate-700 flex items-center gap-2.5 text-left">
            <ShieldCheck className="w-5 h-5 text-sage-600 shrink-0" />
            <span>SmartVerify™ security PIN handshake will be enabled on technician arrival.</span>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/customer/dashboard')}
              className="w-full btn-primary text-xs py-3 font-semibold"
            >
              Go to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] py-10 text-slate-900 selection:bg-sage-500/20 selection:text-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="max-w-xl">
          <span className="text-xs font-mono text-sage-600 uppercase tracking-wider font-semibold">INTELLIGENT BOOKING FLOW</span>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mt-1">Book Residence Service</h1>
        </div>

        {/* Stepper Header */}
        <div className="grid grid-cols-4 gap-2 sm:gap-4 p-2 rounded-2xl bg-white border border-slate-200 shadow-subtle">
          {STEPS.map((step) => {
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <button
                key={step.id}
                onClick={() => handleStepClick(step.id)}
                className={`py-2 px-3 rounded-xl flex items-center gap-2.5 transition-all outline-none text-left ${
                  isCurrent
                    ? 'bg-sage-600 text-white font-bold shadow-subtle'
                    : isCompleted
                    ? 'bg-sage-50 text-sage-700 hover:bg-sage-100 font-semibold'
                    : 'text-slate-700 hover:text-slate-900 hover:bg-slate-100 font-semibold'
                }`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono shrink-0 ${
                  isCurrent ? 'bg-white/25 text-white font-bold' : isCompleted ? 'bg-sage-200 text-sage-800' : 'bg-slate-200 text-slate-700 font-bold'
                }`}>
                  {isCompleted ? <Check className="w-3 h-3" /> : step.id}
                </div>
                <span className="text-xs hidden sm:inline">{step.name}</span>
              </button>
            );
          })}
        </div>

        {/* Main Grid: Form Left, Sticky Summary Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Current Step Content */}
          <div className="lg:col-span-8 p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-card">
            {/* STEP 1: SERVICE SELECTION */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-base font-bold text-slate-900">Select Service Package</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Pick the specific architectural maintenance service for your residence.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {services.map((s) => {
                    const isSelected = selectedServices.some(sel => sel.id === s.id);
                    return (
                      <div
                        key={s.id}
                        onClick={() => setSelectedServices(prev => isSelected ? prev.filter(p => p.id !== s.id) : [...prev, s])}
                        className={`p-5 rounded-2xl border transition-all cursor-pointer flex flex-col justify-between ${
                          isSelected
                            ? 'bg-sage-50/90 border-sage-500 text-slate-900 shadow-subtle ring-2 ring-sage-500/30'
                            : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700 hover:bg-slate-50/60 shadow-subtle'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                              <ServiceEmblem category={s.name} size="xs" />
                              <span className="text-xs font-mono font-bold text-slate-900 px-2.5 py-1 rounded-lg bg-slate-100 border border-slate-200">
                                ₹{(s.price || s.base_price || 0).toFixed(2)}
                              </span>
                            </div>
                            <span className="text-[10px] font-mono text-slate-500">{s.duration_minutes || 60} mins</span>
                          </div>
                          <h3 className="text-sm font-bold text-slate-900">{s.name}</h3>
                          <p className="text-xs text-slate-600 mt-1 line-clamp-2 leading-relaxed">{s.description}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* STEP 2: ADDRESS SELECTION */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-base font-bold text-slate-900">Service Location</h2>
                    <p className="text-xs text-slate-500 mt-0.5">Select from your saved residence addresses or add a new location.</p>
                  </div>
                  <button
                    onClick={() => { setAddressToEdit(null); setAddressModalOpen(true); }}
                    className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
                  >
                    <PlusCircle className="w-3.5 h-3.5 text-sage-600" />
                    <span>New Address</span>
                  </button>
                </div>

                {addresses.length > 0 ? (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {addresses.map((addr) => {
                      const isSelected = selectedAddress?.id === addr.id;
                      return (
                        <div
                          key={addr.id}
                          onClick={() => setSelectedAddress(addr)}
                          className={`p-4 rounded-xl border transition-all cursor-pointer flex flex-col justify-between ${
                            isSelected
                              ? 'bg-sage-50/90 border-sage-500 text-slate-900 shadow-subtle ring-2 ring-sage-500/30'
                              : 'bg-white border-slate-200 hover:border-slate-300 text-slate-700 hover:bg-slate-50/60 shadow-subtle'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-3">
                              <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 ${
                                isSelected ? 'border-sage-600 bg-sage-600 text-white' : 'border-slate-300'
                              }`}>
                                {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                              </div>
                              <div>
                                <h4 className="text-xs font-bold text-slate-900">{addr.city || 'Residence'}</h4>
                                <p className="text-xs text-slate-600 mt-1 leading-relaxed">{addr.house_no}, {addr.area}</p>
                                <span className="text-[10px] font-mono text-slate-400 mt-1 block">{addr.pincode}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                              <button
                                onClick={(e) => { e.stopPropagation(); setAddressToEdit(addr); setAddressModalOpen(true); }}
                                className="text-slate-400 hover:text-slate-800 transition-colors p-1.5 rounded-lg hover:bg-slate-100"
                                title="Edit Address"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={(e) => handleDeleteAddress(e, addr.id)}
                                className="text-slate-400 hover:text-rose-600 transition-colors p-1.5 rounded-lg hover:bg-rose-50"
                                title="Delete Address"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="p-8 rounded-2xl bg-slate-50 border border-slate-200 text-center space-y-3">
                    <p className="text-xs text-slate-500">No saved addresses on file. Add your dispatch address to proceed.</p>
                    <button
                      onClick={() => { setAddressToEdit(null); setAddressModalOpen(true); }}
                      className="btn-primary text-xs px-4 py-2"
                    >
                      Add Service Address
                    </button>
                  </div>
                )}
              </div>
            )}

            {/* STEP 3: SCHEDULE */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-base font-bold text-slate-900">Choose Date & Arrival Slot</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Technicians arrive within a guaranteed 20-minute window of selected slot.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">Service Date *</label>
                    <input
                      type="date"
                      value={bookingDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setBookingDate(e.target.value)}
                      className="input-field bg-white"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-700 mb-1.5">Arrival Slot *</label>
                    <select
                      value={preferredTime}
                      onChange={(e) => setPreferredTime(e.target.value)}
                      className="input-field appearance-none bg-white text-slate-900"
                      required
                    >
                      <option value="" disabled>Select Arrival Slot</option>
                      <option value="09:00:00">09:00 AM - 11:00 AM</option>
                      <option value="11:00:00">11:00 AM - 01:00 PM</option>
                      <option value="13:00:00">01:00 PM - 03:00 PM</option>
                      <option value="15:00:00">03:00 PM - 05:00 PM</option>
                      <option value="17:00:00">05:00 PM - 07:00 PM</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-semibold text-slate-700 mb-1.5">Special Instructions for Technician (Optional)</label>
                  <textarea
                    value={customerNotes}
                    onChange={(e) => setCustomerNotes(e.target.value)}
                    placeholder="Gate code, parking specifics, specific unit model or symptoms..."
                    rows={3}
                    className="input-field resize-none bg-white"
                  />
                </div>
              </div>
            )}

            {/* STEP 4: REVIEW & CONFIRM */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-base font-bold text-slate-900">Review & Escrow Authorization</h2>
                  <p className="text-xs text-slate-500 mt-0.5">Verify your booking details and apply promotional codes.</p>
                </div>

                {/* Coupon Input */}
                <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row gap-3 items-center">
                  <div className="relative w-full">
                    <Tag className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                      placeholder="ENTER COUPON CODE"
                      className="input-field pl-9 font-mono uppercase text-xs bg-white"
                    />
                  </div>
                  <button
                    onClick={handleApplyCoupon}
                    className="btn-secondary text-xs px-4 py-2.5 whitespace-nowrap w-full sm:w-auto"
                  >
                    Apply Coupon
                  </button>
                </div>

                {couponError && (
                  <p className="text-xs text-rose-600 font-medium">{couponError}</p>
                )}

                {appliedCoupon && (
                  <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center justify-between font-medium">
                    <span>Coupon applied! Discount: ₹{appliedCoupon.discount_amount}</span>
                    <button onClick={() => setAppliedCoupon(null)} className="text-[11px] underline">Remove</button>
                  </div>
                )}

                {submitError && (
                  <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{submitError}</span>
                  </div>
                )}
              </div>
            )}

            {/* Stepper Navigation Buttons */}
            <div className="pt-6 mt-8 border-t border-slate-100 flex items-center justify-between">
              {currentStep > 1 ? (
                <button
                  onClick={() => setCurrentStep(currentStep - 1)}
                  className="btn-secondary text-xs px-4 py-2.5 flex items-center gap-1.5"
                >
                  <ChevronLeft className="w-4 h-4" />
                  <span>Back</span>
                </button>
              ) : <div />}

              {currentStep < 4 ? (
                <button
                  onClick={() => handleStepClick(currentStep + 1)}
                  className="btn-primary text-xs px-6 py-2.5 font-semibold flex items-center gap-1.5"
                >
                  <span>Continue</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleConfirmAndPay}
                  disabled={submitting}
                  className="btn-primary text-xs px-6 py-2.5 font-semibold flex items-center gap-1.5 shadow-subtle hover:shadow-accent disabled:opacity-40"
                >
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Confirm Booking</span>
                </button>
              )}
            </div>
          </div>

          {/* Right Column: Sticky Booking Summary */}
          <div className="lg:col-span-4 p-6 rounded-3xl bg-white border border-slate-200 shadow-card sticky top-24 space-y-4">
            <h3 className="text-sm font-bold text-slate-900 tracking-tight pb-3 border-b border-slate-100">
              Booking Summary
            </h3>

            <div className="space-y-3 text-xs">
              {selectedServices.length > 0 && (
                <div className="flex justify-between text-slate-500">
                  <span>Selected Service</span>
                  <span className="font-semibold text-slate-900 text-right truncate max-w-[160px]">{selectedServices.map(s => s.name).join(", ")}</span>
                </div>
              )}

              {selectedServices.length > 0 && selectedAddress && (
                <div className="flex justify-between text-slate-500">
                  <span>Address</span>
                  <span className="text-slate-700 truncate max-w-[140px] text-right font-medium">
                    {selectedAddress.house_no}, {selectedAddress.city}
                  </span>
                </div>
              )}

              {selectedServices.length > 0 && bookingDate && (
                <div className="flex justify-between text-slate-500">
                  <span>Date</span>
                  <span className="text-slate-700 text-right font-medium">{bookingDate}</span>
                </div>
              )}

              {selectedServices.length > 0 && preferredTime && (
                <div className="flex justify-between text-slate-500">
                  <span>Slot</span>
                  <span className="text-slate-700 text-right font-medium">
                    {preferredTime === '09:00:00' ? '09:00 AM - 11:00 AM' :
                     preferredTime === '11:00:00' ? '11:00 AM - 01:00 PM' :
                     preferredTime === '13:00:00' ? '01:00 PM - 03:00 PM' :
                     preferredTime === '15:00:00' ? '03:00 PM - 05:00 PM' :
                     preferredTime === '17:00:00' ? '05:00 PM - 07:00 PM' : preferredTime}
                  </span>
                </div>
              )}

              <div className="pt-3 border-t border-slate-100 space-y-2">
                <div className="flex justify-between text-slate-500">
                  <span>Base Rate</span>
                  <span className="font-mono text-slate-900 font-medium">₹{(selectedServices.reduce((sum, s) => sum + (s.price || s.base_price || 0), 0)).toFixed(2)}</span>
                </div>

                {appliedCoupon && (
                  <div className="flex justify-between text-emerald-600 font-medium">
                    <span>Discount ({couponCode})</span>
                    <span className="font-mono">-₹{appliedCoupon.discount_amount}</span>
                  </div>
                )}

                <div className="pt-2 border-t border-slate-200 flex justify-between font-bold text-sm text-slate-900">
                  <span>Total Amount</span>
                  <span className="font-mono text-base text-slate-900 font-extrabold">₹{calculateFinalPrice().toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 text-[11px] text-slate-600 space-y-1">
              <div className="flex items-center gap-1.5 text-slate-800 font-semibold">
                <ShieldCheck className="w-3.5 h-3.5 text-sage-600" />
                <span>HomiQ Guarantee</span>
              </div>
              <p className="leading-snug">30-day warranty on all parts and workmanship.</p>
            </div>

            <div className="pt-2 hidden lg:block">
              {currentStep < 4 ? (
                <button
                  onClick={() => handleStepClick(currentStep + 1)}
                  className="btn-primary w-full text-xs px-6 py-2.5 font-semibold flex items-center justify-center gap-1.5"
                >
                  <span>Continue</span>
                  <ChevronRight className="w-4 h-4" />
                </button>
              ) : (
                <button
                  onClick={handleConfirmAndPay}
                  disabled={submitting}
                  className="btn-primary w-full text-xs px-6 py-2.5 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-accent disabled:opacity-40"
                >
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Confirm Booking</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Address Modal */}
      {addressModalOpen && (
        <AddressModal
          isOpen={addressModalOpen}
          initialData={addressToEdit}
          onClose={() => { setAddressModalOpen(false); setAddressToEdit(null); }}
          onSaved={(newAddr) => {
            setAddresses(prev => {
              const exists = prev.find(a => a.id === newAddr.id);
              if (exists) return prev.map(a => a.id === newAddr.id ? newAddr : a);
              return [...prev, newAddr];
            });
            setSelectedAddress(newAddr);
          }}
        />
      )}
    </div>
  );
};

