import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  PlusCircle, 
  ShieldCheck, 
  MapPin, 
  Clock, 
  Calendar, 
  CreditCard, 
  CheckCircle2, 
  AlertCircle, 
  ChevronRight, 
  Wind, 
  Zap, 
  Droplet, 
  Sparkles, 
  Wrench, 
  Home, 
  Bell, 
  Eye, 
  Star,
  Phone,
  Trash2,
  Edit2,
  Navigation2,
  Lock,
  Camera
} from 'lucide-react';
import { bookingsApi } from '../api/bookings';
import { customerApi } from '../api/customer';
import { notificationsApi } from '../api/notifications';
import { useAuthStore } from '../store/useAuthStore';
import { Booking, CustomerAddress, NotificationItem } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';
import { SmartVerifyModal } from '../components/modals/SmartVerifyModal';
import { BookingDetailsModal } from '../components/modals/BookingDetailsModal';
import { AddressModal } from '../components/modals/AddressModal';
import { PaymentModal } from '../components/modals/PaymentModal';
import { ReviewModal } from '../components/modals/ReviewModal';
import { ProofReviewModal } from '../components/modals/ProofReviewModal';
import { useRealTimeSync, triggerLocalSync } from '../services/realtime';
import { ServiceEmblem } from '../components/brand/ServiceEmblem';

export const CustomerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [verifyModalBooking, setVerifyModalBooking] = useState<Booking | null>(null);
  const [paymentModalBooking, setPaymentModalBooking] = useState<Booking | null>(null);
  const [reviewModalBooking, setReviewModalBooking] = useState<Booking | null>(null);
  const [reviewProofBooking, setReviewProofBooking] = useState<Booking | null>(null);
  const [addressModalOpen, setAddressModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState<CustomerAddress | null>(null);
  const [arrivedVerification, setArrivedVerification] = useState<{ bookingId: number; code: string; qrData: string } | null>(null);

  const getProofStatus = (note?: string | null) => {
    if (!note) return null;
    try {
      const data = JSON.parse(note);
      return data.proof_status || null;
    } catch {
      return null;
    }
  };

  const loadDashboardData = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const [bookingsRes, addressesRes, notifsRes] = await Promise.allSettled([
        bookingsApi.getBookings({ limit: 50 }),
        customerApi.getAddresses(),
        notificationsApi.getNotifications({ limit: 10 }),
      ]);

      if (bookingsRes.status === 'fulfilled') {
        const bList = Array.isArray(bookingsRes.value) ? bookingsRes.value : (bookingsRes.value as any)?.items || [];
        const sortedList = [...bList].sort((a, b) => {
          const dateA = new Date(a.booking_date).getTime();
          const dateB = new Date(b.booking_date).getTime();
          return dateB - dateA;
        });
        setBookings(sortedList);
      }
      if (addressesRes.status === 'fulfilled' && Array.isArray(addressesRes.value)) {
        setAddresses(addressesRes.value);
      }
      if (notifsRes.status === 'fulfilled' && Array.isArray(notifsRes.value)) {
        setNotifications(notifsRes.value);
      }
    } catch (err) {
      console.error('Failed to load customer DASHBOARD:', err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData(false);
  }, []);

  // Real-time synchronization across dashboards & tabs
  useRealTimeSync(() => {
    loadDashboardData(true);
  }, 15000);

  const activeBookings = bookings.filter((b) => 
    ['assigned', 'accepted', 'in_progress', 'arrived', 'start_trip', 'pending', 'confirmed', 'on_the_way', 'waiting_payment'].includes(b.status) || 
    (['completed'].includes(b.status) && b.payment_status !== 'paid')
  );

  const [arrivedVerifications, setArrivedVerifications] = useState<Record<number, { code: string; qrData: string }>>({});

  useEffect(() => {
    const fetchVerifications = async () => {
      const arrivedIds = activeBookings.filter(b => b.status === 'arrived').map(b => b.id);
      
      const newVerifications: Record<number, { code: string; qrData: string }> = { ...arrivedVerifications };
      let changed = false;

      for (const id of arrivedIds) {
        if (!newVerifications[id]) {
          try {
            const res = await bookingsApi.getVerificationDetails(id);
            newVerifications[id] = { code: res.verification_code, qrData: res.qr_data || res.qr_token };
            changed = true;
          } catch (err) {
            console.error(`Failed to fetch arrival code for ${id}:`, err);
          }
        }
      }
      
      if (changed) {
        setArrivedVerifications(newVerifications);
      }
    };

    fetchVerifications();
  }, [bookings]);



  const handleDeleteAddress = async (id: number) => {
    // Check if any active booking uses this address
    const hasActiveBooking = bookings.some(b => 
      b.address_id === id && 
      ['assigned', 'accepted', 'in_progress', 'arrived', 'start_trip', 'pending', 'confirmed', 'on_the_way'].includes(b.status)
    );
    
    if (hasActiveBooking) {
      alert('Cannot delete this address as it is currently linked to an active service dispatch.');
      return;
    }

    if (!window.confirm('Remove this service address?')) return;
    try {
      await customerApi.deleteAddress(id);
      setAddresses(addresses.filter((a) => a.id !== id));
    } catch (err: any) {
      console.error('Failed to delete address:', err);
      alert(err.response?.data?.detail || 'Failed to delete address');
    }
  };

  const getTechName = (tech: any) => {
    if (!tech) return 'Assigned Professional';
    if (tech.user?.username) return `@${tech.user.username}`;
    if (tech.username) return `@${tech.username}`;
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  if (loading) {
    return <LoadingState message="Connecting to your Home DASHBOARD..." />;
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] py-10 text-slate-900 selection:bg-sage-400/20 selection:text-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        {/* ──────────────────────────────────────────────────────────────────────────
            HEADER & PRIMARY TOP ACTION
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-200">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-pulse" />
              <span className="text-xs font-mono tracking-widest text-sage-600 font-bold uppercase">
                RESIDENTIAL DASHBOARD
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-slate-900">
              Welcome back, @{user?.username || user?.full_name?.split(' ')[0] || 'Customer'}
            </h1>
            <p className="text-xs text-slate-600 mt-0.5">
              Live status, active technician dispatches, and smart home ecosystem health.
            </p>
          </div>

          <button
            onClick={() => navigate('/booking/new')}
            className="btn-primary text-xs sm:text-sm px-6 py-3 font-semibold flex items-center gap-2 shadow-subtle hover:shadow-metallic self-start sm:self-auto"
          >
            <PlusCircle className="w-4 h-4" />
            <span>BOOK A SERVICE</span>
          </button>
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            SIGNATURE HOMIQ HOME VISUALIZATION (SERVICE HOTSPOTS)
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">Your Residence Ecosystem</h2>
              <p className="text-xs text-slate-500">Click any home sector to dispatch certified specialists</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-100 text-slate-700 border border-slate-200">
              System Ready
            </span>
          </div>

          {/* Blueprint Node Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
              { id: 'ac', name: 'AC & Climate', cat: 'ac' },
              { id: 'electrical', name: 'Electrical Core', cat: 'electrical' },
              { id: 'plumbing', name: 'Hydraulics', cat: 'plumbing' },
              { id: 'cleaning', name: 'Deep Sanitization', cat: 'cleaning' },
              { id: 'maintenance', name: 'Preventive Care', cat: 'carpentry' },
            ].map((node) => (
              <button
                key={node.id}
                onClick={() => navigate(`/booking/new`)}
                className="p-4 rounded-2xl bg-slate-50/80 hover:bg-white border border-slate-200 hover:border-slate-300 transition-all duration-200 text-left group flex flex-col justify-between shadow-subtle hover:shadow-card"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="rounded-xl overflow-hidden">
                    <ServiceEmblem category={node.cat} size="xs" />
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-700 transition-colors" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900 group-hover:text-sage-600 transition-colors">{node.name}</h4>
                  <span className="text-[10px] font-mono text-slate-500 block mt-0.5">Quick Dispatch →</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            CURRENT ACTIVE SERVICE OR ZERO-STATE BANNER
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>Current Service Dispatch</span>
          </h2>

          {activeBookings.length > 0 ? (
            <div className="space-y-6">
              {activeBookings.map(activeBooking => (
                <div key={activeBooking.id} className="p-6 sm:p-8 rounded-3xl bg-white border border-slate-200 shadow-modal space-y-6 relative overflow-hidden">
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sage-500 to-transparent" />

                  <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
                    <div className="space-y-2 max-w-xl">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold text-slate-900">
                          {activeBooking.service?.name || 'Home Service'}
                        </span>
                        <StatusBadge status={activeBooking.status} size="sm" />
                      </div>

                      <p className="text-xs text-slate-500 flex items-center gap-2 font-mono">
                        <span>Booking #{activeBooking.booking_number || activeBooking.id}</span>
                        <span>•</span>
                        <span>
                          {activeBooking.booking_date ? new Date(activeBooking.booking_date).toLocaleDateString() : 'Scheduled'}
                        </span>
                      </p>

                      {activeBooking.technician ? (
                        <div className="flex items-center gap-3 pt-2">
                          <div className="w-8 h-8 rounded-lg bg-sage-50 border border-sage-200 flex items-center justify-center text-sage-700 text-xs font-bold">
                            {getTechName(activeBooking.technician).charAt(0)}
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-slate-900">{getTechName(activeBooking.technician)}</p>
                            <span className="text-[10px] text-slate-500 font-mono">Assigned Master Professional</span>
                          </div>
                        </div>
                      ) : (
                        <p className="text-xs text-sage-600 font-mono pt-1 flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5" />
                          <span>Routing nearest certified technician...</span>
                        </p>
                      )}
                    </div>

                    <div className="flex flex-wrap items-center gap-3 w-full md:w-auto shrink-0">
                      <button
                        onClick={() => setSelectedBooking(activeBooking)}
                        className="btn-secondary text-xs px-4 py-2.5 flex items-center gap-1.5"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>View Details</span>
                      </button>

                      {/* Action buttons */}
                      {activeBooking.status === 'in_progress' && getProofStatus(activeBooking.admin_note) === 'submitted' && (
                        <button
                          onClick={() => setReviewProofBooking(activeBooking)}
                          className="btn-primary text-xs px-4 py-2.5 font-bold flex items-center gap-2 shadow-accent animate-pulse"
                        >
                          <Camera className="w-4 h-4" />
                          <span>Review & Approve Work</span>
                        </button>
                      )}

                      {/* Payment Gate Logic: Only after job completion can user pay */}
                      {['confirmed', 'in_progress'].includes(activeBooking.status) && getProofStatus(activeBooking.admin_note) !== 'approved' && activeBooking.payment_status !== 'paid' && (
                        <button
                          disabled
                          className="btn-secondary opacity-50 cursor-not-allowed text-xs px-5 py-2.5 font-semibold flex items-center gap-1.5"
                          title="Payment unlocks only after proof of work is approved."
                        >
                          <Lock className="w-4 h-4" />
                          <span>Payment Locked</span>
                        </button>
                      )}

                      {/* Pay Now Button (Top action cluster) */}
                      {((['completed', 'waiting_payment'].includes(activeBooking.status)) || (activeBooking.status === 'in_progress' && getProofStatus(activeBooking.admin_note) === 'approved')) && activeBooking.payment_status !== 'paid' && (
                        <button
                          onClick={() => setPaymentModalBooking(activeBooking)}
                          className="btn-primary text-xs px-4 py-2.5 font-bold flex items-center gap-2 shadow-accent animate-pulse"
                        >
                          <CreditCard className="w-4 h-4" />
                          <span>Pay Now</span>
                        </button>
                      )}
                    </div>
                  </div>

                  {/* ── SECURITY PIN SHOWCASE: ONLY WHEN ARRIVED ── */}
                  {activeBooking.status === 'arrived' && (
                    <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in duration-300">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
                          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider">
                            Technician Arrived at Location
                          </span>
                        </div>
                        <p className="text-xs text-slate-600">
                          Share this 6-digit PIN with your technician to authorize service initiation:
                        </p>
                      </div>

                      <div className="flex items-center gap-3 self-stretch sm:self-auto justify-between sm:justify-end">
                        {arrivedVerifications[activeBooking.id]?.code ? (
                          <div className="flex items-center gap-2 font-mono text-xl font-extrabold text-emerald-700 bg-white px-5 py-2.5 rounded-xl border border-emerald-500/40 tracking-[0.3em] shadow-sm">
                            {arrivedVerifications[activeBooking.id].code}
                          </div>
                        ) : (
                          <div className="text-xs font-mono text-slate-500 animate-pulse px-4 py-2 bg-white border border-slate-200 rounded-xl">
                            Generating PIN...
                          </div>
                        )}

                        <button
                          onClick={() => setVerifyModalBooking(activeBooking)}
                          className="btn-accent text-xs px-4 py-2.5 font-semibold flex items-center gap-1.5 shadow-subtle shrink-0"
                        >
                          <ShieldCheck className="w-4 h-4" />
                          <span>PIN Details</span>
                        </button>
                      </div>
                    </div>
                  )}

                  {/* ── PROOF OF WORK SUBMITTED: CUSTOMER APPROVAL STEP ── */}
                  {activeBooking.status === 'in_progress' && getProofStatus(activeBooking.admin_note) === 'submitted' && (
                    <div className="p-5 rounded-2xl bg-sage-50 border border-sage-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in duration-300 shadow-sm">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="w-2.5 h-2.5 rounded-full bg-sage-500 animate-ping" />
                          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
                            Work Evidence Ready for Inspection
                          </span>
                        </div>
                        <p className="text-xs text-slate-600">
                          Your technician uploaded Before & After photos. Please inspect and approve the work to unlock payment and complete the job.
                        </p>
                      </div>

                      <button
                        onClick={() => setReviewProofBooking(activeBooking)}
                        className="btn-primary text-xs px-6 py-2.5 font-bold flex items-center gap-2 shrink-0 shadow-accent active:scale-95"
                      >
                        <Camera className="w-4 h-4" />
                        <span>Inspect & Approve Work</span>
                      </button>
                    </div>
                  )}

                  {/* ── APPROVED / PAYMENT BANNER ── */}
                  {(['completed', 'waiting_payment'].includes(activeBooking.status) || (activeBooking.status === 'in_progress' && getProofStatus(activeBooking.admin_note) === 'approved')) && activeBooking.payment_status !== 'paid' && (
                    <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 animate-in fade-in duration-300">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                          <span className="text-xs font-bold text-slate-900 uppercase tracking-wider font-mono">
                            Work Approved • Payment Due
                          </span>
                        </div>
                        <p className="text-xs text-slate-600">
                          Work evidence has been verified. Please complete payment securely to finalize the job.
                        </p>
                      </div>

                      <button
                        onClick={() => setPaymentModalBooking(activeBooking)}
                        className="btn-primary text-xs px-6 py-2.5 font-bold flex items-center gap-2 shrink-0 shadow-accent"
                      >
                        <CreditCard className="w-4 h-4" />
                        <span>Pay ₹{(activeBooking.final_price || activeBooking.total_amount || activeBooking.estimated_price || 0).toFixed(2)}</span>
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-8 rounded-3xl bg-white border border-slate-200 text-center space-y-3 shadow-card">
              <div className="w-12 h-12 rounded-2xl bg-slate-50 border border-slate-200 flex items-center justify-center text-slate-400 mx-auto">
                <CheckCircle2 className="w-6 h-6 text-sage-600" />
              </div>
              <h3 className="text-base font-bold text-slate-900">NO UPCOMING SERVICE</h3>
              <p className="text-xs text-slate-600 max-w-sm mx-auto">
                Book a trusted HomiQ professional for your next home service with guaranteed quality.
              </p>
              <button
                onClick={() => navigate('/booking/new')}
                className="btn-primary text-xs px-6 py-2.5 mt-2"
              >
                BOOK A SERVICE
              </button>
            </div>
          )}
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            SAVED RESIDENCE ADDRESSES
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-bold text-slate-900 tracking-tight">Saved Residence Addresses</h2>
            <button
              onClick={() => {
                setEditingAddress(null);
                setAddressModalOpen(true);
              }}
              className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
            >
              <PlusCircle className="w-3.5 h-3.5 text-sage-600" />
              <span>Add Address</span>
            </button>
          </div>

          {addresses.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {addresses.map((addr) => (
                <div
                  key={addr.id}
                  className="p-5 rounded-2xl bg-white border border-slate-200 flex flex-col justify-between shadow-card relative group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-sage-600" />
                        <span className="text-xs font-bold text-slate-900">{addr.city || 'Residence'}</span>
                      </div>
                      {addr.is_default && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sage-100 text-sage-800 border border-sage-200">
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                      {addr.house_no} {addr.building ? `, ${addr.building}` : ''} {addr.area}
                    </p>
                    <p className="text-[11px] font-mono text-slate-500 mt-1">
                      {addr.city}, {addr.pincode}
                    </p>
                  </div>

                  <div className="pt-4 mt-4 border-t border-slate-100 flex items-center justify-end gap-2">
                    <button
                      onClick={() => {
                        setEditingAddress(addr);
                        setAddressModalOpen(true);
                      }}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-slate-900 hover:bg-slate-100"
                      title="Edit"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteAddress(addr.id)}
                      className="p-1.5 rounded-lg text-slate-500 hover:text-rose-600 hover:bg-rose-50"
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <EmptyState
              title="NO SAVED ADDRESSES"
              description="Add an address to make your next booking faster and enable precise technician dispatch."
              actionLabel="ADD ADDRESS"
              onAction={() => {
                setEditingAddress(null);
                setAddressModalOpen(true);
              }}
            />
          )}
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            SERVICE HISTORY & ALL BOOKINGS TABLE
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight">Service History</h2>

          {bookings.length > 0 ? (
            <div className="rounded-3xl bg-white border border-slate-200 overflow-hidden shadow-card">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-mono uppercase text-[10px]">
                    <tr>
                      <th className="py-3.5 px-4">Booking Ref & Service</th>
                      <th className="py-3.5 px-4">Date</th>
                      <th className="py-3.5 px-4">Status</th>
                      <th className="py-3.5 px-4">Amount</th>
                      <th className="py-3.5 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-600">
                    {bookings.map((b) => (
                      <tr key={b.id} className="hover:bg-slate-50/80 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-medium text-slate-900">
                          #{b.booking_number || b.id}
                          <div className="text-[10px] text-sage-600 mt-1 uppercase font-sans tracking-widest font-semibold">
                            {b.service?.name || 'Service Order'}
                          </div>
                        </td>
                        <td className="py-3.5 px-4 text-slate-500">
                          {b.booking_date ? new Date(b.booking_date).toLocaleDateString() : '—'}
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge 
                            status={['confirmed', 'in_progress', 'completed'].includes(b.status) && b.payment_status !== 'paid' ? 'waiting_payment' : b.status} 
                            size="sm" 
                          />
                        </td>
                        <td className="py-3.5 px-4 font-mono font-bold text-slate-900">
                          ₹{(b.final_price || b.total_amount || b.estimated_price || 0).toFixed(2)}
                        </td>
                        <td className="py-3.5 px-4 text-right space-x-2">
                          <button
                            onClick={() => setSelectedBooking(b)}
                            className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 text-[11px] font-medium"
                          >
                            Details
                          </button>
                          {b.status === 'completed' && b.payment_status === 'paid' && (
                            <button
                              onClick={() => setReviewModalBooking(b)}
                              className="px-2.5 py-1 rounded-lg bg-sage-50 hover:bg-sage-100 text-sage-700 border border-sage-200 text-[11px] font-medium"
                            >
                              Review
                            </button>
                          )}
                          {['confirmed', 'in_progress', 'completed'].includes(b.status) && b.payment_status !== 'paid' && (
                            <button
                              onClick={() => setPaymentModalBooking(b)}
                              className="px-2.5 py-1 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 text-[11px] font-medium"
                            >
                              Pay Now
                            </button>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-2xl bg-white border border-slate-200 text-center text-xs text-slate-500 shadow-card">
              No historical services recorded yet. Your completed bookings and workmanship reports will appear here.
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      {selectedBooking && (
        <BookingDetailsModal
          booking={selectedBooking}
          isOpen={!!selectedBooking}
          onClose={() => setSelectedBooking(null)}
          onOpenVerify={() => {
            setVerifyModalBooking(selectedBooking);
            setSelectedBooking(null);
          }}
          onOpenPayment={() => {
            setPaymentModalBooking(selectedBooking);
            setSelectedBooking(null);
          }}
          onOpenReview={() => {
            setReviewModalBooking(selectedBooking);
            setSelectedBooking(null);
          }}
          onBookingUpdated={() => {
            loadDashboardData(true);
          }}
        />
      )}

      {verifyModalBooking && (
        <SmartVerifyModal
          booking={verifyModalBooking}
          isOpen={!!verifyModalBooking}
          onClose={() => setVerifyModalBooking(null)}
          onVerified={() => {
            loadDashboardData();
          }}
        />
      )}

      {paymentModalBooking && (
        <PaymentModal
          booking={paymentModalBooking}
          amount={paymentModalBooking.final_price || paymentModalBooking.total_amount || paymentModalBooking.estimated_price || 0}
          isOpen={!!paymentModalBooking}
          onClose={() => setPaymentModalBooking(null)}
          onSuccess={() => {
            loadDashboardData();
          }}
        />
      )}

      {reviewModalBooking && (
        <ReviewModal
          booking={reviewModalBooking}
          isOpen={!!reviewModalBooking}
          onClose={() => setReviewModalBooking(null)}
          onSubmitted={() => {
            loadDashboardData();
          }}
        />
      )}

      {addressModalOpen && (
        <AddressModal
          isOpen={addressModalOpen}
          initialData={editingAddress}
          onClose={() => {
            setAddressModalOpen(false);
            setEditingAddress(null);
          }}
          onSaved={() => {
            loadDashboardData();
          }}
        />
      )}

      {reviewProofBooking && (
        <ProofReviewModal
          booking={reviewProofBooking}
          isOpen={!!reviewProofBooking}
          onClose={() => setReviewProofBooking(null)}
          onApproved={() => {
            const bookingToPay = reviewProofBooking;
            setReviewProofBooking(null);
            triggerLocalSync();
            loadDashboardData(true);
            if (bookingToPay) {
              setPaymentModalBooking(bookingToPay);
            }
          }}
        />
      )}
    </div>
  );
};



