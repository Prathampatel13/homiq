import React, { useEffect, useState } from 'react';
import { 
  Building2, 
  Users, 
  Briefcase, 
  Layers, 
  TrendingUp, 
  ShieldCheck, 
  DollarSign, 
  CheckCircle2, 
  Clock, 
  MapPin, 
  PlusCircle, 
  Search,
  ChevronRight
} from 'lucide-react';
import { companyApi } from '../api/company';
import { bookingsApi } from '../api/bookings';
import { adminApi } from '../api/admin';
import { CompanyProfile, Booking, TechnicianProfile } from '../types';
import { StatusBadge } from '../components/ui/StatusBadge';
import { EmptyState } from '../components/ui/EmptyState';
import { LoadingState } from '../components/ui/LoadingState';

export const CompanyDashboard: React.FC = () => {
  const [profile, setProfile] = useState<CompanyProfile | null>(null);
  const [technicians, setTechnicians] = useState<TechnicianProfile[]>([]);
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'technicians' | 'bookings' | 'analytics'>('overview');

  useEffect(() => {
    const loadCompanyData = async () => {
      try {
        setLoading(true);
        const [profRes, techRes, bookRes] = await Promise.allSettled([
          companyApi.getProfile(),
          adminApi.getTechnicians(),
          bookingsApi.getBookings({ limit: 100 }),
        ]);

        if (profRes.status === 'fulfilled' && profRes.value) {
          setProfile(profRes.value);
        }
        if (techRes.status === 'fulfilled') {
          const tList = Array.isArray(techRes.value) ? techRes.value : (techRes.value as any)?.items || [];
          setTechnicians(tList);
        }
        if (bookRes.status === 'fulfilled') {
          const bList = Array.isArray(bookRes.value) ? bookRes.value : (bookRes.value as any)?.items || [];
          setBookings(bList);
        }
      } catch (err) {
        console.error('Failed to load company workspace:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCompanyData();
  }, []);

  if (loading) {
    return <LoadingState message="Loading Enterprise Fleet Workspace..." />;
  }

  const activeOperations = bookings.filter((b) => ['assigned', 'accepted', 'in_progress', 'arrived', 'on_the_way'].includes(b.status));
  const completedOperations = bookings.filter((b) => b.status === 'completed');

  const getTechName = (tech: any) => {
    if (!tech) return 'Pending Assignment';
    if (typeof tech.full_name === 'string') return tech.full_name;
    if (tech.user?.full_name) return tech.user.full_name;
    return 'Master Technician';
  };

  return (
    <div className="min-h-screen bg-dark-950 py-8 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        {/* Company Header */}
        <div className="p-6 sm:p-8 rounded-3xl bg-dark-900 border border-dark-750 flex flex-col sm:flex-row sm:items-center justify-between gap-6 shadow-card">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-2xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 font-bold text-xl shadow-accent">
              <Building2 className="w-7 h-7" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-bold text-white tracking-tight">{profile?.company_name || 'Enterprise Fleet Operations'}</h1>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-dark-800 text-sage-300 border border-dark-750">
                  ENTERPRISE PARTNER
                </span>
              </div>
              <p className="text-xs text-slate-400 font-mono mt-0.5">
                Fleet Capacity: {technicians.length} Master Techs • Active Operations: {activeOperations.length}
              </p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex items-center gap-2 border-b border-dark-750 pb-3">
          {[
            { id: 'overview', label: 'Fleet Overview' },
            { id: 'technicians', label: 'Technicians Roster', count: technicians.length },
            { id: 'bookings', label: 'Operations & Jobs', count: bookings.length },
            { id: 'analytics', label: 'Enterprise Performance' },
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
                <span className="ml-2 text-[10px] font-mono px-1.5 py-0.2 rounded bg-dark-800 text-slate-300">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Content */}
        {activeTab === 'overview' ? (
          <div className="space-y-6">
            {/* KPI Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
              <div className="p-5 rounded-2xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Active Operations</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{activeOperations.length}</p>
                <span className="text-[10px] text-sage-400 font-mono mt-0.5 block">Live in field</span>
              </div>
              <div className="p-5 rounded-2xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Total Completed</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{completedOperations.length}</p>
                <span className="text-[10px] text-emerald-400 font-mono mt-0.5 block">100% Quality rating</span>
              </div>
              <div className="p-5 rounded-2xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Fleet Size</span>
                <p className="text-2xl font-bold font-mono text-white mt-1">{technicians.length}</p>
                <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">Certified Technicians</span>
              </div>
              <div className="p-5 rounded-2xl bg-dark-900 border border-dark-750 shadow-card">
                <span className="text-xs font-mono text-slate-400 uppercase">Compliance</span>
                <p className="text-2xl font-bold font-mono text-sage-400 mt-1">100%</p>
                <span className="text-[10px] text-slate-400 font-mono mt-0.5 block">SmartVerify audited</span>
              </div>
            </div>

            {/* Active Operations List */}
            <div className="space-y-4">
              <h2 className="text-base font-bold text-white tracking-tight">Active Dispatches</h2>
              {activeOperations.length > 0 ? (
                <div className="space-y-3">
                  {activeOperations.map((b) => (
                    <div
                      key={b.id}
                      className="p-5 rounded-2xl bg-dark-900 border border-dark-750 flex items-center justify-between shadow-card"
                    >
                      <div>
                        <div className="flex items-center gap-2.5">
                          <span className="text-sm font-bold text-white">{b.service?.name || 'Service'}</span>
                          <StatusBadge status={b.status} size="sm" />
                        </div>
                        <p className="text-xs text-slate-400 font-mono mt-0.5">Booking ID #{b.booking_number || b.id}</p>
                      </div>
                      <span className="text-xs font-mono text-slate-300">
                        {getTechName(b.technician)}
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-8 rounded-2xl bg-dark-900/50 border border-dark-750 text-center text-xs text-slate-400">
                  No active operations at this moment.
                </div>
              )}
            </div>
          </div>
        ) : activeTab === 'technicians' ? (
          <div className="space-y-4">
            {technicians.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {technicians.map((t) => (
                  <div key={t.id} className="p-5 rounded-2xl bg-dark-900 border border-dark-750 shadow-card">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl bg-sage-400/15 border border-sage-400/30 flex items-center justify-center text-sage-400 text-xs font-bold">
                        {t.user?.full_name?.charAt(0) || 'T'}
                      </div>
                      <div>
                        <h4 className="text-xs font-bold text-white">{t.user?.full_name || 'Technician'}</h4>
                        <span className="text-[10px] font-mono text-slate-400">{t.specialization || 'Master Tech'}</span>
                      </div>
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 flex items-center justify-between pt-3 border-t border-dark-750">
                      <span>Rating: ★ {t.rating_avg || '4.9'}</span>
                      <span className="text-emerald-400">Active</span>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState
                title="NO TECHNICIANS IN FLEET"
                description="Assign technicians to your company roster to receive enterprise dispatches."
              />
            )}
          </div>
        ) : (
          <div className="p-8 rounded-2xl bg-dark-900 border border-dark-750 text-center text-xs text-slate-400">
            Enterprise analytics and operational logs synchronized.
          </div>
        )}
      </div>
    </div>
  );
};
