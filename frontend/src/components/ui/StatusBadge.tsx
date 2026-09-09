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
          bg: 'bg-emerald-50 border-emerald-300 text-emerald-700 font-bold',
          icon: CheckCircle2,
        };
      case 'waiting_payment':
      case 'payment_pending':
        return {
          label: 'Payment Pending',
          bg: 'bg-orange-50 border-orange-300 text-orange-700 font-bold',
          icon: Clock,
        };
      case 'in_progress':
      case 'started':
      case 'service_started':
        return {
          label: 'In Progress',
          bg: 'bg-sage-50 border-sage-300 text-sage-700 font-bold',
          icon: Play,
        };
      case 'assigned':
      case 'accepted':
        return {
          label: 'Technician Assigned',
          bg: 'bg-cyan-50 border-cyan-300 text-cyan-800 font-bold',
          icon: UserCheck,
        };
      case 'on_the_way':
      case 'start_trip':
      case 'dispatched':
        return {
          label: 'On The Way',
          bg: 'bg-sky-50 border-sky-300 text-sky-800 font-bold',
          icon: Navigation,
        };
      case 'arrived':
        return {
          label: 'Technician Arrived',
          bg: 'bg-indigo-50 border-indigo-300 text-indigo-800 font-bold',
          icon: ShieldCheck,
        };
      case 'confirmed':
      case 'booked':
        return {
          label: 'Confirmed',
          bg: 'bg-slate-100 border-slate-300 text-slate-800 font-bold',
          icon: Clock,
        };
      case 'pending':
      case 'created':
        return {
          label: 'Pending Assignment',
          bg: 'bg-amber-50 border-amber-300 text-amber-800 font-bold',
          icon: Clock,
        };
      case 'cancelled':
      case 'rejected':
      case 'failed':
      case 'suspended':
        return {
          label: normStatus.charAt(0).toUpperCase() + normStatus.slice(1),
          bg: 'bg-rose-50 border-rose-300 text-rose-700 font-bold',
          icon: XCircle,
        };
      default:
        return {
          label: status || 'Unknown',
          bg: 'bg-slate-100 border-slate-300 text-slate-700 font-bold',
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
