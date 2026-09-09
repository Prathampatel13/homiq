import React, { useEffect, useState } from 'react';
import { technicianApi } from '../api/technician';
import { useAuthStore } from '../store/useAuthStore';
import { UserRole } from '../types';
import { BarChart3, IndianRupee, Briefcase, Star, TrendingUp, CheckCircle2 } from 'lucide-react';
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
      <div className="min-h-screen bg-[#F8FAFC] flex items-center justify-center text-slate-600 font-medium">
        Analytics are only available for Technician accounts.
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#F8FAFC] py-8 text-slate-900 selection:bg-sage-500/20 selection:text-slate-900">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
        <div>
          <h1 className="text-2xl font-extrabold tracking-tight text-slate-900">Performance Analytics</h1>
          <p className="text-sm text-slate-600 mt-1">
            Track your earnings, completion rates, and master rating.
          </p>
        </div>

        {/* Overview KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card flex flex-col justify-between hover:border-sage-500/40 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-500 uppercase font-semibold">Total Earnings</span>
              <div className="w-8 h-8 rounded-lg bg-emerald-50 border border-emerald-200 flex items-center justify-center">
                <IndianRupee className="w-4 h-4 text-emerald-600" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold font-mono text-slate-900">₹{(stats.total_earnings || 0).toFixed(2)}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-[10px] text-emerald-700 font-mono font-semibold">+12% vs last month</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card flex flex-col justify-between hover:border-sage-500/40 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-500 uppercase font-semibold">Completed Services</span>
              <div className="w-8 h-8 rounded-lg bg-sky-50 border border-sky-200 flex items-center justify-center">
                <Briefcase className="w-4 h-4 text-sky-600" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold font-mono text-slate-900">{stats.completed || stats.completed_jobs_count || 0}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <CheckCircle2 className="w-3.5 h-3.5 text-slate-400" />
                <span className="text-[10px] text-slate-500 font-mono">Total assignments finished</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card flex flex-col justify-between hover:border-sage-500/40 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-500 uppercase font-semibold">Master Rating</span>
              <div className="w-8 h-8 rounded-lg bg-amber-50 border border-amber-200 flex items-center justify-center">
                <Star className="w-4 h-4 text-amber-500 fill-amber-400" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold font-mono text-slate-900">{(stats.average_rating || stats.rating_avg || 0).toFixed(1)}</p>
              <div className="flex items-center gap-1.5 mt-2">
                <span className="text-[10px] text-slate-500 font-mono">Based on {stats.total_reviews || 0} reviews</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card flex flex-col justify-between hover:border-sage-500/40 transition-colors">
            <div className="flex items-center justify-between mb-4">
              <span className="text-xs font-mono text-slate-500 uppercase font-semibold">Completion Rate</span>
              <div className="w-8 h-8 rounded-lg bg-indigo-50 border border-indigo-200 flex items-center justify-center">
                <BarChart3 className="w-4 h-4 text-indigo-600" />
              </div>
            </div>
            <div>
              <p className="text-3xl font-extrabold font-mono text-slate-900">{((stats.completion_rate || 1) * 100).toFixed(0)}%</p>
              <div className="flex items-center gap-1.5 mt-2">
                <span className="text-[10px] text-slate-500 font-mono">High reliability score</span>
              </div>
            </div>
          </div>
        </div>

        {/* Detailed Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card">
            <h3 className="text-base font-bold text-slate-900 mb-6">Pipeline Breakdown</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Total Assigned</span>
                <span className="font-mono text-slate-900 font-bold">{stats.total_assigned || 0}</span>
              </div>
              <div className="h-px bg-slate-100" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Accepted</span>
                <span className="font-mono text-slate-900 font-bold">{stats.accepted || 0}</span>
              </div>
              <div className="h-px bg-slate-100" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">In Progress</span>
                <span className="font-mono text-slate-900 font-bold">{stats.in_progress || stats.active_jobs_count || 0}</span>
              </div>
              <div className="h-px bg-slate-100" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Cancelled</span>
                <span className="font-mono text-rose-600 font-bold">{stats.cancelled || 0}</span>
              </div>
            </div>
          </div>

          <div className="p-6 rounded-3xl bg-white border border-slate-200 shadow-card">
            <h3 className="text-base font-bold text-slate-900 mb-6">Financial Overview</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Cleared Earnings</span>
                <span className="font-mono text-emerald-700 font-bold">₹{(stats.total_earnings || 0).toFixed(2)}</span>
              </div>
              <div className="h-px bg-slate-100" />
              <div className="flex items-center justify-between">
                <span className="text-sm text-slate-600">Pending Payouts</span>
                <span className="font-mono text-amber-700 font-bold">₹{(stats.pending_earnings || 0).toFixed(2)}</span>
              </div>
              <div className="mt-6 p-4 rounded-2xl bg-slate-50 border border-slate-200 flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-emerald-50 border border-emerald-200 flex items-center justify-center shrink-0">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                </div>
                <div>
                  <p className="text-sm font-bold text-slate-900">Direct Deposit Active</p>
                  <p className="text-xs text-slate-600 mt-1">Earnings are automatically disbursed to your linked bank account every week.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};
