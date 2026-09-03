import React, { useEffect, useState } from 'react';
import { technicianApi } from '../api/technician';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../types';
import { BarChart3, DollarSign, Briefcase, Star, TrendingUp, CheckCircle2 } from 'lucide-react';
import { LoadingState } from '../components/ui/LoadingState';

export const AnalyticsPage: React.FC = () => {
  const { user, getEffectiveRole } = useAuthStore();
  const role = getEffectiveRole();
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        if (role === UserRole.TECHNICIAN) {
          const res = await technicianApi.getDashboard();
          // Backend returns { stats: {...}, todays_jobs: [...] }
          const dashboardStats = (res as any).stats || res;
          setStats(dashboardStats);
        } else {
          // If not a technician, maybe redirect or show empty state
          setStats(null);
        }
      } catch (err) {
        console.error('Failed to fetch analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, [role]);

  if (loading) return <LoadingState message="Loading Analytics..." />;

  if (role !== UserRole.TECHNICIAN || !stats) {
    return (
      <div className="min-h-screen bg-dark-950 flex items-center justify-center text-slate-400">
        Analytics are only available for Technician accounts.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-dark-950 py-8 text-white selection:bg-sage-400/20 selection:text-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Performance Analytics</h1>
          <p className="text-sm text-slate-400 mt-1">
            Track your earnings, completion rates, and master rating.
          </p>
        </div>

        {/* Overview KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card flex flex-col justify-between hover:border-sage-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-400 uppercase">Total Earnings</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 flex items-center justify-center">
                <DollarSign className="w-4 h-4 text-emerald-400" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-bold font-mono text-white">₹{(stats.total_earnings || 0).toFixed(2)}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-[10px] text-emerald-400 font-mono">+12% vs last month</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card flex flex-col justify-between hover:border-sage-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-400 uppercase">Completed Services</span>
              <div className="w-8 h-8 rounded-lg bg-sky-500/10 flex items-center justify-center">
                <Briefcase className="w-4 h-4 text-sky-400" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-bold font-mono text-white">{stats.completed || stats.completed_jobs_count || 0}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-slate-500" />
                <span className="text-[10px] text-slate-400 font-mono">Total assignments finished</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card flex flex-col justify-between hover:border-sage-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-400 uppercase">Master Rating</span>
              <div className="w-8 h-8 rounded-lg bg-sage-500/10 flex items-center justify-center">
                <Star className="w-4 h-4 text-sage-400 fill-sage-400" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-bold font-mono text-sage-400">{(stats.average_rating || stats.rating_avg || 0).toFixed(1)}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <span className="text-[10px] text-slate-400 font-mono">Based on {stats.total_reviews || 0} reviews</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card flex flex-col justify-between hover:border-sage-500/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-400 uppercase">Completion Rate</span>
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-indigo-400" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-bold font-mono text-white">{((stats.completion_rate || 1) * 100).toFixed(0)}%</p>
              <div className="flex items-center gap-1.5 mt-2">
                <span className="text-[10px] text-slate-400 font-mono">High reliability score</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
            <h3 className="text-base font-bold text-white mb-6">Pipeline Breakdown</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Total Assigned</span>
                <span className="font-mono text-white">{stats.total_assigned || 0}</span>
              </div>
              <div className="h-px bg-dark-800" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Accepted</span>
                <span className="font-mono text-white">{stats.accepted || 0}</span>
              </div>
              <div className="h-px bg-dark-800" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">In Progress</span>
                <span className="font-mono text-white">{stats.in_progress || stats.active_jobs_count || 0}</span>
              </div>
              <div className="h-px bg-dark-800" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Cancelled</span>
                <span className="font-mono text-rose-400">{stats.cancelled || 0}</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-dark-900 border border-dark-750 shadow-card">
            <h3 className="text-base font-bold text-white mb-6">Financial Overview</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Cleared Earnings</span>
                <span className="font-mono text-emerald-400">₹{(stats.total_earnings || 0).toFixed(2)}</span>
              </div>
              <div className="h-px bg-dark-800" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-400">Pending Payouts</span>
                <span className="font-mono text-amber-400">₹{(stats.pending_earnings || 0).toFixed(2)}</span>
              </div>
              <div className="mt-6 p-4 rounded-2xl bg-dark-850 border border-dark-750 flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-500/10 flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-white">Direct Deposit Active</p>
                  <p className="text-xs text-slate-400 mt-1">Earnings are automatically disbursed to your linked bank account every week.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
