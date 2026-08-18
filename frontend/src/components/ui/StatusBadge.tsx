import React from 'react';
import { Clock, CheckCircle2, AlertCircle, Car, ShieldCheck, Play, XCircle, RotateCcw } from 'lucide-react';
import { BookingStatus } from '../../types';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

interface StatusBadgeProps {
  status: BookingStatus | string;
  className?: string;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, className }) => {
  const norm = String(status).toLowerCase();

  const getStatusConfig = () => {
    switch (norm) {
      case 'pending':
        return {
          label: 'Pending',
          icon: Clock,
          classes: 'bg-amber-500/10 text-amber-400 border-amber-500/30',
        };
      case 'assigned':
        return {
          label: 'Assigned',
          icon: Clock,
          classes: 'bg-sky-500/10 text-sky-400 border-sky-500/30',
        };
      case 'accepted':
      case 'confirmed':
        return {
          label: 'Accepted',
          icon: CheckCircle2,
          classes: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
        };
      case 'on_the_way':
        return {
          label: 'En Route',
          icon: Car,
          classes: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30 animate-pulse',
        };
      case 'arrived':
        return {
          label: 'Arrived',
          icon: ShieldCheck,
          classes: 'bg-purple-500/10 text-purple-400 border-purple-500/30',
        };
      case 'waiting_qr':
        return {
          label: 'Verify QR',
          icon: ShieldCheck,
          classes: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
        };
      case 'qr_verified':
        return {
          label: 'QR Verified',
          icon: CheckCircle2,
          classes: 'bg-teal-500/10 text-teal-400 border-teal-500/30',
        };
      case 'in_progress':
        return {
          label: 'In Progress',
          icon: Play,
          classes: 'bg-brand-500/15 text-brand-400 border-brand-500/30',
        };
      case 'completed':
      case 'paid':
      case 'issued':
        return {
          label: 'Completed',
          icon: CheckCircle2,
          classes: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
      case 'cancelled':
      case 'failed':
      case 'rejected':
        return {
          label: 'Cancelled',
          icon: XCircle,
          classes: 'bg-rose-500/10 text-rose-400 border-rose-500/30',
        };
      case 'refunded':
        return {
          label: 'Refunded',
          icon: RotateCcw,
          classes: 'bg-slate-500/10 text-slate-400 border-slate-500/30',
        };
      default:
        return {
          label: status.replace(/_/g, ' '),
          icon: AlertCircle,
          classes: 'bg-dark-800 text-slate-300 border-dark-700/80',
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  return (
    <span
      className={twMerge(
        clsx(
          'inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border capitalize transition-colors',
          config.classes,
          className
        )
      )}
    >
      <Icon className="w-3 h-3" />
      <span>{config.label}</span>
    </span>
  );
};
