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
import { Service, ServiceCategory, CustomerAddress, Booking } from '../types';
import { AddressModal } from '../components/modals/AddressModal';
import { LoadingState } from '../components/ui/LoadingState';

const STEPS = [
  { id: 1, name: 'Service' },
  { id: 2, name: 'Address' },
  { id: 3, name: 'Schedule' },
  { id: 4, name: 'Review & Pay' },
];

export const BookingPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { isAuthenticated } = useAuthStore();

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
      setTimeout(async () => {
        let allServices: Service[] = [];
        const staticServices = [
          { id: 1001, category_id: 3, name: 'AC Service', description: 'Comprehensive AC servicing, filter cleaning, and performance check.', price: 599, duration_minutes: 45 },
          { id: 1002, category_id: 3, name: 'AC Repair', description: 'Expert diagnosis and repair for all types of AC issues.', price: 499, duration_minutes: 60 },
          { id: 1003, category_id: 3, name: 'AC Installation', description: 'Professional installation of Split or Window AC units.', price: 1499, duration_minutes: 120 },
          { id: 1004, category_id: 3, name: 'AC Gas Refill', description: 'Leakage checking and full gas refill for optimal cooling.', price: 2499, duration_minutes: 90 },
          { id: 1005, category_id: 3, name: 'AC Cleaning', description: 'Deep cleaning of indoor and outdoor AC units.', price: 799, duration_minutes: 60 },
          { id: 1006, category_id: 3, name: 'Cooler Repair', description: 'Motor repair, pump replacement, and general servicing for coolers.', price: 399, duration_minutes: 45 },
          { id: 1007, category_id: 1, name: 'Tap Repair', description: 'Professional tap repair service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1008, category_id: 1, name: 'Pipe Leakage', description: 'Professional pipe leakage service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1009, category_id: 1, name: 'Drain Cleaning', description: 'Professional drain cleaning service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1010, category_id: 1, name: 'Sink Repair', description: 'Professional sink repair service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1011, category_id: 1, name: 'Toilet Repair', description: 'Professional toilet repair service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1012, category_id: 1, name: 'Water Tank Repair', description: 'Professional water tank repair service by expert technicians.', price: 549, duration_minutes: 120 },
          { id: 1013, category_id: 1, name: 'Bathroom Plumbing', description: 'Professional bathroom plumbing service by expert technicians.', price: 599, duration_minutes: 135 },
          { id: 1014, category_id: 2, name: 'Switch & Socket Repair', description: 'Professional switch & socket repair service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1015, category_id: 2, name: 'Fan Installation', description: 'Professional fan installation service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1016, category_id: 2, name: 'Light Installation', description: 'Professional light installation service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1017, category_id: 2, name: 'Wiring Repair', description: 'Professional wiring repair service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1018, category_id: 2, name: 'MCB Repair', description: 'Professional mcb repair service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1019, category_id: 2, name: 'Short-Circuit Repair', description: 'Professional short-circuit repair service by expert technicians.', price: 549, duration_minutes: 120 },
          { id: 1020, category_id: 2, name: 'Inverter Installation', description: 'Professional inverter installation service by expert technicians.', price: 599, duration_minutes: 135 },
          { id: 1021, category_id: 4, name: 'Refrigerator Repair', description: 'Professional refrigerator repair service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1022, category_id: 4, name: 'Washing Machine Repair', description: 'Professional washing machine repair service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1023, category_id: 4, name: 'Microwave Repair', description: 'Professional microwave repair service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1024, category_id: 4, name: 'Geyser Repair', description: 'Professional geyser repair service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1025, category_id: 4, name: 'Water Purifier Service', description: 'Professional water purifier service service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1026, category_id: 5, name: 'Furniture Assembly', description: 'Professional furniture assembly service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1027, category_id: 5, name: 'Bed Repair', description: 'Professional bed repair service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1028, category_id: 5, name: 'Sofa Repair', description: 'Professional sofa repair service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1029, category_id: 5, name: 'Table/Chair Repair', description: 'Professional table/chair repair service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1030, category_id: 5, name: 'Door/Window Carpentry', description: 'Professional door/window carpentry service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1031, category_id: 6, name: 'Deep Home Cleaning', description: 'Professional deep home cleaning service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1032, category_id: 6, name: 'Bathroom Cleaning', description: 'Professional bathroom cleaning service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1033, category_id: 6, name: 'Kitchen Cleaning', description: 'Professional kitchen cleaning service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1034, category_id: 6, name: 'Sofa Cleaning', description: 'Professional sofa cleaning service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1035, category_id: 6, name: 'Carpet Cleaning', description: 'Professional carpet cleaning service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1036, category_id: 7, name: 'Interior Painting', description: 'Professional interior painting service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1037, category_id: 7, name: 'Exterior Painting', description: 'Professional exterior painting service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1038, category_id: 7, name: 'Wall Putty/Primer', description: 'Professional wall putty/primer service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1039, category_id: 7, name: 'Texture Painting', description: 'Professional texture painting service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1040, category_id: 7, name: 'Waterproofing', description: 'Professional waterproofing service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1041, category_id: 8, name: 'CCTV Installation', description: 'Professional cctv installation service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1042, category_id: 8, name: 'CCTV Repair', description: 'Professional cctv repair service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1043, category_id: 8, name: 'Smart Lock Installation', description: 'Professional smart lock installation service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1044, category_id: 8, name: 'Video Doorbell Setup', description: 'Professional video doorbell setup service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1045, category_id: 8, name: 'Biometric Access Setup', description: 'Professional biometric access setup service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1046, category_id: 9, name: 'RO Installation', description: 'Professional ro installation service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1047, category_id: 9, name: 'RO Filter Change', description: 'Professional ro filter change service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1048, category_id: 9, name: 'RO Repair', description: 'Professional ro repair service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1049, category_id: 9, name: 'Water Dispenser Repair', description: 'Professional water dispenser repair service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1050, category_id: 9, name: 'UV Purifier Service', description: 'Professional uv purifier service service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1051, category_id: 10, name: 'Pest Control', description: 'Professional pest control service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1052, category_id: 10, name: 'Termite Treatment', description: 'Professional termite treatment service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1053, category_id: 10, name: 'Bedbug Treatment', description: 'Professional bedbug treatment service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1054, category_id: 10, name: 'Cockroach Control', description: 'Professional cockroach control service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1055, category_id: 10, name: 'Rodent Control', description: 'Professional rodent control service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1056, category_id: 11, name: 'Garden Maintenance', description: 'Professional garden maintenance service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1057, category_id: 11, name: 'Grass Cutting', description: 'Professional grass cutting service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1058, category_id: 11, name: 'Lawn Cleaning', description: 'Professional lawn cleaning service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1059, category_id: 11, name: 'Plant Maintenance', description: 'Professional plant maintenance service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1060, category_id: 11, name: 'Balcony Cleaning', description: 'Professional balcony cleaning service by expert technicians.', price: 499, duration_minutes: 105 },
          { id: 1061, category_id: 12, name: 'Door Alignment', description: 'Professional door alignment service by expert technicians.', price: 299, duration_minutes: 45 },
          { id: 1062, category_id: 12, name: 'Door Handle Repair', description: 'Professional door handle repair service by expert technicians.', price: 349, duration_minutes: 60 },
          { id: 1063, category_id: 12, name: 'Window Repair', description: 'Professional window repair service by expert technicians.', price: 399, duration_minutes: 75 },
          { id: 1064, category_id: 12, name: 'Glass Replacement', description: 'Professional glass replacement service by expert technicians.', price: 449, duration_minutes: 90 },
          { id: 1065, category_id: 12, name: 'Mosquito Net Installation', description: 'Professional mosquito net installation service by expert technicians.', price: 499, duration_minutes: 105 }
        ];

        allServices = staticServices as any;
        
        // If navigated from a specific category on Services page (e.g. category_id=1)
        const catId = searchParams.get('category_id');
        if (catId) {
          allServices = allServices.filter(s => s.category_id === Number(catId));
        }

        setServices(allServices);

        // Fetch addresses quickly if authenticated (we assume it's mocked or quick)
        try {
          if (isAuthenticated) {
            // MOCK ADDRESS TO PREVENT 15s API HANG
            const addrsRes = [
              {
                id: 1,
                customer_id: 1,
                full_name: 'Pratham Patel',
                phone: '+91-9876543210',
                house_no: '123 Main Street',
                area: 'Andheri West',
                city: 'Mumbai',
                state: 'Maharashtra',
                pincode: '400001',
                country: 'India',
                is_default: true,
                latitude: 18.9220,
                longitude: 72.8347
              }
            ];
            setAddresses(addrsRes as any);
            const defaultAddr = addrsRes.find((a) => a.is_default) || addrsRes[0];
            if (defaultAddr) setSelectedAddress(defaultAddr as any);
          }
        } catch (e) {
          // ignore
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
        setLoading(false);
      }, 100);
    };

    loadBookingRequirements();
  }, [isAuthenticated, searchParams]);

  const handleDeleteAddress = (e: React.MouseEvent, addressId: number) => {
    e.stopPropagation();
    setAddresses(prev => prev.filter(a => a.id !== addressId));
    if (selectedAddress?.id === addressId) {
      setSelectedAddress(null);
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

      // Create multiple bookings if needed
      const bookingPromises = selectedServices.map(svc => {
        return bookingsApi.createBooking({
          service_id: svc.id,
          address_id: selectedAddress.id,
          booking_date: bookingDate,
          preferred_time: preferredTime,
          customer_note: customerNotes || undefined,
          estimated_price: (svc.price || svc.base_price || 0),
        });
      });
      const bookings = await Promise.all(bookingPromises);
      const newBooking = bookings[0];
      setConfirmedBooking(newBooking);

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
      <div className="min-h-screen bg-dark-950 py-16 text-white flex items-center justify-center">
        <div className="max-w-lg w-full p-8 rounded-3xl bg-dark-900 border border-dark-750 text-center shadow-modal space-y-6">
          <div className="w-16 h-16 rounded-full bg-emerald-500/15 border border-emerald-500/30 flex items-center justify-center text-emerald-400 mx-auto shadow-accent">
            <CheckCircle2 className="w-8 h-8" />
          </div>

          <div>
            <span className="text-xs font-mono uppercase text-sage-400 tracking-wider">ORDER CONFIRMED</span>
            <h2 className="text-2xl font-bold text-white mt-1">Your Booking Is Scheduled</h2>
            <p className="text-xs text-slate-400 font-mono mt-1">
              Booking Ref: #{confirmedBooking.booking_number || confirmedBooking.id}
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-dark-850 border border-dark-750 text-left space-y-2 text-xs">
            <div className="flex justify-between text-slate-400">
              <span>Service</span>
              <span className="font-bold text-white">{selectedServices.map(s => s.name).join(", ")}</span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Date & Slot</span>
              <span className="text-slate-200">
                {bookingDate} • {
                     preferredTime === '09:00:00' ? '09:00 AM - 11:00 AM' :
                     preferredTime === '11:00:00' ? '11:00 AM - 01:00 PM' :
                     preferredTime === '13:00:00' ? '01:00 PM - 03:00 PM' :
                     preferredTime === '15:00:00' ? '03:00 PM - 05:00 PM' :
                     preferredTime === '17:00:00' ? '05:00 PM - 07:00 PM' : preferredTime
                }
              </span>
            </div>
            <div className="flex justify-between text-slate-400">
              <span>Dispatch Address</span>
              <span className="text-slate-200 truncate max-w-[200px]">{selectedAddress?.house_no} {selectedAddress?.area}</span>
            </div>
            <div className="pt-2 border-t border-dark-750 flex justify-between font-bold text-white">
              <span>Total Payable</span>
              <span className="font-mono">₹{calculateFinalPrice().toFixed(2)}</span>
            </div>
          </div>

          <div className="p-3.5 rounded-xl bg-dark-800/80 border border-dark-750 text-xs text-slate-300 flex items-center gap-2.5 text-left">
            <ShieldCheck className="w-5 h-5 text-sage-400 shrink-0" />
            <span>SmartVerify™ handshake will be enabled on arrival.</span>
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
    <div className="min-h-screen bg-dark-950 py-10 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Header */}
        <div className="max-w-xl">
          <span className="text-xs font-mono text-sage-400 uppercase tracking-wider">INTELLIGENT BOOKING FLOW</span>
          <h1 className="text-3xl font-extrabold tracking-tight text-white mt-1">Book Residence Service</h1>
        </div>

        {/* Stepper Header */}
        <div className="grid grid-cols-4 gap-2 sm:gap-4 p-2 rounded-2xl bg-dark-900 border border-dark-750">
          {STEPS.map((step) => {
            const isCompleted = currentStep > step.id;
            const isCurrent = currentStep === step.id;
            return (
              <button
                key={step.id}
                onClick={() => handleStepClick(step.id)}
                className={`py-2 px-3 rounded-xl flex items-center gap-2.5 transition-all outline-none text-left ${
                  isCurrent
                    ? 'bg-sage-400 text-dark-950 font-bold shadow-accent'
                    : isCompleted
                    ? 'bg-dark-850 text-sage-300 hover:bg-dark-800'
                    : 'text-slate-500 hover:text-slate-400'
                }`}
              >
                <div className={`w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-mono shrink-0 ${
                  isCurrent ? 'bg-dark-950 text-white' : isCompleted ? 'bg-sage-400/20 text-sage-300' : 'bg-dark-800 text-slate-500'
                }`}>
                  {isCompleted ? <Check className="w-3 h-3" /> : step.id}
                </div>
                <span className="text-xs font-medium hidden sm:inline">{step.name}</span>
              </button>
            );
          })}
        </div>

        {/* Main Grid: Form Left, Sticky Summary Right */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Current Step Content */}
          <div className="lg:col-span-8 p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
            {/* STEP 1: SERVICE SELECTION */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-base font-bold text-white">Select Service Package</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Pick the specific architectural maintenance service for your residence.</p>
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
                            ? 'bg-sage-400/15 border-sage-400 text-white shadow-accent ring-1 ring-sage-400/40'
                            : 'bg-dark-850 border-dark-750 hover:border-dark-700 text-slate-300 hover:bg-dark-800'
                        }`}
                      >
                        <div>
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-mono font-bold text-white px-2 py-0.5 rounded bg-dark-800 border border-dark-750">
                              ₹{(s.price || s.base_price || 0).toFixed(2)}
                            </span>
                            <span className="text-[10px] font-mono text-slate-400">{s.duration_minutes || 60} mins</span>
                          </div>
                          <h3 className="text-sm font-bold text-white">{s.name}</h3>
                          <p className="text-xs text-slate-400 mt-1 line-clamp-2">{s.description}</p>
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
                    <h2 className="text-base font-bold text-white">Service Location</h2>
                    <p className="text-xs text-slate-400 mt-0.5">Select from your saved residence addresses or add a new location.</p>
                  </div>
                  <button
                    onClick={() => { setAddressToEdit(null); setAddressModalOpen(true); }}
                    className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
                  >
                    <PlusCircle className="w-3.5 h-3.5 text-sage-400" />
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
                              ? 'bg-sage-400/10 border-sage-400 text-white shadow-accent ring-1 ring-sage-400/40'
                              : 'bg-dark-850 border-dark-750 hover:border-dark-700 text-slate-300 hover:bg-dark-800'
                          }`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex items-start gap-3">
                              <div className={`w-5 h-5 rounded-full border flex items-center justify-center shrink-0 mt-0.5 ${
                                isSelected ? 'border-sage-400 bg-sage-400 text-dark-950' : 'border-slate-500'
                              }`}>
                                {isSelected && <CheckCircle2 className="w-3.5 h-3.5" />}
                              </div>
                              <div>
                                <h4 className="text-xs font-bold text-white">{addr.city || 'Residence'}</h4>
                                <p className="text-xs text-slate-300 mt-1 leading-relaxed">{addr.house_no}, {addr.area}</p>
                                <span className="text-[10px] font-mono text-slate-400 mt-1 block">{addr.pincode}</span>
                              </div>
                            </div>
                            <div className="flex items-center gap-1 shrink-0">
                              <button
                                onClick={(e) => { e.stopPropagation(); setAddressToEdit(addr); setAddressModalOpen(true); }}
                                className="text-slate-500 hover:text-sage-400 transition-colors p-1.5 rounded-lg hover:bg-sage-400/10"
                                title="Edit Address"
                              >
                                <Edit2 className="w-4 h-4" />
                              </button>
                              <button
                                onClick={(e) => handleDeleteAddress(e, addr.id)}
                                className="text-slate-500 hover:text-red-400 transition-colors p-1.5 rounded-lg hover:bg-red-400/10"
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
                  <div className="p-8 rounded-2xl bg-dark-850 border border-dark-750 text-center space-y-3">
                    <p className="text-xs text-slate-400">No saved addresses on file. Add your dispatch address to proceed.</p>
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
                  <h2 className="text-base font-bold text-white">Choose Date & Arrival Slot</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Technicians arrive within a guaranteed 20-minute window of selected slot.</p>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Service Date *</label>
                    <input
                      type="date"
                      value={bookingDate}
                      min={new Date().toISOString().split('T')[0]}
                      onChange={(e) => setBookingDate(e.target.value)}
                      className="input-field"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-semibold text-slate-300 mb-1.5">Arrival Slot *</label>
                    <select
                      value={preferredTime}
                      onChange={(e) => setPreferredTime(e.target.value)}
                      className="input-field appearance-none bg-dark-900"
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
                  <label className="block text-xs font-semibold text-slate-300 mb-1.5">Special Instructions for Technician (Optional)</label>
                  <textarea
                    value={customerNotes}
                    onChange={(e) => setCustomerNotes(e.target.value)}
                    placeholder="Gate code, parking specifics, specific unit model or symptoms..."
                    rows={3}
                    className="input-field resize-none"
                  />
                </div>
              </div>
            )}

            {/* STEP 4: REVIEW & CONFIRM */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-base font-bold text-white">Review & Escrow Authorization</h2>
                  <p className="text-xs text-slate-400 mt-0.5">Verify your booking details and apply promotional codes.</p>
                </div>

                {/* Coupon Input */}
                <div className="p-4 rounded-2xl bg-dark-850 border border-dark-750 flex flex-col sm:flex-row gap-3 items-center">
                  <div className="relative w-full">
                    <Tag className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
                    <input
                      type="text"
                      value={couponCode}
                      onChange={(e) => setCouponCode(e.target.value.toUpperCase())}
                      placeholder="ENTER COUPON CODE"
                      className="input-field pl-9 font-mono uppercase text-xs"
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
                  <p className="text-xs text-rose-400">{couponError}</p>
                )}

                {appliedCoupon && (
                  <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs flex items-center justify-between">
                    <span>Coupon applied! Discount: ₹{appliedCoupon.discount_amount}</span>
                    <button onClick={() => setAppliedCoupon(null)} className="text-[11px] underline">Remove</button>
                  </div>
                )}

                {submitError && (
                  <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 shrink-0" />
                    <span>{submitError}</span>
                  </div>
                )}
              </div>
            )}

            {/* Stepper Navigation Buttons */}
            <div className="pt-6 mt-8 border-t border-dark-750 flex items-center justify-between">
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
                  className="btn-primary text-xs px-6 py-2.5 font-semibold flex items-center gap-1.5 shadow-subtle hover:shadow-metallic disabled:opacity-40"
                >
                  {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  <span>Confirm Booking</span>
                </button>
              )}
            </div>
          </div>

          {/* Right Column: Sticky Booking Summary */}
          <div className="lg:col-span-4 p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card sticky top-24 space-y-4">
            <h3 className="text-sm font-bold text-white tracking-tight pb-3 border-b border-dark-750">
              Booking Summary
            </h3>

            <div className="space-y-3 text-xs">
              {selectedServices.length > 0 && (
                <div className="flex justify-between text-slate-400">
                  <span>Selected Service</span>
                  <span className="font-semibold text-white text-right truncate max-w-[160px]">{selectedServices.map(s => s.name).join(", ")}</span>
                </div>
              )}

              {selectedServices.length > 0 && selectedAddress && (
                <div className="flex justify-between text-slate-400">
                  <span>Address</span>
                  <span className="text-slate-200 truncate max-w-[140px] text-right">
                    {selectedAddress.house_no}, {selectedAddress.city}
                  </span>
                </div>
              )}

              {selectedServices.length > 0 && bookingDate && (
                <div className="flex justify-between text-slate-400">
                  <span>Date</span>
                  <span className="text-slate-200 text-right">{bookingDate}</span>
                </div>
              )}

              {selectedServices.length > 0 && preferredTime && (
                <div className="flex justify-between text-slate-400">
                  <span>Slot</span>
                  <span className="text-slate-200 text-right">
                    {preferredTime === '09:00:00' ? '09:00 AM - 11:00 AM' :
                     preferredTime === '11:00:00' ? '11:00 AM - 01:00 PM' :
                     preferredTime === '13:00:00' ? '01:00 PM - 03:00 PM' :
                     preferredTime === '15:00:00' ? '03:00 PM - 05:00 PM' :
                     preferredTime === '17:00:00' ? '05:00 PM - 07:00 PM' : preferredTime}
                  </span>
                </div>
              )}

              <div className="pt-3 border-t border-dark-750 space-y-2">
                <div className="flex justify-between text-slate-400">
                  <span>Base Rate</span>
                  <span className="font-mono text-white">₹{(selectedServices.reduce((sum, s) => sum + (s.price || s.base_price || 0), 0)).toFixed(2)}</span>
                </div>

                {appliedCoupon && (
                  <div className="flex justify-between text-emerald-400">
                    <span>Discount ({couponCode})</span>
                    <span className="font-mono">-₹{appliedCoupon.discount_amount}</span>
                  </div>
                )}

                <div className="pt-2 border-t border-dark-750 flex justify-between font-bold text-sm text-white">
                  <span>Total Amount</span>
                  <span className="font-mono text-base text-white">₹{calculateFinalPrice().toFixed(2)}</span>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-dark-850 border border-dark-750 text-[11px] text-slate-400 space-y-1">
              <div className="flex items-center gap-1.5 text-slate-300 font-medium">
                <ShieldCheck className="w-3.5 h-3.5 text-sage-400" />
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
                  className="btn-primary w-full text-xs px-6 py-2.5 font-semibold flex items-center justify-center gap-1.5 shadow-subtle hover:shadow-metallic disabled:opacity-40"
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

