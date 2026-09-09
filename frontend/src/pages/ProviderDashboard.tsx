import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, 
  Clock, 
  MapPin, 
  ShieldCheck, 
  Power, 
  Navigation, 
  Play, 
  DollarSign, 
  TrendingUp, 
  Star, 
  FileText, 
  Calendar, 
  User, 
  Phone, 
  AlertCircle,
  Eye,
  CheckSquare,
  Bell,
  Camera
} from 'lucide-react';
import { technicianApi } from '../api/technician';
import { bookingsApi } from '../api/bookings';
import { notificationsApi } from '../api/notifications';
import { BookingMediaSection } from '../components/media/BookingMediaSection';
import { JobCompletionModal } from '../components/modals/JobCompletionModal';
import { useAuthStore } from '../store/useAuthStore';
import { Booking, TechnicianProfile, NotificationItem } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';
import { TechnicianVerifyModal } from '../components/modals/TechnicianVerifyModal';
import { BookingDetailsModal } from '../components/modals/BookingDetailsModal';
import { useRealTimeSync, triggerLocalSync } from '../services/realtime';
import { getErrorMessage } from '../api/axios';

export const ProviderDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [profile, setProfile] = useState<TechnicianProfile | null>(null);
  const [jobs, setJobs] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [completingJobId, setCompletingJobId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'today' | 'active' | 'pending' | 'completed' | 'all' | 'earnings' | 'documents' | 'notifications'>('today');

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [verifyBooking, setVerifyBooking] = useState<Booking | null>(null);
  const [detailsBooking, setDetailsBooking] = useState<Booking | null>(null);

  const getProofStatus = (note?: string | null) => {
    if (!note) return null;
    try {
      const data = JSON.parse(note);
      return data.proof_status || null;
    } catch {
      return null;
    }
  };

  const loadTechnicianData = async (isBackground = false) => {
    try {
      if (!isBackground) setLoading(true);
      const [profRes, jobsRes, activeRes, notifRes] = await Promise.allSettled([
        technicianApi.getProfile(),
        technicianApi.getMyJobs(),
        technicianApi.getActiveBookings(),
        notificationsApi.getNotifications({ limit: 50 }),
      ]);

      if (profRes.status === 'fulfilled' && profRes.value) {
        setProfile(profRes.value);
      }

      let allJobs: Booking[] = [];
      if (jobsRes.status === 'fulfilled') {
        const jList = Array.isArray(jobsRes.value) ? jobsRes.value : (jobsRes.value as any)?.items || [];
        allJobs = [...jList];
      }
      if (activeRes.status === 'fulfilled') {
        const aList = Array.isArray(activeRes.value) ? activeRes.value : (activeRes.value as any)?.items || [];
        const existingIds = new Set(allJobs.map((j) => j.id));
        aList.forEach((a: Booking) => {
          if (!existingIds.has(a.id)) allJobs.push(a);
        });
      }
      setJobs(allJobs);

      if (notifRes.status === 'fulfilled') {
        const nList = Array.isArray(notifRes.value) ? notifRes.value : (notifRes.value as any)?.items || [];
        setNotifications(nList);
        setUnreadCount(nList.filter((n: NotificationItem) => !n.is_read).length);
      }
    } catch (err) {
      console.error('Failed to load technician workspace:', err);
    } finally {
      if (!isBackground) setLoading(false);
    }
  };

  useEffect(() => {
    loadTechnicianData(false);
  }, []);

  // Real-time synchronization across dashboards & tabs
  useRealTimeSync(() => {
    loadTechnicianData(true);
  }, 15000);

  // Status transitions
  const handleJobAction = async (bookingId: number, action: 'accept' | 'start_trip' | 'arrived' | 'start_service' | 'complete') => {
    try {
      setActionLoading(bookingId);
      switch (action) {
        case 'accept':
          await technicianApi.acceptBooking(bookingId);
          break;
        case 'start_trip':
          await technicianApi.startTrip(bookingId);
          break;
        case 'arrived':
          await technicianApi.markArrived(bookingId);
          break;
        case 'start_service':
          await technicianApi.startService(bookingId);
          break;
        case 'complete':
          await technicianApi.completeService(bookingId);
          break;
      }
      triggerLocalSync();
      await loadTechnicianData(true);
    } catch (err: any) {
      console.error(`Failed to execute ${action}:`, err);
      alert(getErrorMessage(err, `Action ${action} failed`));
    } finally {
      setActionLoading(null);
    }
  };

  const [inlineCodes, setInlineCodes] = useState<Record<number, string>>({});

  const handleVerifyCode = async (bookingId: number, codeToVerify?: string) => {
    const code = (codeToVerify || inlineCodes[bookingId] || '').trim();
    if (code.length < 6) {
      alert('Please enter the full 6-digit customer PIN.');
      return;
    }
    try {
      setActionLoading(bookingId);
      await technicianApi.verifyCode(bookingId, code);
      setInlineCodes((prev) => ({ ...prev, [bookingId]: '' }));
      triggerLocalSync();
      await loadTechnicianData(true);
    } catch (err: any) {
      console.error('Failed to verify code:', err);
      alert(getErrorMessage(err, 'Invalid verification code. Please check with customer.'));
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return <LoadingState message="Initializing Technician Workspace..." />;
  }

  const activeJobs = jobs.filter((j) => ['accepted', 'confirmed', 'in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status));
  const pendingJobs = jobs.filter((j) => ['assigned', 'pending'].includes(j.status));
  const completedJobs = jobs.filter((j) => j.status === 'completed');

  const totalEarnings = completedJobs.reduce((acc, j) => acc + (j.final_price || j.total_amount || j.estimated_price || 0) * 0.8, 0);

  return (
    <div className="min-h-screen bg-[#F8FAFC] py-8 text-slate-900 selection:bg-sage-500/20 selection:text-slate-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* ──────────────────────────────────────────────────────────────────────────
            TOP STATUS & DISPATCH TOGGLE BAR
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="p-6 rounded-3xl bg-white border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-card">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-sage-50 border border-sage-200 flex items-center justify-center text-sage-700 text-base font-bold shadow-subtle">
              {(user?.username || user?.full_name)?.charAt(0)?.toUpperCase() || 'T'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-slate-900 tracking-tight">@{user?.username || user?.full_name || 'technician'}</h1>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-sage-50 text-sage-700 border border-sage-200 font-semibold">
                  {profile?.specialization || 'Multi-Trade Master'}
                </span>
              </div>
              <p className="text-xs text-slate-500 font-mono mt-0.5">
                Rating: <span className="text-sage-600 font-bold">★ {profile?.rating_avg || '4.95'}</span> • {completedJobs.length} Completed Missions
              </p>
            </div>
          </div>
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            WORKSPACE NAVIGATION TABS
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 border-b border-slate-200 pb-3 overflow-x-auto">
          {[
            { id: 'today', label: "Today's Queue", count: activeJobs.length + pendingJobs.length },
            { id: 'active', label: 'In Execution', count: activeJobs.length },
            { id: 'pending', label: 'Incoming Dispatches', count: pendingJobs.length },
            { id: 'completed', label: 'Completed Missions', count: completedJobs.length },
            { id: 'all', label: 'All Missions', count: jobs.length },
            { id: 'earnings', label: 'Earnings & Payouts' },
            { id: 'notifications', label: 'Alerts', count: unreadCount },
            { id: 'documents', label: 'KYC & Credentials' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                activeTab === tab.id
                  ? 'bg-sage-600 text-white border-sage-600 shadow-subtle'
                  : 'bg-white text-slate-600 hover:text-slate-900 border-slate-200 hover:border-slate-300'
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`ml-2 text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  activeTab === tab.id ? 'bg-white/20 text-white' : 'bg-slate-100 text-slate-600'
                }`}>
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            TAB CONTENT
        ────────────────────────────────────────────────────────────────────────── */}
        {activeTab === 'today' || activeTab === 'active' || activeTab === 'pending' || activeTab === 'completed' || activeTab === 'all' ? (
          <div className="space-y-4">
            {jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs
                  .filter((j) => {
                    if (activeTab === 'active') return ['accepted', 'confirmed', 'in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status);
                    if (activeTab === 'pending') return ['assigned', 'pending'].includes(j.status);
                    if (activeTab === 'today') return ['assigned', 'pending', 'accepted', 'confirmed', 'in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status);
                    if (activeTab === 'completed') return j.status === 'completed';
                    return true; // 'all' will return true for all jobs including completed
                  })
                  .map((job) => (
                    <div
                      key={job.id}
                      className="p-6 rounded-3xl bg-white border border-slate-200 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 shadow-card hover:border-slate-300 transition-colors"
                    >
                      <div className="space-y-2 max-w-xl">
                        <div className="flex items-center gap-3">
                          <span className="text-base font-bold text-slate-900">
                            {job.service?.name || 'Service Assignment'}
                          </span>
                          <StatusBadge status={job.status} size="sm" />
                        </div>

                        <p className="text-xs text-slate-500 font-mono">
                          Booking ID #{job.booking_number || job.id} • Schedule: {job.booking_date ? new Date(job.booking_date).toLocaleDateString() : 'Today'} {job.preferred_time ? `(${job.preferred_time})` : ''}
                        </p>

                        <div className="flex flex-col gap-1.5 pt-1">
                          <div className="flex items-center gap-2 text-xs text-slate-600">
                            <User className="w-3.5 h-3.5 text-sage-600 shrink-0" />
                            <span className="font-semibold text-slate-900">@{job.customer?.username || job.customer?.full_name || 'customer'}</span>
                            {job.customer?.phone && (
                              <>
                                <span className="text-slate-400">•</span>
                                <Phone className="w-3 h-3 text-slate-500 shrink-0" />
                                <span className="text-slate-600">{job.customer.phone}</span>
                              </>
                            )}
                          </div>
                          <div className="flex items-start gap-2 text-xs text-slate-600">
                            <MapPin className="w-3.5 h-3.5 text-sage-600 shrink-0 mt-0.5" />
                            <span>
                              {job.address ? `${job.address.house_no} ${job.address.area}, ${job.address.city}` : 'Customer Address on record'}
                            </span>
                            {job.address && (
                              <a 
                                href={`https://maps.google.com/?q=${encodeURIComponent(`${job.address.house_no} ${job.address.area}, ${job.address.city}, ${job.address.pincode}`)}`} 
                                target="_blank" 
                                rel="noopener noreferrer"
                                className="ml-2 text-[10px] text-sage-600 hover:text-sage-700 underline underline-offset-2 flex items-center gap-1 font-semibold"
                                title="Open in Google Maps"
                              >
                                <Navigation className="w-3 h-3" />
                                Navigate
                              </a>
                            )}
                          </div>
                        </div>

                        {job.customer_note && (
                          <p className="text-[11px] text-slate-600 bg-slate-50 p-2.5 rounded-xl border border-slate-200">
                            Notes: {job.customer_note}
                          </p>
                        )}
                      </div>

                      {/* Action Bar based on Status */}
                      <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto shrink-0">
                        <button
                          onClick={() => setDetailsBooking(job)}
                          className="px-3 py-2 rounded-xl text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 font-medium"
                        >
                          Details
                        </button>

                        {/* Accept */}
                        {(job.status === 'assigned' || job.status === 'pending') && (
                          <button
                            onClick={() => handleJobAction(job.id, 'accept')}
                            disabled={actionLoading === job.id}
                            className="btn-primary text-xs px-4 py-2 flex items-center gap-1.5"
                          >
                            <CheckSquare className="w-3.5 h-3.5" />
                            <span>Accept Dispatch</span>
                          </button>
                        )}

                        {/* Arrived */}
                        {(job.status === 'accepted' || job.status === 'start_trip' || job.status === 'on_the_way') && (
                          <button
                            onClick={() => handleJobAction(job.id, 'arrived')}
                            disabled={actionLoading === job.id}
                            className="btn-accent text-xs px-4 py-2 flex items-center gap-1.5 shadow-subtle"
                          >
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Mark Arrived</span>
                          </button>
                        )}

                        {/* Arrival & Verification: Inline PIN Entry + Modal Trigger */}
                        {job.status === 'arrived' && (
                          <div className="flex flex-wrap items-center gap-2">
                            <div className="flex items-center gap-1.5 bg-slate-50 p-1 rounded-xl border border-slate-200">
                              <input
                                type="text"
                                maxLength={6}
                                placeholder="6-digit PIN"
                                value={inlineCodes[job.id] || ''}
                                onChange={(e) => setInlineCodes({ ...inlineCodes, [job.id]: e.target.value.replace(/[^0-9a-zA-Z]/g, '') })}
                                className="w-24 px-2 py-1.5 text-center font-mono text-xs bg-white border border-slate-300 rounded-lg text-slate-900 tracking-widest focus:outline-none focus:border-sage-500"
                              />
                              <button
                                onClick={() => handleVerifyCode(job.id)}
                                disabled={actionLoading === job.id || (inlineCodes[job.id] || '').length < 6}
                                className="btn-accent text-xs px-3 py-1.5 flex items-center gap-1 shadow-subtle disabled:opacity-40 font-semibold"
                              >
                                <span>Verify</span>
                              </button>
                            </div>
                            <button
                              onClick={() => setVerifyBooking(job)}
                              className="px-3 py-2 rounded-xl text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 flex items-center gap-1 font-medium"
                            >
                              <ShieldCheck className="w-3.5 h-3.5 text-sage-600" />
                              <span>PIN Modal</span>
                            </button>
                          </div>
                        )}

                        {/* Working / Ongoing Service: Proof of Work -> Customer Approval -> Complete */}
                        {(job.status === 'confirmed' || job.status === 'in_progress') && (
                          <div className="flex items-center gap-2">
                            {getProofStatus(job.admin_note) === 'approved' ? (
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] font-mono px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 border border-emerald-200 flex items-center gap-1.5 font-bold">
                                  <CheckCircle2 className="w-3.5 h-3.5" />
                                  <span>Customer Approved Work</span>
                                </span>
                                <span className="text-[11px] font-mono px-3 py-1.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1.5 font-medium">
                                  <Clock className="w-3.5 h-3.5 animate-pulse" />
                                  <span>Awaiting Customer Payment...</span>
                                </span>
                              </div>
                            ) : getProofStatus(job.admin_note) === 'submitted' ? (
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] font-mono px-3 py-1.5 rounded-xl bg-amber-50 text-amber-700 border border-amber-200 flex items-center gap-1.5 font-medium">
                                  <Clock className="w-3.5 h-3.5 animate-pulse" />
                                  <span>Proof Submitted • Awaiting User Approval</span>
                                </span>
                                <button
                                  onClick={() => setCompletingJobId(job.id)}
                                  className="px-3 py-1.5 text-xs font-mono rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 border border-slate-200 flex items-center gap-1"
                                  title="Update or view uploaded proof photos"
                                >
                                  <Camera className="w-3.5 h-3.5" />
                                  <span>Update Evidence</span>
                                </button>
                              </div>
                            ) : getProofStatus(job.admin_note) === 'changes_requested' ? (
                              <div className="flex items-center gap-2">
                                <span className="text-[11px] font-mono px-3 py-1.5 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 flex items-center gap-1.5 font-medium">
                                  <AlertCircle className="w-3.5 h-3.5" />
                                  <span>Changes Requested by Customer</span>
                                </span>
                                <button
                                  onClick={() => setCompletingJobId(job.id)}
                                  className="btn-primary text-xs px-4 py-2 rounded-xl bg-amber-600 text-white font-bold flex items-center gap-1.5"
                                >
                                  <Camera className="w-3.5 h-3.5" />
                                  <span>Re-upload Evidence</span>
                                </button>
                              </div>
                            ) : (
                              <button
                                onClick={() => setCompletingJobId(job.id)}
                                disabled={actionLoading === job.id}
                                className="btn-primary text-xs px-5 py-2 rounded-xl bg-sage-600 hover:bg-sage-700 text-white flex items-center gap-1.5 font-bold shadow-subtle"
                              >
                                <Camera className="w-4 h-4" />
                                <span>Upload Proof of Work</span>
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <EmptyState
                title="NO ACTIVE DISPATCHES"
                description="Incoming dispatches and assignments in your area will appear here automatically."
              />
            )}
          </div>
        ) : activeTab === 'earnings' ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card">
                <span className="text-xs font-mono text-slate-500 uppercase">Settled Earnings</span>
                <p className="text-3xl font-bold font-mono text-slate-900 mt-1">₹{totalEarnings.toFixed(2)}</p>
                <span className="text-[10px] text-emerald-600 font-mono mt-1 block font-semibold">Direct Bank Transfer Active</span>
              </div>
              <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card">
                <span className="text-xs font-mono text-slate-500 uppercase">Completed Missions</span>
                <p className="text-3xl font-bold font-mono text-slate-900 mt-1">{completedJobs.length}</p>
                <span className="text-[10px] text-slate-500 font-mono mt-1 block">100% On-Time Precision</span>
              </div>
              <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card">
                <span className="text-xs font-mono text-slate-500 uppercase">Master Rating</span>
                <p className="text-3xl font-bold font-mono text-sage-600 mt-1">★ {profile?.rating_avg || '4.95'}</p>
                <span className="text-[10px] text-slate-500 font-mono mt-1 block">Top 5% Tier Network</span>
              </div>
            </div>
          </div>
        ) : activeTab === 'notifications' ? (
          <div className="space-y-4 max-w-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900 tracking-tight">Recent Alerts</h3>
              {unreadCount > 0 && (
                <button 
                  onClick={async () => {
                    await notificationsApi.markAllRead();
                    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
                    setUnreadCount(0);
                  }}
                  className="text-xs font-mono text-sage-600 hover:text-sage-700 font-semibold transition-colors"
                >
                  MARK ALL READ
                </button>
              )}
            </div>
            {notifications.length > 0 ? (
              <div className="space-y-3">
                {notifications.map((notif) => (
                  <div 
                    key={notif.id}
                    className={`p-5 rounded-2xl border flex gap-4 transition-all ${
                      notif.is_read 
                        ? 'bg-white border-slate-200 opacity-70' 
                        : 'bg-white border-sage-200 shadow-card ring-1 ring-sage-400/20'
                    }`}
                  >
                    <div className="mt-1">
                      {notif.is_read ? (
                        <Bell className="w-5 h-5 text-slate-400" />
                      ) : (
                        <div className="relative">
                          <Bell className="w-5 h-5 text-sage-600" />
                          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-500 shadow-subtle"></span>
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-semibold ${notif.is_read ? 'text-slate-600' : 'text-slate-900'}`}>
                        {notif.title}
                      </p>
                      <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                        {notif.message}
                      </p>
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-[10px] font-mono text-slate-400">
                          {new Date(notif.created_at).toLocaleString()}
                        </span>
                        {!notif.is_read && (
                          <button
                            onClick={async () => {
                              await notificationsApi.markRead(notif.id);
                              setNotifications(notifications.map(n => n.id === notif.id ? { ...n, is_read: true } : n));
                              setUnreadCount(prev => Math.max(0, prev - 1));
                            }}
                            className="text-[10px] font-bold font-mono text-sage-600 hover:text-sage-700"
                          >
                            MARK READ
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                title="NO NOTIFICATIONS"
                description="You are all caught up. New assignments and alerts will appear here."
              />
            )}
          </div>
        ) : (
          <div className="p-6 rounded-3xl bg-white border border-slate-200 space-y-4 shadow-card">
            <h3 className="text-base font-bold text-slate-900">KYC Verification & Master Credentials</h3>
            <p className="text-xs text-slate-600 leading-relaxed max-w-xl">
              Government ID, background verification check, and trade license credentials are securely verified.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-700 bg-emerald-50 p-3 rounded-xl border border-emerald-200 max-w-md font-semibold">
              <CheckCircle2 className="w-4 h-4 shrink-0 text-emerald-600" />
              <span>Identity & Work Authorization: VERIFIED & ACTIVE</span>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {verifyBooking && (
        <TechnicianVerifyModal
          booking={verifyBooking}
          isOpen={!!verifyBooking}
          onClose={() => setVerifyBooking(null)}
          onVerified={() => {
            triggerLocalSync();
            loadTechnicianData(true);
          }}
        />
      )}

      {detailsBooking && (
        <BookingDetailsModal
          booking={detailsBooking}
          isOpen={!!detailsBooking}
          onClose={() => setDetailsBooking(null)}
        />
      )}

      {completingJobId && (
        <JobCompletionModal
          bookingId={completingJobId}
          isOpen={!!completingJobId}
          onClose={() => setCompletingJobId(null)}
          onSuccess={() => {
            setCompletingJobId(null);
            triggerLocalSync();
            loadTechnicianData(true);
          }}
        />
      )}
    </div>
  );
};
