import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Calendar,
  Clock,
  MapPin,
  Plus,
  QrCode,
  ShieldCheck,
  CreditCard,
  Bell,
  User as UserIcon,
  Phone,
  Trash2,
  Edit2,
  CheckCircle2,
  FileText,
  AlertTriangle,
  Star,
  ChevronRight,
  TrendingUp,
} from 'lucide-react';
import { customerApi, CustomerProfile } from '../api/customer';
import { bookingsApi } from '../api/bookings';
import { paymentsApi } from '../api/payments';
import { notificationsApi } from '../api/notifications';
import { Booking, CustomerAddress, NotificationItem, Payment } from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatsCard } from '../components/ui/StatsCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs } from '../components/ui/Tabs';
import { AddressModal } from '../components/modals/AddressModal';
import { SmartVerifyModal } from '../components/modals/SmartVerifyModal';
import { BookingDetailsModal } from '../components/modals/BookingDetailsModal';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { Input } from '../components/ui/Input';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';
import { useAuthStore } from '../store/useAuthStore';

export const CustomerDashboard: React.FC = () => {
  const navigate = useNavigate();
  const toast = useToast();
  const { user, updateUser } = useAuthStore();

  const [activeTab, setActiveTab] = useState('bookings');
  const [bookingFilter, setBookingFilter] = useState('all');

  const [profile, setProfile] = useState<CustomerProfile | null>(null);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [addresses, setAddresses] = useState<CustomerAddress[]>([]);
  const [payments, setPayments] = useState<Payment[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Selected booking for detailed drawer / verify modal
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [isDetailsModalOpen, setIsDetailsModalOpen] = useState(false);
  const [isVerifyModalOpen, setIsVerifyModalOpen] = useState(false);

  // Address modal
  const [isAddressModalOpen, setIsAddressModalOpen] = useState(false);
  const [addressToEdit, setAddressToEdit] = useState<CustomerAddress | null>(null);

  // Profile edit state
  const [profileForm, setProfileForm] = useState({
    full_name: '',
    phone: '',
    city: '',
    state: '',
    postal_code: '',
  });
  const [isSavingProfile, setIsSavingProfile] = useState(false);

  const fetchDashboardData = useCallback(async () => {
    try {
      const [profData, bookingsData, addrData, notifData, payData] = await Promise.all([
        customerApi.getProfile().catch(() => null),
        bookingsApi.getBookings().catch(() => []),
        customerApi.getAddresses().catch(() => []),
        notificationsApi.getNotifications().catch(() => []),
        paymentsApi.getHistory().catch(() => []),
      ]);

      if (profData) {
        setProfile(profData);
        setProfileForm({
          full_name: profData.full_name || '',
          phone: profData.phone || '',
          city: profData.city || '',
          state: profData.state || '',
          postal_code: profData.postal_code || '',
        });
      }

      setBookings(Array.isArray(bookingsData) ? bookingsData : (bookingsData as any).items || []);
      setAddresses(addrData);
      setNotifications(Array.isArray(notifData) ? notifData : (notifData as any).notifications || []);
      setPayments(Array.isArray(payData) ? payData : (payData as any).items || []);
    } catch (err) {
      toast.error('Could not refresh dashboard data', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  // Derived metrics
  const activeBookings = bookings.filter((b) =>
    ['pending', 'assigned', 'accepted', 'on_the_way', 'arrived', 'waiting_qr', 'qr_verified', 'in_progress'].includes(
      String(b.status).toLowerCase()
    )
  );

  const completedBookings = bookings.filter((b) => String(b.status).toLowerCase() === 'completed');

  const totalSpent = bookings
    .filter((b) => String(b.status).toLowerCase() === 'completed')
    .reduce((sum, b) => sum + (b.final_price || b.base_price || b.estimated_price || 0), 0);

  // In-flight spotlight booking (the first active job)
  const inFlightBooking = activeBookings[0] || null;

  const filteredBookings = bookings.filter((b) => {
    if (bookingFilter === 'all') return true;
    if (bookingFilter === 'active') {
      return ['pending', 'assigned', 'accepted', 'on_the_way', 'arrived', 'waiting_qr', 'qr_verified', 'in_progress'].includes(
        String(b.status).toLowerCase()
      );
    }
    if (bookingFilter === 'completed') return String(b.status).toLowerCase() === 'completed';
    if (bookingFilter === 'cancelled') return ['cancelled', 'rejected'].includes(String(b.status).toLowerCase());
    return true;
  });

  const handleSetDefaultAddress = async (id: number) => {
    try {
      await customerApi.setDefaultAddress(id);
      toast.success('Address Updated', 'Set as default delivery location.');
      fetchDashboardData();
    } catch (err) {
      toast.error('Failed to set default address', extractErrorMessage(err));
    }
  };

  const handleDeleteAddress = async (id: number) => {
    if (!window.confirm('Delete this saved address?')) return;
    try {
      await customerApi.deleteAddress(id);
      toast.success('Address Removed');
      fetchDashboardData();
    } catch (err) {
      toast.error('Failed to delete address', extractErrorMessage(err));
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSavingProfile(true);
    try {
      const updated = await customerApi.updateProfile(profileForm);
      setProfile(updated);
      updateUser({ full_name: updated.full_name, phone: updated.phone });
      toast.success('Profile Updated', 'Your customer settings have been saved.');
    } catch (err) {
      toast.error('Failed to update profile', extractErrorMessage(err));
    } finally {
      setIsSavingProfile(false);
    }
  };

  const handleMarkNotificationRead = async (id: number) => {
    try {
      await notificationsApi.markRead(id);
      setNotifications((prev) => prev.map((n) => (n.id === id ? { ...n, is_read: true } : n)));
    } catch (err) {
      toast.error('Notification update error', extractErrorMessage(err));
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <LoadingState message="Loading your customer control center..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header & Quick Action */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-dark-750">
        <div>
          <p className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold mb-1">
            Customer Control Center
          </p>
          <h1 className="text-3xl font-bold text-white tracking-tight">
            Welcome back, {user?.full_name || 'Customer'}
          </h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Manage your home bookings, SmartVerify security handshakes, and service history.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          leftIcon={Plus}
          onClick={() => navigate('/booking/new')}
        >
          Book New Service
        </Button>
      </div>

      {/* KPI METRICS OVERVIEW */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          label="Total Bookings"
          value={bookings.length}
          icon={Calendar}
          subtext="Lifetime service orders"
        />
        <StatsCard
          label="Active Jobs"
          value={activeBookings.length}
          icon={Clock}
          subtext="In-flight or scheduled"
        />
        <StatsCard
          label="Completed"
          value={completedBookings.length}
          icon={CheckCircle2}
          subtext="Verified & closed"
        />
        <StatsCard
          label="Total Spend"
          value={`₹${totalSpent.toFixed(2)}`}
          icon={CreditCard}
          subtext="Completed jobs"
        />
      </div>

      {/* IN-FLIGHT SPOTLIGHT (IF ACTIVE SERVICE EXISTS) */}
      {inFlightBooking && (
        <Card className="p-6 bg-gradient-to-r from-dark-900 via-dark-850 to-dark-900 border-brand-500/30 relative overflow-hidden">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-brand-500/15 text-brand-400 border border-brand-500/30 animate-pulse">
                  IN-FLIGHT ACTIVE SERVICE
                </span>
                <StatusBadge status={inFlightBooking.status} />
              </div>

              <div>
                <h3 className="text-xl font-bold text-white">
                  {inFlightBooking.service?.name || 'Home Maintenance Service'}
                </h3>
                <p className="text-xs text-slate-300 mt-1">
                  Scheduled for <span className="font-semibold text-white">{inFlightBooking.booking_date}</span> at{' '}
                  <span className="font-semibold text-white">{inFlightBooking.preferred_time}</span>
                </p>
              </div>

              {inFlightBooking.address && (
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <MapPin className="w-3.5 h-3.5 text-brand-400" />
                  <span>
                    {inFlightBooking.address.house_no}, {inFlightBooking.address.area}, {inFlightBooking.address.city}
                  </span>
                </div>
              )}
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <Button
                variant="primary"
                size="md"
                leftIcon={QrCode}
                onClick={() => {
                  setSelectedBooking(inFlightBooking);
                  setIsVerifyModalOpen(true);
                }}
              >
                SmartVerify QR
              </Button>

              <Button
                variant="secondary"
                size="md"
                onClick={() => {
                  setSelectedBooking(inFlightBooking);
                  setIsDetailsModalOpen(true);
                }}
              >
                View Full Details
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* DASHBOARD TABS */}
      <div className="space-y-6">
        <Tabs
          tabs={[
            { id: 'bookings', label: 'My Bookings', count: bookings.length },
            { id: 'addresses', label: 'Saved Addresses', count: addresses.length },
            { id: 'payments', label: 'Payments & Receipts', count: payments.length },
            { id: 'notifications', label: 'Notifications', count: notifications.filter((n) => !n.is_read).length },
            { id: 'profile', label: 'Profile Settings' },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          variant="underline"
        />

        {/* TAB 1: BOOKINGS */}
        {activeTab === 'bookings' && (
          <div className="space-y-6">
            {/* Filter pills */}
            <div className="flex items-center gap-2">
              {[
                { id: 'all', label: 'All' },
                { id: 'active', label: 'Active' },
                { id: 'completed', label: 'Completed' },
                { id: 'cancelled', label: 'Cancelled' },
              ].map((f) => (
                <button
                  key={f.id}
                  onClick={() => setBookingFilter(f.id)}
                  className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                    bookingFilter === f.id
                      ? 'bg-dark-800 text-white border border-dark-700'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {filteredBookings.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredBookings.map((b) => (
                  <Card
                    key={b.id}
                    className="p-5 flex flex-col justify-between hover:border-dark-750 group"
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="text-[11px] font-mono text-slate-500 block">
                            #{b.booking_number || b.id}
                          </span>
                          <h4 className="text-sm font-bold text-white group-hover:text-brand-400 transition-colors">
                            {b.service?.name || 'Home Maintenance'}
                          </h4>
                        </div>
                        <StatusBadge status={b.status} />
                      </div>

                      <div className="grid grid-cols-2 gap-2 text-xs text-slate-300 py-1">
                        <div className="flex items-center gap-1.5">
                          <Calendar className="w-3.5 h-3.5 text-brand-400" />
                          <span>{b.booking_date}</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                          <Clock className="w-3.5 h-3.5 text-brand-400" />
                          <span>{b.preferred_time}</span>
                        </div>
                      </div>

                      {b.address && (
                        <p className="text-xs text-slate-400 truncate">
                          📍 {b.address.house_no}, {b.address.area}
                        </p>
                      )}
                    </div>

                    <div className="pt-4 mt-4 border-t border-dark-800/80 flex items-center justify-between">
                      <div>
                        <span className="text-[10px] text-slate-500 block">Total Fare</span>
                        <span className="text-base font-bold text-white font-mono">
                          ₹{(b.final_price || b.base_price || b.estimated_price || 0).toFixed(2)}
                        </span>
                      </div>

                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => {
                          setSelectedBooking(b);
                          setIsDetailsModalOpen(true);
                        }}
                      >
                        Inspect
                      </Button>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Calendar}
                title="No bookings in this category"
                description="Schedule a vetted technician for any home repair or installation."
                actionLabel="Book a Service"
                onAction={() => navigate('/booking/new')}
              />
            )}
          </div>
        )}

        {/* TAB 2: SAVED ADDRESSES */}
        {activeTab === 'addresses' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-white">Your Service Addresses</h3>
              <Button
                variant="primary"
                size="sm"
                leftIcon={Plus}
                onClick={() => {
                  setAddressToEdit(null);
                  setIsAddressModalOpen(true);
                }}
              >
                Add Address
              </Button>
            </div>

            {addresses.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {addresses.map((addr) => (
                  <Card key={addr.id} className="p-5 flex flex-col justify-between space-y-4">
                    <div className="space-y-2">
                      <div className="flex justify-between items-start">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-brand-400" />
                          <h4 className="text-sm font-bold text-white">{addr.full_name}</h4>
                        </div>
                        {addr.is_default && (
                          <span className="px-2 py-0.5 rounded text-[10px] bg-brand-500/15 text-brand-400 border border-brand-500/30">
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
                      <p className="text-[11px] text-slate-500 font-mono">Contact: {addr.phone}</p>
                    </div>

                    <div className="pt-3 border-t border-dark-800 flex items-center justify-between text-xs">
                      {!addr.is_default && (
                        <button
                          onClick={() => handleSetDefaultAddress(addr.id)}
                          className="text-brand-400 hover:text-brand-300 font-medium"
                        >
                          Make Default
                        </button>
                      )}
                      <div className="flex items-center gap-3 ml-auto">
                        <button
                          onClick={() => {
                            setAddressToEdit(addr);
                            setIsAddressModalOpen(true);
                          }}
                          className="text-slate-400 hover:text-white p-1"
                        >
                          <Edit2 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => handleDeleteAddress(addr.id)}
                          className="text-rose-400 hover:text-rose-300 p-1"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={MapPin}
                title="No saved addresses"
                description="Save your home or office address for 1-click future bookings."
                actionLabel="Add Address"
                onAction={() => {
                  setAddressToEdit(null);
                  setIsAddressModalOpen(true);
                }}
              />
            )}
          </div>
        )}

        {/* TAB 3: PAYMENTS & INVOICES */}
        {activeTab === 'payments' && (
          <div className="space-y-6">
            <h3 className="text-base font-bold text-white">Payment Receipts & Invoices</h3>
            {payments.length > 0 ? (
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl divide-y divide-dark-800">
                {payments.map((p) => (
                  <div key={p.id} className="py-3.5 flex items-center justify-between text-xs">
                    <div className="space-y-0.5">
                      <p className="font-bold text-white font-mono">Payment #{p.id}</p>
                      <p className="text-[11px] text-slate-400">
                        {new Date(p.created_at).toLocaleDateString()} via {p.payment_method || 'Online'}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-white font-mono text-sm">₹{p.amount.toFixed(2)}</p>
                      <span className="inline-block px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase">
                        {p.status}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={CreditCard}
                title="No payments found"
                description="Your transaction receipts and tax invoices will appear here."
              />
            )}
          </div>
        )}

        {/* TAB 4: NOTIFICATIONS */}
        {activeTab === 'notifications' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-white">Recent Updates</h3>
              {notifications.some((n) => !n.is_read) && (
                <button
                  onClick={async () => {
                    await notificationsApi.markAllRead();
                    setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })));
                    toast.success('All marked as read');
                  }}
                  className="text-xs text-brand-400 hover:text-brand-300 font-medium"
                >
                  Mark all as read
                </button>
              )}
            </div>

            {notifications.length > 0 ? (
              <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl divide-y divide-dark-800">
                {notifications.map((n) => (
                  <div
                    key={n.id}
                    onClick={() => handleMarkNotificationRead(n.id)}
                    className={`py-3 flex items-start justify-between gap-4 cursor-pointer transition-colors ${
                      n.is_read ? 'opacity-70' : 'opacity-100'
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={`w-2 h-2 rounded-full mt-1.5 flex-shrink-0 ${
                          n.is_read ? 'bg-dark-750' : 'bg-brand-400'
                        }`}
                      />
                      <div>
                        <h5 className="text-xs font-bold text-white">{n.title}</h5>
                        <p className="text-xs text-slate-400 mt-0.5">{n.message}</p>
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono flex-shrink-0">
                      {new Date(n.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                icon={Bell}
                title="No new notifications"
                description="You are completely caught up with your service alerts."
              />
            )}
          </div>
        )}

        {/* TAB 5: PROFILE SETTINGS */}
        {activeTab === 'profile' && (
          <div className="max-w-2xl space-y-6">
            <h3 className="text-base font-bold text-white">Customer Account Details</h3>
            <form onSubmit={handleSaveProfile} className="space-y-4">
              <Input
                label="Full Name"
                value={profileForm.full_name}
                onChange={(e) => setProfileForm({ ...profileForm, full_name: e.target.value })}
                required
              />
              <Input
                label="Registered Email"
                value={user?.email || ''}
                disabled
                helperText="Email address cannot be changed."
              />
              <Input
                label="Primary Phone Number"
                value={profileForm.phone}
                onChange={(e) => setProfileForm({ ...profileForm, phone: e.target.value })}
              />

              <div className="grid grid-cols-3 gap-3">
                <Input
                  label="City"
                  value={profileForm.city}
                  onChange={(e) => setProfileForm({ ...profileForm, city: e.target.value })}
                />
                <Input
                  label="State"
                  value={profileForm.state}
                  onChange={(e) => setProfileForm({ ...profileForm, state: e.target.value })}
                />
                <Input
                  label="Postal Code"
                  value={profileForm.postal_code}
                  onChange={(e) => setProfileForm({ ...profileForm, postal_code: e.target.value })}
                />
              </div>

              <div className="pt-3">
                <Button variant="primary" size="md" type="submit" isLoading={isSavingProfile}>
                  Save Profile Changes
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Detailed Booking Modal */}
      <BookingDetailsModal
        isOpen={isDetailsModalOpen}
        onClose={() => {
          setIsDetailsModalOpen(false);
          setSelectedBooking(null);
        }}
        booking={selectedBooking}
        onBookingUpdated={fetchDashboardData}
      />

      {/* SmartVerify Modal */}
      {selectedBooking && (
        <SmartVerifyModal
          isOpen={isVerifyModalOpen}
          onClose={() => {
            setIsVerifyModalOpen(false);
            setSelectedBooking(null);
          }}
          booking={selectedBooking}
          onVerified={fetchDashboardData}
        />
      )}

      {/* Address Create/Edit Modal */}
      <AddressModal
        isOpen={isAddressModalOpen}
        onClose={() => {
          setIsAddressModalOpen(false);
          setAddressToEdit(null);
        }}
        addressToEdit={addressToEdit}
        onSuccess={fetchDashboardData}
      />
    </div>
  );
};
