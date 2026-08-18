import React, { useState, useEffect, useCallback } from 'react';
import {
  Users,
  Briefcase,
  Calendar,
  DollarSign,
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Settings,
  Plus,
  Trash2,
  Edit2,
  Tag,
  FileCheck,
  RefreshCw,
  Search,
  Eye,
} from 'lucide-react';
import { adminApi, AdminDashboardData, AdminTechnicianDoc } from '../api/admin';
import { servicesApi } from '../api/services';
import { couponsApi } from '../api/coupons';
import {
  AdminSettings,
  AnalyticsOverview,
  Booking,
  Coupon,
  Service,
  ServiceCategory,
  TechnicianProfile,
  User,
} from '../types';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { StatsCard } from '../components/ui/StatsCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Tabs } from '../components/ui/Tabs';
import { Input } from '../components/ui/Input';
import { Modal } from '../components/ui/Modal';
import { LoadingState } from '../components/ui/LoadingState';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../components/ui/Toast';
import { extractErrorMessage } from '../api/axios';

export const AdminDashboard: React.FC = () => {
  const toast = useToast();

  const [activeTab, setActiveTab] = useState('overview');
  const [dashboardData, setDashboardData] = useState<AdminDashboardData | null>(null);
  const [users, setUsers] = useState<User[]>([]);
  const [technicians, setTechnicians] = useState<TechnicianProfile[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [settings, setSettings] = useState<AdminSettings | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [actionLoadingId, setActionLoadingId] = useState<number | null>(null);

  // Modals
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [newCatName, setNewCatName] = useState('');
  const [newCatDesc, setNewCatDesc] = useState('');

  const [isServiceModalOpen, setIsServiceModalOpen] = useState(false);
  const [serviceForm, setServiceForm] = useState({
    name: '',
    description: '',
    category_id: 1,
    price: 499,
    duration_minutes: 60,
    is_active: true,
  });

  const [isCouponModalOpen, setIsCouponModalOpen] = useState(false);
  const [couponForm, setCouponForm] = useState({
    code: '',
    discount_type: 'percentage',
    discount_value: 10,
    max_discount_amount: 200,
    min_order_amount: 499,
    valid_from: new Date().toISOString().split('T')[0],
    valid_until: new Date(Date.now() + 30 * 86400000).toISOString().split('T')[0],
    is_active: true,
  });

  // Settings form
  const [commissionPct, setCommissionPct] = useState(15);
  const [taxPct, setTaxPct] = useState(18);

  // Status override modal
  const [selectedBookingForOverride, setSelectedBookingForOverride] = useState<Booking | null>(null);
  const [overrideStatusVal, setOverrideStatusVal] = useState('completed');
  const [overrideNote, setOverrideNote] = useState('');

  // Selected tech for doc review
  const [selectedTechDocs, setSelectedTechDocs] = useState<{ tech: TechnicianProfile; docs: AdminTechnicianDoc[] } | null>(null);

  const fetchAdminData = useCallback(async () => {
    try {
      const [dash, usersData, techsData, bookingsData, catsData, srvsData, cpnData, settingsData] =
        await Promise.all([
          adminApi.getDashboard().catch(() => null),
          adminApi.getUsers().catch(() => []),
          adminApi.getTechnicians().catch(() => []),
          adminApi.getBookings().catch(() => []),
          servicesApi.getCategories().catch(() => []),
          servicesApi.getServices().catch(() => []),
          couponsApi.getCoupons().catch(() => []),
          adminApi.getSettings().catch(() => null),
        ]);

      if (dash) setDashboardData(dash);
      setUsers(Array.isArray(usersData) ? usersData : []);
      setTechnicians(Array.isArray(techsData) ? techsData : []);
      setBookings(Array.isArray(bookingsData) ? bookingsData : []);
      setCategories(catsData);
      setServices(srvsData);
      setCoupons(Array.isArray(cpnData) ? cpnData : (cpnData as any).items || []);
      if (settingsData) {
        setSettings(settingsData);
        setCommissionPct(settingsData.commission_percentage || 15);
        setTaxPct(settingsData.tax_percentage || 18);
      }
    } catch (err) {
      toast.error('Failed to load admin dataset', extractErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    fetchAdminData();
  }, [fetchAdminData]);

  // User Actions
  const handleToggleUserSuspend = async (user: User) => {
    try {
      if (user.is_active) {
        await adminApi.suspendUser(user.id);
        toast.info('User Suspended', `${user.full_name} has been deactivated.`);
      } else {
        await adminApi.activateUser(user.id);
        toast.success('User Activated', `${user.full_name} has been reactivated.`);
      }
      fetchAdminData();
    } catch (err) {
      toast.error('User action failed', extractErrorMessage(err));
    }
  };

  // Technician Verification
  const handleApproveTech = async (techId: number) => {
    setActionLoadingId(techId);
    try {
      await adminApi.approveTechnician(techId);
      toast.success('Technician Approved', 'Verified pro status granted.');
      fetchAdminData();
    } catch (err) {
      toast.error('Approval failed', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRejectTech = async (techId: number) => {
    setActionLoadingId(techId);
    try {
      await adminApi.rejectTechnician(techId);
      toast.info('Technician Rejected');
      fetchAdminData();
    } catch (err) {
      toast.error('Rejection failed', extractErrorMessage(err));
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleInspectTechDocs = async (tech: TechnicianProfile) => {
    try {
      const docs = await adminApi.getTechnicianDocs(tech.id);
      setSelectedTechDocs({ tech, docs });
    } catch (err) {
      toast.error('Could not load credentials', extractErrorMessage(err));
    }
  };

  const handleApproveDoc = async (docId: number) => {
    try {
      await adminApi.approveDoc(docId);
      toast.success('Document Verified');
      if (selectedTechDocs) {
        handleInspectTechDocs(selectedTechDocs.tech);
      }
    } catch (err) {
      toast.error('Doc approval failed', extractErrorMessage(err));
    }
  };

  // Booking Override
  const handleExecuteStatusOverride = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBookingForOverride) return;

    try {
      await adminApi.overrideBookingStatus(
        selectedBookingForOverride.id,
        overrideStatusVal,
        overrideNote || 'Admin emergency override'
      );
      toast.success('Status Overridden', `Booking #${selectedBookingForOverride.id} updated.`);
      setSelectedBookingForOverride(null);
      fetchAdminData();
    } catch (err) {
      toast.error('Override failed', extractErrorMessage(err));
    }
  };

  // Service CRUD
  const handleCreateCategory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newCatName.trim()) return;
    try {
      await servicesApi.createCategory({
        name: newCatName.trim(),
        description: newCatDesc.trim(),
        is_active: true,
      });
      toast.success('Category Created');
      setIsCategoryModalOpen(false);
      setNewCatName('');
      setNewCatDesc('');
      fetchAdminData();
    } catch (err) {
      toast.error('Category creation failed', extractErrorMessage(err));
    }
  };

  const handleCreateService = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await servicesApi.createService(serviceForm);
      toast.success('Service Catalog Item Added');
      setIsServiceModalOpen(false);
      fetchAdminData();
    } catch (err) {
      toast.error('Service creation failed', extractErrorMessage(err));
    }
  };

  // Coupon CRUD
  const handleCreateCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!couponForm.code.trim()) return;
    try {
      await couponsApi.createCoupon({
        ...couponForm,
        code: couponForm.code.trim().toUpperCase(),
      });
      toast.success('Promotion Created', `Code ${couponForm.code.toUpperCase()} is active.`);
      setIsCouponModalOpen(false);
      fetchAdminData();
    } catch (err) {
      toast.error('Coupon creation failed', extractErrorMessage(err));
    }
  };

  const handleDeleteCoupon = async (id: number) => {
    try {
      await couponsApi.deleteCoupon(id);
      toast.success('Coupon Removed');
      fetchAdminData();
    } catch (err) {
      toast.error('Failed to delete coupon', extractErrorMessage(err));
    }
  };

  // Save Settings
  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const updated = await adminApi.updateSettings({
        commission_percentage: commissionPct,
        tax_percentage: taxPct,
      });
      setSettings(updated);
      toast.success('System Settings Saved');
    } catch (err) {
      toast.error('Failed to save settings', extractErrorMessage(err));
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-20">
        <LoadingState message="Loading administrative operations suite..." />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-dark-750">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-mono uppercase tracking-widest text-brand-400 font-semibold">
              Root Administration
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] bg-brand-500/10 text-brand-400 border border-brand-500/20 font-mono">
              PRO-OPS
            </span>
          </div>
          <h1 className="text-3xl font-bold text-white tracking-tight">Executive Command Center</h1>
          <p className="text-xs sm:text-sm text-slate-400 mt-1">
            Real-time platform governance, user access management, document verification & dispatch overrides.
          </p>
        </div>

        <Button variant="outline" size="sm" leftIcon={RefreshCw} onClick={fetchAdminData}>
          Refresh Telemetry
        </Button>
      </div>

      {/* KPI METRICS OVERVIEW */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatsCard
          label="Registered Users"
          value={dashboardData?.total_users || users.length}
          icon={Users}
          subtext="Customers & providers"
        />
        <StatsCard
          label="Technicians"
          value={dashboardData?.total_technicians || technicians.length}
          icon={Briefcase}
          subtext={`${technicians.filter((t) => !t.is_verified).length} pending audit`}
        />
        <StatsCard
          label="Total Bookings"
          value={dashboardData?.total_bookings || bookings.length}
          icon={Calendar}
          subtext="Gross service volume"
        />
        <StatsCard
          label="Gross Revenue"
          value={`₹${(dashboardData?.total_revenue || 0).toFixed(2)}`}
          icon={DollarSign}
          subtext="Platform ledger"
        />
      </div>

      {/* TABS */}
      <div className="space-y-6">
        <Tabs
          tabs={[
            { id: 'overview', label: 'Platform Overview' },
            { id: 'users', label: 'Users Directory', count: users.length },
            { id: 'technicians', label: 'Technician Verification', count: technicians.length },
            { id: 'bookings', label: 'Bookings Dispatch', count: bookings.length },
            { id: 'services', label: 'Service Catalog', count: services.length },
            { id: 'coupons', label: 'Coupons & Promos', count: coupons.length },
            { id: 'settings', label: 'Global Settings' },
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          variant="underline"
        />

        {/* TAB 1: OVERVIEW */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <h3 className="text-base font-bold text-white">Recent System Bookings</h3>
            <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl divide-y divide-dark-800">
              {bookings.slice(0, 6).map((b) => (
                <div key={b.id} className="py-3 flex items-center justify-between text-xs">
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-white font-semibold">#{b.booking_number || b.id}</span>
                      <span className="text-slate-300">• {b.service?.name || 'Home Service'}</span>
                    </div>
                    <p className="text-[11px] text-slate-500">
                      {b.booking_date} at {b.preferred_time}
                    </p>
                  </div>

                  <div className="flex items-center gap-3">
                    <StatusBadge status={b.status} />
                    <span className="font-mono font-bold text-white">
                      ₹{(b.final_price || b.base_price || 499).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 2: USERS DIRECTORY */}
        {activeTab === 'users' && (
          <div className="space-y-4">
            <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-dark-800 text-slate-400 font-semibold">
                    <th className="pb-3">User</th>
                    <th className="pb-3">Role</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Registered</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-800/60">
                  {users.map((u) => (
                    <tr key={u.id} className="text-slate-300 hover:bg-dark-850/40 transition-colors">
                      <td className="py-3">
                        <p className="font-bold text-white">{u.full_name}</p>
                        <p className="text-[11px] text-slate-500">{u.email}</p>
                      </td>
                      <td className="py-3 font-mono text-[11px] uppercase">
                        {String(u.role).replace('ROLE_', '')}
                      </td>
                      <td className="py-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                            u.is_active
                              ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                              : 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                          }`}
                        >
                          {u.is_active ? 'ACTIVE' : 'SUSPENDED'}
                        </span>
                      </td>
                      <td className="py-3 text-slate-400">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}
                      </td>
                      <td className="py-3 text-right">
                        <Button
                          variant={u.is_active ? 'danger' : 'secondary'}
                          size="sm"
                          onClick={() => handleToggleUserSuspend(u)}
                        >
                          {u.is_active ? 'Suspend' : 'Activate'}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 3: TECHNICIAN VERIFICATION */}
        {activeTab === 'technicians' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {technicians.map((tech) => (
                <Card key={tech.id} className="p-5 flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h4 className="text-sm font-bold text-white">
                          {tech.user?.full_name || `Technician #${tech.id}`}
                        </h4>
                        <p className="text-xs text-brand-400 font-semibold">{tech.specialization}</p>
                      </div>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                          tech.is_verified
                            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                            : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                        }`}
                      >
                        {tech.is_verified ? 'VERIFIED PRO' : 'PENDING AUDIT'}
                      </span>
                    </div>

                    <div className="text-xs text-slate-300 grid grid-cols-2 gap-2 pt-1">
                      <span>Experience: {tech.experience_years} yrs</span>
                      <span>Radius: {tech.service_radius_km} km</span>
                    </div>
                  </div>

                  <div className="pt-3 border-t border-dark-800 flex items-center justify-between">
                    <Button
                      variant="outline"
                      size="sm"
                      leftIcon={FileCheck}
                      onClick={() => handleInspectTechDocs(tech)}
                    >
                      Audit Docs
                    </Button>

                    <div className="flex items-center gap-2">
                      {!tech.is_verified ? (
                        <Button
                          variant="primary"
                          size="sm"
                          onClick={() => handleApproveTech(tech.id)}
                          isLoading={actionLoadingId === tech.id}
                        >
                          Approve Pro
                        </Button>
                      ) : (
                        <Button
                          variant="danger"
                          size="sm"
                          onClick={() => handleRejectTech(tech.id)}
                          isLoading={actionLoadingId === tech.id}
                        >
                          Revoke
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* TAB 4: BOOKINGS DISPATCH */}
        {activeTab === 'bookings' && (
          <div className="space-y-4">
            <div className="p-4 bg-dark-900 border border-dark-750 rounded-2xl overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-dark-800 text-slate-400 font-semibold">
                    <th className="pb-3">Booking ID</th>
                    <th className="pb-3">Service</th>
                    <th className="pb-3">Status</th>
                    <th className="pb-3">Schedule</th>
                    <th className="pb-3">Amount</th>
                    <th className="pb-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-dark-800/60">
                  {bookings.map((b) => (
                    <tr key={b.id} className="text-slate-300 hover:bg-dark-850/40">
                      <td className="py-3 font-mono font-bold text-white">#{b.booking_number || b.id}</td>
                      <td className="py-3">{b.service?.name || 'Home Service'}</td>
                      <td className="py-3">
                        <StatusBadge status={b.status} />
                      </td>
                      <td className="py-3">
                        {b.booking_date} @ {b.preferred_time}
                      </td>
                      <td className="py-3 font-mono font-bold text-white">
                        ₹{(b.final_price || b.base_price || 499).toFixed(2)}
                      </td>
                      <td className="py-3 text-right">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => {
                            setSelectedBookingForOverride(b);
                            setOverrideStatusVal(String(b.status).toLowerCase());
                          }}
                        >
                          Override Status
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: SERVICE CATALOG */}
        {activeTab === 'services' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-white">Categories & Services</h3>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={() => setIsCategoryModalOpen(true)}>
                  Add Category
                </Button>
                <Button variant="primary" size="sm" onClick={() => setIsServiceModalOpen(true)}>
                  Add Service
                </Button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {services.map((srv) => (
                <Card key={srv.id} className="p-4 space-y-2">
                  <div className="flex justify-between items-start">
                    <span className="text-[10px] font-medium px-2 py-0.5 rounded bg-dark-800 text-slate-400">
                      {srv.category_name || 'Service'}
                    </span>
                    <span className="font-mono font-bold text-white">₹{srv.price}</span>
                  </div>
                  <h4 className="text-sm font-bold text-white">{srv.name}</h4>
                  <p className="text-xs text-slate-400 line-clamp-2">{srv.description}</p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* TAB 6: COUPONS */}
        {activeTab === 'coupons' && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="text-base font-bold text-white">Active Promotions</h3>
              <Button variant="primary" size="sm" leftIcon={Plus} onClick={() => setIsCouponModalOpen(true)}>
                Create Coupon
              </Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {coupons.map((cpn) => (
                <Card key={cpn.id} className="p-4 space-y-3">
                  <div className="flex justify-between items-start">
                    <span className="px-2.5 py-1 rounded-lg text-xs font-mono font-bold bg-brand-500/15 text-brand-400 border border-brand-500/30">
                      {cpn.code}
                    </span>
                    <button
                      onClick={() => handleDeleteCoupon(cpn.id)}
                      className="text-rose-400 hover:text-rose-300 p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <p className="text-xs text-slate-300">
                    {cpn.discount_type === 'percentage'
                      ? `${cpn.discount_value}% OFF`
                      : `Flat ₹${cpn.discount_value} OFF`}
                  </p>
                  <p className="text-[11px] text-slate-500">
                    Min Order: ₹{cpn.min_order_amount} • Valid till {cpn.valid_until}
                  </p>
                </Card>
              ))}
            </div>
          </div>
        )}

        {/* TAB 7: GLOBAL SETTINGS */}
        {activeTab === 'settings' && (
          <div className="max-w-xl space-y-6">
            <h3 className="text-base font-bold text-white">Platform Parameters</h3>
            <form onSubmit={handleSaveSettings} className="space-y-4">
              <Input
                label="Platform Take Commission (%)"
                type="number"
                value={commissionPct}
                onChange={(e) => setCommissionPct(Number(e.target.value))}
                required
              />
              <Input
                label="GST / Tax Rate (%)"
                type="number"
                value={taxPct}
                onChange={(e) => setTaxPct(Number(e.target.value))}
                required
              />
              <div className="pt-2">
                <Button variant="primary" size="md" type="submit">
                  Save Platform Settings
                </Button>
              </div>
            </form>
          </div>
        )}
      </div>

      {/* Override Modal */}
      {selectedBookingForOverride && (
        <Modal
          isOpen={!!selectedBookingForOverride}
          onClose={() => setSelectedBookingForOverride(null)}
          title={`Override Booking #${selectedBookingForOverride.id}`}
          description="Force state transition on platform booking ledger."
          maxWidth="md"
        >
          <form onSubmit={handleExecuteStatusOverride} className="space-y-4">
            <div className="space-y-1 text-left">
              <label className="text-xs font-semibold text-slate-300">Select Target State</label>
              <select
                value={overrideStatusVal}
                onChange={(e) => setOverrideStatusVal(e.target.value)}
                className="w-full bg-dark-850 border border-dark-700 rounded-xl px-3 py-2 text-xs text-white"
              >
                <option value="pending">Pending</option>
                <option value="assigned">Assigned</option>
                <option value="accepted">Accepted</option>
                <option value="on_the_way">On The Way</option>
                <option value="arrived">Arrived</option>
                <option value="qr_verified">QR Verified</option>
                <option value="in_progress">In Progress</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>

            <Input
              label="Admin Audit Reason"
              placeholder="e.g. Customer requested immediate resolution..."
              value={overrideNote}
              onChange={(e) => setOverrideNote(e.target.value)}
            />

            <div className="flex justify-end gap-3 pt-3 border-t border-dark-750">
              <Button variant="outline" size="sm" type="button" onClick={() => setSelectedBookingForOverride(null)}>
                Cancel
              </Button>
              <Button variant="primary" size="sm" type="submit">
                Execute Override
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {/* Document Review Modal */}
      {selectedTechDocs && (
        <Modal
          isOpen={!!selectedTechDocs}
          onClose={() => setSelectedTechDocs(null)}
          title={`Audit Credentials: ${selectedTechDocs.tech.user?.full_name || 'Technician'}`}
          description="Verify government identification and trade certifications."
          maxWidth="lg"
        >
          <div className="space-y-4">
            {selectedTechDocs.docs.length > 0 ? (
              selectedTechDocs.docs.map((doc) => (
                <div key={doc.id} className="p-4 bg-dark-850 border border-dark-750 rounded-xl flex items-center justify-between text-xs">
                  <div>
                    <p className="font-bold text-white capitalize">{doc.doc_type.replace(/_/g, ' ')}</p>
                    <p className="text-[11px] text-slate-400">Uploaded on {new Date(doc.created_at).toLocaleDateString()}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    {!doc.is_verified ? (
                      <Button variant="primary" size="sm" onClick={() => handleApproveDoc(doc.id)}>
                        Approve Document
                      </Button>
                    ) : (
                      <span className="text-emerald-400 font-semibold">✓ Verified</span>
                    )}
                  </div>
                </div>
              ))
            ) : (
              <p className="text-xs text-slate-400">No documents submitted yet.</p>
            )}
          </div>
        </Modal>
      )}

      {/* Category Modal */}
      <Modal
        isOpen={isCategoryModalOpen}
        onClose={() => setIsCategoryModalOpen(false)}
        title="Add Service Category"
        maxWidth="md"
      >
        <form onSubmit={handleCreateCategory} className="space-y-4">
          <Input
            label="Category Name *"
            placeholder="e.g. Electrical & Lighting"
            value={newCatName}
            onChange={(e) => setNewCatName(e.target.value)}
            required
          />
          <Input
            label="Description"
            placeholder="Short description of trade..."
            value={newCatDesc}
            onChange={(e) => setNewCatDesc(e.target.value)}
          />
          <div className="flex justify-end gap-3 pt-3 border-t border-dark-750">
            <Button variant="outline" size="sm" type="button" onClick={() => setIsCategoryModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit">
              Create
            </Button>
          </div>
        </form>
      </Modal>

      {/* Service Modal */}
      <Modal
        isOpen={isServiceModalOpen}
        onClose={() => setIsServiceModalOpen(false)}
        title="Add Service Item"
        maxWidth="md"
      >
        <form onSubmit={handleCreateService} className="space-y-4">
          <Input
            label="Service Title *"
            placeholder="e.g. Inverter AC Gas Refill"
            value={serviceForm.name}
            onChange={(e) => setServiceForm({ ...serviceForm, name: e.target.value })}
            required
          />
          <div className="space-y-1 text-left">
            <label className="text-xs font-semibold text-slate-300">Category</label>
            <select
              value={serviceForm.category_id}
              onChange={(e) => setServiceForm({ ...serviceForm, category_id: Number(e.target.value) })}
              className="w-full bg-dark-850 border border-dark-700 rounded-xl px-3 py-2 text-xs text-white"
            >
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Price (₹) *"
              type="number"
              value={serviceForm.price}
              onChange={(e) => setServiceForm({ ...serviceForm, price: Number(e.target.value) })}
              required
            />
            <Input
              label="Duration (Mins) *"
              type="number"
              value={serviceForm.duration_minutes}
              onChange={(e) => setServiceForm({ ...serviceForm, duration_minutes: Number(e.target.value) })}
              required
            />
          </div>
          <Input
            label="Description"
            placeholder="Scope of work..."
            value={serviceForm.description}
            onChange={(e) => setServiceForm({ ...serviceForm, description: e.target.value })}
          />
          <div className="flex justify-end gap-3 pt-3 border-t border-dark-750">
            <Button variant="outline" size="sm" type="button" onClick={() => setIsServiceModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit">
              Save Service
            </Button>
          </div>
        </form>
      </Modal>

      {/* Coupon Modal */}
      <Modal
        isOpen={isCouponModalOpen}
        onClose={() => setIsCouponModalOpen(false)}
        title="Create Promotional Coupon"
        maxWidth="md"
      >
        <form onSubmit={handleCreateCoupon} className="space-y-4">
          <Input
            label="Promo Code *"
            placeholder="e.g. FESTIVE50"
            value={couponForm.code}
            onChange={(e) => setCouponForm({ ...couponForm, code: e.target.value })}
            className="uppercase font-mono"
            required
          />
          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Discount Value *"
              type="number"
              value={couponForm.discount_value}
              onChange={(e) => setCouponForm({ ...couponForm, discount_value: Number(e.target.value) })}
              required
            />
            <Input
              label="Min Order Amount (₹)"
              type="number"
              value={couponForm.min_order_amount}
              onChange={(e) => setCouponForm({ ...couponForm, min_order_amount: Number(e.target.value) })}
            />
          </div>
          <div className="flex justify-end gap-3 pt-3 border-t border-dark-750">
            <Button variant="outline" size="sm" type="button" onClick={() => setIsCouponModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" size="sm" type="submit">
              Create Coupon
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
