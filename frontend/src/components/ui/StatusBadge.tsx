import React from 'react';
import { 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  UserCheck, 
  Navigation, 
  Play, 
  XCircle, 
  ShieldCheck 
} from 'lucide-react';

export interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  className = '',
  showIcon = true,
}) => {
  const normStatus = (status || '').toLowerCase().replace(/[\s-]/g, '_');

  const getStatusConfig = () => {
    switch (normStatus) {
      case 'completed':
      case 'verified':
      case 'paid':
      case 'active':
      case 'approved':
        return {
          label: 'Completed',
          bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400',
          icon: CheckCircle2,
        };
      case 'waiting_payment':
      case 'payment_pending':
        return {
          label: 'Payment Pending',
          bg: 'bg-orange-500/10 border-orange-500/30 text-orange-400',
          icon: Clock,
        };
      case 'in_progress':
      case 'started':
      case 'service_started':
        return {
          label: 'In Progress',
          bg: 'bg-sage-400/15 border-sage-400/40 text-sage-300',
          icon: Play,
        };
      case 'assigned':
      case 'accepted':
        return {
          label: 'Technician Assigned',
          bg: 'bg-cyan-500/10 border-cyan-500/30 text-cyan-400',
          icon: UserCheck,
        };
      case 'on_the_way':
      case 'start_trip':
      case 'dispatched':
        return {
          label: 'On The Way',
          bg: 'bg-sky-500/10 border-sky-500/30 text-sky-400',
          icon: Navigation,
        };
      case 'arrived':
        return {
          label: 'Technician Arrived',
          bg: 'bg-indigo-500/10 border-indigo-500/30 text-indigo-400',
          icon: ShieldCheck,
        };
      case 'confirmed':
      case 'booked':
        return {
          label: 'Confirmed',
          bg: 'bg-slate-500/10 border-slate-500/30 text-slate-300',
          icon: Clock,
        };
      case 'pending':
      case 'created':
        return {
          label: 'Pending Assignment',
          bg: 'bg-amber-500/10 border-amber-500/30 text-amber-400',
          icon: Clock,
        };
      case 'cancelled':
      case 'rejected':
      case 'failed':
      case 'suspended':
        return {
          label: normStatus.charAt(0).toUpperCase() + normStatus.slice(1),
          bg: 'bg-rose-500/10 border-rose-500/30 text-rose-400',
          icon: XCircle,
        };
      default:
        return {
          label: status || 'Unknown',
          bg: 'bg-dark-800 border-dark-750 text-slate-400',
          icon: AlertCircle,
        };
    }
  };

  const config = getStatusConfig();
  const Icon = config.icon;

  const sizeClasses = {
    sm: 'text-[10px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3.5 py-1.5 gap-2',
  }[size];

  return (
    <span
      className={`inline-flex items-center rounded-full font-mono font-medium border uppercase tracking-wider ${config.bg} ${sizeClasses} ${className}`}
    >
      {showIcon && <Icon className="w-3.5 h-3.5 shrink-0" />}
      <span>{config.label}</span>
    </span>
  );
};
