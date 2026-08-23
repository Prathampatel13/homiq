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
  Edit2
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
import { LiveTrackingModal } from '../components/modals/LiveTrackingModal';
import { LiveTrackingWidget } from '../components/ui/LiveTrackingWidget';

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
  const [trackingModalBooking, setTrackingModalBooking] = useState<Booking | null>(null);
  const [addressModalOpen, setAddressModalOpen] = useState(false);
  const [editingAddress, setEditingAddress] = useState<CustomerAddress | null>(null);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [bookingsRes, addressesRes, notifsRes] = await Promise.allSettled([
        bookingsApi.getBookings({ limit: 50 }),
        customerApi.getAddresses(),
        notificationsApi.getNotifications({ limit: 10 }),
      ]);

      if (bookingsRes.status === 'fulfilled') {
        const bList = Array.isArray(bookingsRes.value) ? bookingsRes.value : (bookingsRes.value as any)?.items || [];
        setBookings(bList);
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
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const activeBooking = bookings.find((b) => 
    ['assigned', 'accepted', 'in_progress', 'arrived', 'start_trip', 'pending', 'confirmed', 'on_the_way'].includes(b.status)
  );

  const routingBooking = bookings.find((b) => 
    ['assigned', 'accepted', 'on_the_way', 'pending', 'confirmed'].includes(b.status)
  );

  const pastBookings = bookings.filter((b) => 
    ['completed', 'cancelled', 'rejected'].includes(b.status)
  );

  const handleDeleteAddress = async (id: number) => {
    if (!window.confirm('Remove this service address?')) return;
    try {
      await customerApi.deleteAddress(id);
      setAddresses(addresses.filter((a) => a.id !== id));
    } catch (err) {
      console.error('Failed to delete address:', err);
    }
  };

  const getTechName = (tech: any) => {
    if (!tech) return 'Assigned Professional';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  if (loading) {
    return <LoadingState message="Connecting to your Home DASHBOARD..." />;
  }

  return (
    <div className="min-h-screen bg-dark-950 py-10 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-10">
        {/* ──────────────────────────────────────────────────────────────────────────
            HEADER & PRIMARY TOP ACTION
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-dark-750">
                <div>
            <div className="flex items-center gap-2 mb-1">
              <span className="w-2.5 h-2.5 rounded-full bg-sage-400 animate-pulse" />
              <span className="text-xs font-mono tracking-widest text-sage-400 uppercase">
                RESIDENTIAL DASHBOARD
              </span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-extrabold tracking-tight text-white">
              Welcome back, {user?.full_name?.split(' ')[0] || 'Homeowner'}
            </h1>
            <p className="text-xs text-slate-400 mt-0.5">
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
        <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-b from-dark-900 via-dark-850 to-dark-900 border border-dark-750 shadow-card">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-bold text-white tracking-tight">Your Residence Ecosystem</h2>
              <p className="text-xs text-slate-400">Click any home sector to dispatch certified specialists</p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-dark-800 text-slate-300 border border-dark-750">
              System Ready
            </span>
          </div>

          {/* Blueprint Node Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
              { id: 'ac', name: 'AC & Climate', icon: Wind, cat: 'ac' },
              { id: 'electrical', name: 'Electrical Core', icon: Zap, cat: 'electrical' },
              { id: 'plumbing', name: 'Hydraulics', icon: Droplet, cat: 'plumbing' },
              { id: 'cleaning', name: 'Deep Sanitization', icon: Sparkles, cat: 'cleaning' },
              { id: 'maintenance', name: 'Preventive Care', icon: Wrench, cat: 'maintenance' },
            ].map((node) => (
              <button
                key={node.id}
                onClick={() => navigate(`/booking/new`)}
                className="p-4 rounded-2xl bg-dark-900/90 hover:bg-dark-800 border border-dark-750 hover:border-sage-400/50 transition-all duration-200 text-left group flex flex-col justify-between shadow-subtle"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="p-2.5 rounded-xl bg-dark-850 group-hover:bg-sage-400 text-sage-400 group-hover:text-dark-950 transition-colors">
                    <node.icon className="w-5 h-5" />
                  </div>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-500 group-hover:text-white transition-colors" />
                </div>
                <div>
                  <h4 className="text-xs font-bold text-white group-hover:text-sage-300 transition-colors">{node.name}</h4>
                  <span className="text-[10px] font-mono text-slate-400 block mt-0.5">Quick Dispatch →</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            CURRENT ACTIVE SERVICE OR ZERO-STATE BANNER
        ────────────────────────────────────────────────────────────────────────── */}
        {/* 🚀 LIVE TRACKING WIDGET */}
        {routingBooking && <LiveTrackingWidget booking={routingBooking} />}

        {/* ⚡ CURRENT ACTIVE SERVICE OR ZERO-STATE BANNER */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
            <span>Current Service Dispatch</span>
          </h2>

          {activeBooking ? (
            <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 shadow-modal flex flex-col md:flex-row items-start md:items-center justify-between gap-6 relative overflow-hidden">
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-sage-400 to-transparent" />

              <div className="space-y-2 max-w-xl">
                <div className="flex items-center gap-3">
                  <span className="text-lg font-bold text-white">
                    {activeBooking.service?.name || 'Home Service'}
                  </span>
                  <StatusBadge status={activeBooking.status} size="sm" />
                </div>

                <p className="text-xs text-slate-400 flex items-center gap-2 font-mono">
                  <span>Booking #{activeBooking.booking_number || activeBooking.id}</span>
                  <span>•</span>
                  <span>
                    {activeBooking.booking_date ? new Date(activeBooking.booking_date).toLocaleDateString() : 'Scheduled'}
                  </span>
                </p>

                {activeBooking.technician ? (
                  <div className="flex items-center gap-3 pt-2">
                    <div className="w-8 h-8 rounded-lg bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 text-xs font-bold">
                      {getTechName(activeBooking.technician).charAt(0)}
                    </div>
                    <div>
                      <p className="text-xs font-semibold text-white">{getTechName(activeBooking.technician)}</p>
                      <span className="text-[10px] text-slate-400 font-mono">Assigned Master Professional</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-xs text-sage-400 font-mono pt-1 flex items-center gap-1.5">
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

                {['assigned', 'accepted', 'in_progress', 'arrived', 'on_the_way'].includes(activeBooking.status) && (
                  <button
                    onClick={() => setVerifyModalBooking(activeBooking)}
                    className="btn-accent text-xs px-5 py-2.5 font-semibold flex items-center gap-1.5 shadow-accent"
                  >
                    <ShieldCheck className="w-4 h-4" />
                    <span>SmartVerify™ Code</span>
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="p-8 rounded-3xl bg-dark-900/60 border border-dark-750 text-center space-y-3">
              <div className="w-12 h-12 rounded-2xl bg-dark-850 border border-dark-750 flex items-center justify-center text-slate-400 mx-auto">
                <CheckCircle2 className="w-6 h-6 text-sage-400" />
              </div>
              <h3 className="text-base font-bold text-white">NO UPCOMING SERVICE</h3>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
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
            <h2 className="text-lg font-bold text-white tracking-tight">Saved Residence Addresses</h2>
            <button
              onClick={() => {
                setEditingAddress(null);
                setAddressModalOpen(true);
              }}
              className="btn-secondary text-xs px-3.5 py-1.5 flex items-center gap-1.5"
            >
              <PlusCircle className="w-3.5 h-3.5 text-sage-400" />
              <span>Add Address</span>
            </button>
          </div>

          {addresses.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {addresses.map((addr) => (
                <div
                  key={addr.id}
                  className="p-5 rounded-2xl bg-dark-900 border border-dark-750 flex flex-col justify-between shadow-card relative group"
                >
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-sage-400" />
                        <span className="text-xs font-bold text-white">{addr.city || 'Residence'}</span>
                      </div>
                      {addr.is_default && (
                        <span className="text-[9px] font-mono px-1.5 py-0.5 rounded bg-sage-400/20 text-sage-300 border border-sage-400/30">
                          DEFAULT
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-slate-300 line-clamp-2 leading-relaxed">
                      {addr.house_no} {addr.building ? `, ${addr.building}` : ''} {addr.area}
                    </p>
                    <p className="text-[11px] font-mono text-slate-400 mt-1">
                      {addr.city}, {addr.pincode}
                    </p>
                  </div>

                  <div className="pt-4 mt-4 border-t border-dark-750 flex items-center justify-end gap-2">
                    <button
                      onClick={() => {
                        setEditingAddress(addr);
                        setAddressModalOpen(true);
                      }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-dark-850"
                      title="Edit"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </button>
                    <button
                      onClick={() => handleDeleteAddress(addr.id)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-dark-850"
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
            SERVICE HISTORY & COMPLETED BOOKINGS TABLE
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-white tracking-tight">Service History</h2>

          {pastBookings.length > 0 ? (
            <div className="rounded-3xl bg-dark-900 border border-dark-750 overflow-hidden shadow-card">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-dark-850 border-b border-dark-750 text-slate-400 font-mono uppercase text-[10px]">
                    <tr>
                      <th className="py-3.5 px-4">Booking Ref</th>
                      <th className="py-3.5 px-4">Service</th>
                      <th className="py-3.5 px-4">Date</th>
                      <th className="py-3.5 px-4">Status</th>
                      <th className="py-3.5 px-4">Amount</th>
                      <th className="py-3.5 px-4 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-dark-750/70 text-slate-300">
                    {pastBookings.map((b) => (
                      <tr key={b.id} className="hover:bg-dark-850/50 transition-colors">
                        <td className="py-3.5 px-4 font-mono font-medium text-white">
                          #{b.booking_number || b.id}
                        </td>
                        <td className="py-3.5 px-4 font-semibold text-white">
                          {b.service?.name || 'Service Order'}
                        </td>
                        <td className="py-3.5 px-4 text-slate-400">
                          {b.booking_date ? new Date(b.booking_date).toLocaleDateString() : '—'}
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={b.status} size="sm" />
                        </td>
                        <td className="py-3.5 px-4 font-mono font-bold text-white">
                          ₹{(b.final_price || b.total_amount || b.estimated_price || 0).toFixed(2)}
                        </td>
                        <td className="py-3.5 px-4 text-right space-x-2">
                          <button
                            onClick={() => setSelectedBooking(b)}
                            className="px-2.5 py-1 rounded-lg bg-dark-800 hover:bg-dark-750 text-slate-200 border border-dark-750 text-[11px]"
                          >
                            Details
                          </button>
                          {b.status === 'completed' && (
                            <button
                              onClick={() => setReviewModalBooking(b)}
                              className="px-2.5 py-1 rounded-lg bg-sage-400/15 hover:bg-sage-400/25 text-sage-300 border border-sage-400/30 text-[11px]"
                            >
                              Review
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
            <div className="p-8 rounded-2xl bg-dark-900/50 border border-dark-750 text-center text-xs text-slate-400">
              No historical services recorded yet. Your completed bookings and workmanship reports will appear here.
            </div>
          )}        </div>
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
          onOpenTracking={() => {
            setTrackingModalBooking(selectedBooking);
            setSelectedBooking(null);
          }}
        />
      )}

      <LiveTrackingModal
        booking={trackingModalBooking}
        isOpen={!!trackingModalBooking}
        onClose={() => setTrackingModalBooking(null)}
      />

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
    </div>
  );
};



