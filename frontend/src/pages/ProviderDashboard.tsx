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
  Bell
} from 'lucide-react';
import { technicianApi } from '../api/technician';
import { bookingsApi } from '../api/bookings';
import { notificationsApi } from '../api/notifications';
import { useAuthStore } from '../store/useAuthStore';
import { Booking, TechnicianProfile, NotificationItem } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';
import { TechnicianVerifyModal } from '../components/modals/TechnicianVerifyModal';
import { BookingDetailsModal } from '../components/modals/BookingDetailsModal';
import { useRealTimeSync, triggerLocalSync } from '../services/realtime';

export const ProviderDashboard: React.FC = () => {
  const { user } = useAuthStore();
  const [profile, setProfile] = useState<TechnicianProfile | null>(null);
  const [isOnline, setIsOnline] = useState<boolean>(true);
  const [jobs, setJobs] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'today' | 'active' | 'pending' | 'all' | 'earnings' | 'documents' | 'notifications'>('today');

  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);

  const [verifyBooking, setVerifyBooking] = useState<Booking | null>(null);
  const [detailsBooking, setDetailsBooking] = useState<Booking | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);

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
        setIsOnline(profRes.value.is_online ?? true);
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
  }, 6000);

  const handleToggleOnline = async () => {
    try {
      if (isOnline) {
        await technicianApi.setOffline();
        setIsOnline(false);
      } else {
        await technicianApi.setOnline();
        setIsOnline(true);
      }
    } catch (err) {
      console.error('Failed to toggle status:', err);
    }
  };

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
      alert(err?.response?.data?.detail || `Action ${action} failed`);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return <LoadingState message="Initializing Technician Workspace..." />;
  }

  const activeJobs = jobs.filter((j) => ['in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status));
  const pendingJobs = jobs.filter((j) => ['assigned', 'pending'].includes(j.status));
  const completedJobs = jobs.filter((j) => j.status === 'completed');

  const totalEarnings = completedJobs.reduce((acc, j) => acc + (j.final_price || j.total_amount || j.estimated_price || 0) * 0.8, 0);

  return (
    <div className="min-h-screen bg-dark-950 py-8 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* ──────────────────────────────────────────────────────────────────────────
            TOP STATUS & DISPATCH TOGGLE BAR
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-card">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 text-base font-bold shadow-accent">
              {user?.full_name?.charAt(0) || 'T'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-white tracking-tight">{user?.full_name || 'Master Technician'}</h1>
                <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-dark-800 text-sage-300 border border-dark-750">
                  {profile?.specialization || 'Multi-Trade Master'}
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Rating: <span className="text-sage-400 font-bold">★ {profile?.rating_avg || '4.95'}</span> • {completedJobs.length} Completed Missions
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 self-start sm:self-auto">
            <button
              onClick={handleToggleOnline}
              className={`px-4 py-2 rounded-full text-xs font-mono font-bold flex items-center gap-2.5 transition-all duration-300 ${
                isOnline
                  ? 'bg-emerald-500/15 text-emerald-400 border border-emerald-500/40 shadow-[0_0_15px_rgba(16,185,129,0.15)] hover:bg-emerald-500/20'
                  : 'bg-dark-800 text-slate-400 border border-dark-700 hover:bg-dark-750 hover:text-slate-300'
              }`}
            >
              <div className="relative flex items-center justify-center">
                <Power className="w-4 h-4 z-10" />
                {isOnline && (
                  <span className="absolute w-4 h-4 bg-emerald-400/30 rounded-full animate-ping"></span>
                )}
              </div>
              <span className="tracking-wide">
                {isOnline ? (
                  <>
                    <span className="text-white">ONLINE</span> <span className="text-emerald-500/50 mx-1">•</span> <span className="text-emerald-300/90 font-medium tracking-normal text-[11px]">RECEIVING DISPATCHES</span>
                  </>
                ) : (
                  'OFFLINE • ON BREAK'
                )}
              </span>
            </button>
          </div>
        </div>

        {/* ──────────────────────────────────────────────────────────────────────────
            WORKSPACE NAVIGATION TABS
        ────────────────────────────────────────────────────────────────────────── */}
        <div className="flex items-center gap-2 border-b border-dark-750 pb-3 overflow-x-auto">
          {[
            { id: 'today', label: "Today's Queue", count: activeJobs.length + pendingJobs.length },
            { id: 'active', label: 'In Execution', count: activeJobs.length },
            { id: 'pending', label: 'Incoming Dispatches', count: pendingJobs.length },
            { id: 'all', label: 'All Services', count: jobs.length },
            { id: 'earnings', label: 'Earnings & Payouts' },
            { id: 'notifications', label: 'Alerts', count: unreadCount },
            { id: 'documents', label: 'KYC & Credentials' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all border ${
                activeTab === tab.id
                  ? 'bg-sage-400 text-dark-950 border-sage-400 shadow-accent'
                  : 'bg-dark-900 text-slate-400 hover:text-white border-dark-750 hover:border-dark-700'
              }`}
            >
              <span>{tab.label}</span>
              {tab.count !== undefined && (
                <span className={`ml-2 text-[10px] font-mono px-1.5 py-0.2 rounded ${
                  activeTab === tab.id ? 'bg-dark-950/30 text-dark-950' : 'bg-dark-800 text-slate-300'
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
        {activeTab === 'today' || activeTab === 'active' || activeTab === 'pending' || activeTab === 'all' ? (
          <div className="space-y-4">
            {jobs.length > 0 ? (
              <div className="space-y-4">
                {jobs
                  .filter((j) => {
                    if (activeTab === 'active') return ['in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status);
                    if (activeTab === 'pending') return ['assigned', 'pending'].includes(j.status);
                    if (activeTab === 'today') return ['assigned', 'pending', 'in_progress', 'arrived', 'start_trip', 'on_the_way'].includes(j.status);
                    return true; // 'all' will return true for all jobs including completed
                  })
                  .map((job) => (
                    <div
                      key={job.id}
                      className="p-6 rounded-3xl bg-dark-900 border border-dark-750 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-6 shadow-card hover:border-dark-700 transition-colors"
                    >
                      <div className="space-y-2 max-w-xl">
                        <div className="flex items-center gap-3">
                          <span className="text-base font-bold text-white">
                            {job.service?.name || 'Service Assignment'}
                          </span>
                          <StatusBadge status={job.status} size="sm" />
                        </div>

                        <p className="text-xs text-slate-400 font-mono">
                          Booking ID #{job.booking_number || job.id} • Schedule: {job.booking_date ? new Date(job.booking_date).toLocaleDateString() : 'Today'} {job.preferred_time ? `(${job.preferred_time})` : ''}
                        </p>

                        <div className="flex flex-col gap-1.5 pt-1">
                          <div className="flex items-center gap-2 text-xs text-slate-300">
                            <User className="w-3.5 h-3.5 text-sage-400 shrink-0" />
                            <span className="font-semibold text-white">{job.customer?.full_name || 'Customer'}</span>
                            {job.customer?.phone && (
                              <>
                                <span className="text-slate-500">•</span>
                                <Phone className="w-3 h-3 text-slate-400 shrink-0" />
                                <span className="text-slate-400">{job.customer.phone}</span>
                              </>
                            )}
                          </div>
                          <div className="flex items-start gap-2 text-xs text-slate-300">
                            <MapPin className="w-3.5 h-3.5 text-sage-400 shrink-0 mt-0.5" />
                            <span>
                              {job.address ? `${job.address.house_no} ${job.address.area}, ${job.address.city}` : 'Customer Address on record'}
                            </span>
                          </div>
                        </div>

                        {job.customer_note && (
                          <p className="text-[11px] text-slate-400 bg-dark-850 p-2.5 rounded-xl border border-dark-750">
                            Notes: {job.customer_note}
                          </p>
                        )}
                      </div>

                      {/* Action Bar based on Status */}
                      <div className="flex flex-wrap items-center gap-2.5 w-full lg:w-auto shrink-0">
                        <button
                          onClick={() => setDetailsBooking(job)}
                          className="px-3 py-2 rounded-xl text-xs bg-dark-850 hover:bg-dark-800 text-slate-300 border border-dark-750"
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
                            className="btn-accent text-xs px-4 py-2 flex items-center gap-1.5 shadow-accent"
                          >
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Mark Arrived</span>
                          </button>
                        )}

                        {/* SmartVerify Customer OTP */}
                        {job.status === 'arrived' && (
                          <button
                            onClick={() => setVerifyBooking(job)}
                            className="btn-accent text-xs px-5 py-2 flex items-center gap-1.5 shadow-accent"
                          >
                            <ShieldCheck className="w-3.5 h-3.5" />
                            <span>Verify Customer Passcode</span>
                          </button>
                        )}

                        {/* In Progress -> Complete */}
                        {job.status === 'in_progress' && (
                          <button
                            onClick={() => handleJobAction(job.id, 'complete')}
                            disabled={actionLoading === job.id}
                            className="btn-primary text-xs px-5 py-2 flex items-center gap-1.5 bg-emerald-500 hover:bg-emerald-400 text-dark-950 shadow-subtle"
                          >
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Complete Job & Audit</span>
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            ) : (
              <EmptyState
                title="NO ACTIVE DISPATCHES"
                description="Keep your status toggled to Online to receive upcoming assignments in your zone."
              />
            )}
          </div>
        ) : activeTab === 'earnings' ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Settled Earnings</span>
                <p className="text-3xl font-bold font-mono text-white mt-1">₹{totalEarnings.toFixed(2)}</p>
                <span className="text-[10px] text-emerald-400 font-mono mt-1 block">Direct Bank Transfer Active</span>
              </div>
              <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Completed Services</span>
                <p className="text-3xl font-bold font-mono text-white mt-1">{completedJobs.length}</p>
                <span className="text-[10px] text-slate-400 font-mono mt-1 block">100% On-Time Precision</span>
              </div>
              <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Master Rating</span>
                <p className="text-3xl font-bold font-mono text-sage-400 mt-1">★ {profile?.rating_avg || '4.95'}</p>
                <span className="text-[10px] text-slate-400 font-mono mt-1 block">Top 5% Tier Network</span>
              </div>
            </div>
          </div>
        ) : activeTab === 'notifications' ? (
          <div className="space-y-4 max-w-3xl">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-bold text-white tracking-tight">Recent Alerts</h3>
              {unreadCount > 0 && (
                <button 
                  onClick={async () => {
                    await notificationsApi.markAllRead();
                    setNotifications(notifications.map(n => ({ ...n, is_read: true })));
                    setUnreadCount(0);
                  }}
                  className="text-xs font-mono text-sage-400 hover:text-sage-300 transition-colors"
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
                        ? 'bg-dark-900 border-dark-750 opacity-70' 
                        : 'bg-dark-850 border-sage-500/30 shadow-card'
                    }`}
                  >
                    <div className="mt-1">
                      {notif.is_read ? (
                        <Bell className="w-5 h-5 text-slate-500" />
                      ) : (
                        <div className="relative">
                          <Bell className="w-5 h-5 text-sage-400" />
                          <span className="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-500 shadow-accent"></span>
                        </div>
                      )}
                    </div>
                    <div className="flex-1">
                      <p className={`text-sm font-semibold ${notif.is_read ? 'text-slate-300' : 'text-white'}`}>
                        {notif.title}
                      </p>
                      <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                        {notif.message}
                      </p>
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-[10px] font-mono text-slate-500">
                          {new Date(notif.created_at).toLocaleString()}
                        </span>
                        {!notif.is_read && (
                          <button
                            onClick={async () => {
                              await notificationsApi.markRead(notif.id);
                              setNotifications(notifications.map(n => n.id === notif.id ? { ...n, is_read: true } : n));
                              setUnreadCount(prev => Math.max(0, prev - 1));
                            }}
                            className="text-[10px] font-bold font-mono text-sage-400 hover:text-sage-300"
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
          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 space-y-4">
            <h3 className="text-base font-bold text-white">KYC Verification & Master Credentials</h3>
            <p className="text-xs text-slate-400 leading-relaxed max-w-xl">
              Government ID, background verification check, and trade license credentials are securely verified.
            </p>
            <div className="flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/30 max-w-md">
              <CheckCircle2 className="w-4 h-4 shrink-0" />
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
    </div>
  );
};
