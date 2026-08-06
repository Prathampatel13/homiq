import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  Calendar,
  Clock,
  MapPin,
  QrCode,
  Star,
  Plus,
  Wrench,
  X,
  AlertCircle,
  Home,
  CheckCircle2,
} from 'lucide-react';
import { bookingApi } from '../api/booking';
import { addressApi } from '../api/address';
import { Booking, BookingStatus, CustomerAddress } from '../types';
import { useAuthStore } from '../store/useAuthStore';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { AddressModal } from '../components/modals/AddressModal';
import { ReviewModal } from '../components/modals/ReviewModal';

export const CustomerDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeQRBooking, setActiveQRBooking] = useState<Booking | null>(null);
  
  // Modals state
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [reviewModalState, setReviewModalState] = useState<{
    isOpen: boolean;
    bookingId: number;
    serviceName: string;
  }>({
    isOpen: false,
    bookingId: 0,
    serviceName: '',
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const [bookingsData, addressesData] = await Promise.all([
        bookingApi.getCustomerBookings(),
        addressApi.getAddresses().catch(() => []),
      ]);
      setBookings(Array.isArray(bookingsData) ? bookingsData : []);
      setAddresses(Array.isArray(addressesData) ? addressesData : []);
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddressCreated = (newAddr: CustomerAddress) => {
    setAddresses((prev) => [newAddr, ...prev]);
  };

  const safeBookings = Array.isArray(bookings) ? bookings : [];
  const activeBookings = safeBookings.filter(
    (b) => b.status !== BookingStatus.COMPLETED && b.status !== BookingStatus.CANCELLED
  );
  const completedBookings = safeBookings.filter(
    (b) => b.status === BookingStatus.COMPLETED
  );

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* ── 1. Welcome Banner ────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 glass-card p-8 border-brand-500/20">
        <div className="space-y-2">
          <h1 className="text-3xl font-extrabold text-white">
            Hello, <span className="gradient-text">{user?.full_name || 'Customer'}</span> 👋
          </h1>
          <p className="text-slate-400 text-sm">
            Manage your house maintenance requests, track technicians in real-time, and manage delivery addresses.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="md"
            leftIcon={<Home className="w-4 h-4" />}
            onClick={() => setIsAddressModalOpen(true)}
          >
            Add Address
          </Button>
          <Link to="/booking/new">
            <Button variant="primary" size="md" leftIcon={<Plus className="w-4 h-4" />}>
              New Maintenance Booking
            </Button>
          </Link>
        </div>
      </div>

      {/* ── 2. Active Bookings Section ───────────────────────────────────────── */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Clock className="w-5 h-5 text-brand-400" />
            Active Service Requests ({activeBookings.length})
          </h2>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2].map((i) => (
              <div key={i} className="glass-card p-6 h-48 animate-pulse bg-slate-900/50" />
            ))}
          </div>
        ) : activeBookings.length === 0 ? (
          <Card className="text-center py-12 space-y-3">
            <Wrench className="w-8 h-8 text-slate-500 mx-auto" />
            <div className="text-slate-300 font-semibold text-sm">No Active Maintenance Requests</div>
            <p className="text-slate-500 text-xs">Need an electrician, plumber, or cleaning? Book instantly.</p>
            <Link to="/booking/new" className="inline-block pt-2">
              <Button variant="primary" size="sm">
                Book a Service
              </Button>
            </Link>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {activeBookings.map((b) => (
              <motion.div key={b.id} whileHover={{ y: -2 }} transition={{ duration: 0.2 }}>
                <Card className="space-y-5 border-slate-800 relative overflow-hidden">
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="text-xs font-mono text-brand-400 font-semibold">#{b.booking_number}</span>
                      <h3 className="text-lg font-bold text-white mt-1">{b.service?.name || 'Maintenance Service'}</h3>
                    </div>
                    <Badge status={b.status} />
                  </div>

                  <div className="grid grid-cols-2 gap-3 text-xs text-slate-300 bg-slate-950/60 p-4 rounded-xl border border-slate-800/80">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-brand-400 shrink-0" />
                      <span>{b.booking_date}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Clock className="w-4 h-4 text-brand-400 shrink-0" />
                      <span>{b.preferred_time}</span>
                    </div>
                    <div className="flex items-center gap-2 col-span-2">
                      <MapPin className="w-4 h-4 text-brand-400 shrink-0" />
                      <span className="truncate">
                        {b.address ? `${b.address.house_no}, ${b.address.area}, ${b.address.city}` : 'Default Customer Address'}
                      </span>
                    </div>
                  </div>

                  <div className="pt-2 flex items-center justify-between border-t border-slate-800/60">
                    <div>
                      <div className="text-[10px] text-slate-400 uppercase font-semibold">Escrow Price</div>
                      <div className="text-base font-extrabold text-white">₹{b.final_price}</div>
                    </div>
                    {b.qr_code && (
                      <Button
                        variant="glass"
                        size="sm"
                        leftIcon={<QrCode className="w-4 h-4 text-brand-400" />}
                        onClick={() => setActiveQRBooking(b)}
                      >
                        View Verification QR
                      </Button>
                    )}
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      {/* ── 3. Saved Delivery Addresses ─────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <MapPin className="w-5 h-5 text-brand-400" />
            Saved Delivery Addresses ({addresses.length})
          </h2>
          <button
            onClick={() => setIsAddressModalOpen(true)}
            className="text-xs font-semibold text-brand-400 hover:text-brand-300 flex items-center gap-1 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" /> Add New Address
          </button>
        </div>

        {addresses.length === 0 ? (
          <Card className="text-center py-6 text-xs text-slate-400">
            No saved addresses found. Click "Add New Address" to save your primary home location.
          </Card>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {addresses.map((addr) => (
              <Card key={addr.id} className="p-4 space-y-2 border-slate-800 text-xs">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-white">{addr.full_name}</span>
                  {addr.is_default && (
                    <span className="px-2 py-0.5 rounded-full bg-brand-500/10 text-brand-400 border border-brand-500/20 text-[10px] font-semibold">
                      Default
                    </span>
                  )}
                </div>
                <p className="text-slate-400">{addr.house_no}, {addr.area}</p>
                <p className="text-slate-500">{addr.city}, {addr.state} - {addr.pincode}</p>
                <div className="text-slate-400 pt-1 font-mono">{addr.phone}</div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* ── 4. Completed History & Rating ────────────────────────────────────── */}
      {completedBookings.length > 0 && (
        <div className="space-y-6 pt-4">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
            Completed Service History ({completedBookings.length})
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {completedBookings.map((b) => (
              <Card key={b.id} className="space-y-4 border-slate-800">
                <div className="flex items-start justify-between">
                  <div>
                    <span className="text-xs font-mono text-slate-500">#{b.booking_number}</span>
                    <h3 className="text-base font-bold text-white mt-0.5">{b.service?.name || 'Completed Job'}</h3>
                  </div>
                  <Badge status={b.status} />
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400 pt-2 border-t border-slate-800">
                  <span>Completed on {b.booking_date}</span>
                  <Button
                    variant="glass"
                    size="sm"
                    leftIcon={<Star className="w-3.5 h-3.5 text-amber-400 fill-amber-400" />}
                    onClick={() =>
                      setReviewModalState({
                        isOpen: true,
                        bookingId: b.id,
                        serviceName: b.service?.name || 'Maintenance Service',
                      })
                    }
                  >
                    Rate Service
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* ── 5. QR Code Modal Viewer ──────────────────────────────────────────── */}
      {activeQRBooking && (
        <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4 z-50">
          <motion.div
            initial={{ scale: 0.95, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className="glass-card p-6 max-w-sm w-full space-y-6 text-center relative border-slate-800"
          >
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h3 className="text-sm font-bold text-white">SmartVerify QR Code</h3>
              <button onClick={() => setActiveQRBooking(null)} className="text-slate-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-4 bg-white rounded-2xl inline-block shadow-xl shadow-brand-500/10 mx-auto">
              <img
                src={`https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=${encodeURIComponent(
                  activeQRBooking.qr_code || ''
                )}`}
                alt="Verification QR Code"
                className="w-44 h-44 mx-auto"
              />
            </div>

            <div className="space-y-1.5">
              <p className="text-xs text-slate-300 font-semibold">Show this QR to your assigned technician</p>
              <p className="text-[11px] text-slate-500">
                Technician will scan this code to securely start service.
              </p>
            </div>
          </motion.div>
        </div>
      )}

      {/* Address Creation Modal */}
      <AddressModal
        isOpen={isAddressModalOpen}
        onClose={() => setIsAddressModalOpen(false)}
        onAddressCreated={handleAddressCreated}
      />

      {/* Review Submission Modal */}
      <ReviewModal
        isOpen={reviewModalState.isOpen}
        bookingId={reviewModalState.bookingId}
        serviceName={reviewModalState.serviceName}
        onClose={() => setReviewModalState({ isOpen: false, bookingId: 0, serviceName: '' })}
        onReviewSubmitted={() => {
          fetchData();
        }}
      />
    </div>
  );
};
