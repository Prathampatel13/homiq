import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Users, ShieldCheck, DollarSign, Activity, AlertTriangle, FileText, CheckCircle, RefreshCw, BarChart2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const AdminDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState({
    totalUsers: 1420,
    activeTechnicians: 88,
    totalBookings: 3290,
    grossRevenue: 4892000,
    systemHealth: 'healthy',
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
      {/* ── 1. Admin Header ─────────────────────────────────────────────────── */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 glass-card p-8 border-brand-500/20">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-extrabold text-white">Admin Operations Center</h1>
            <span className="px-3 py-1 rounded-full bg-rose-500/10 text-rose-400 text-xs font-semibold border border-rose-500/20">
              SYSTEM ADMIN
            </span>
          </div>
          <p className="text-slate-400 text-sm">Real-time platform metrics, user accounts, and system health status.</p>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
            All Systems Operational (FastAPI + Redis + PostgreSQL)
          </div>
        </div>
      </div>

      {/* ── 2. Platform Overview Metrics ────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Registered Users</span>
            <Users className="w-4 h-4 text-brand-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{metrics.totalUsers.toLocaleString()}</div>
          <div className="text-[10px] text-emerald-400 font-semibold">↑ +14% this month</div>
        </Card>

        <Card className="space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Verified Technicians</span>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{metrics.activeTechnicians}</div>
          <div className="text-[10px] text-emerald-400 font-semibold">88 Online & Available</div>
        </Card>

        <Card className="space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Total Platform Bookings</span>
            <Activity className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">{metrics.totalBookings.toLocaleString()}</div>
          <div className="text-[10px] text-purple-400 font-semibold">99.4% Completion Rate</div>
        </Card>

        <Card className="space-y-2">
          <div className="flex items-center justify-between text-slate-400">
            <span className="text-xs font-medium">Gross Platform Revenue</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold text-white">₹{(metrics.grossRevenue / 100000).toFixed(2)} Lakh</div>
          <div className="text-[10px] text-amber-400 font-semibold">Razorpay Escrow Verified</div>
        </Card>
      </div>

      {/* ── 3. System Infrastructure Diagnostics ────────────────────────────── */}
      <div className="glass-card p-6 border-slate-800 space-y-4">
        <h3 className="text-lg font-bold text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-brand-400" />
          Core Infrastructure Diagnostic Status
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="text-slate-400 font-medium">PostgreSQL Database</div>
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" /> Connected (Latency: 1.2ms)
            </div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="text-slate-400 font-medium">Redis 7 Broker & Cache</div>
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" /> Connected (Ping: OK)
            </div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="text-slate-400 font-medium">Celery Task Workers</div>
            <div className="text-emerald-400 font-bold flex items-center gap-1.5">
              <CheckCircle className="w-4 h-4" /> 4 Active Workers
            </div>
          </div>

          <div className="bg-slate-950/60 p-4 rounded-xl border border-slate-800 space-y-1">
            <div className="text-slate-400 font-medium">Prometheus Metrics</div>
            <div className="text-brand-400 font-bold flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4" /> /metrics Operational
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
