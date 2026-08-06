import React from 'react';
import { BookingStatus } from '../../types';

interface BadgeProps {
  status?: BookingStatus | string;
  variant?: 'success' | 'warning' | 'info' | 'danger' | 'neutral';
  children?: React.ReactNode;
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  status,
  variant,
  children,
  className = '',
}) => {
  const getBadgeStyle = () => {
    if (variant) {
      const styles = {
        success: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
        warning: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        info: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        danger: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        neutral: 'bg-slate-800 text-slate-300 border-slate-700',
      };
      return styles[variant];
    }

    switch (status) {
      case BookingStatus.COMPLETED:
        return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      case BookingStatus.IN_PROGRESS:
      case BookingStatus.ACCEPTED:
      case BookingStatus.ON_THE_WAY:
      case BookingStatus.ARRIVED:
        return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
      case BookingStatus.WAITING_QR:
      case BookingStatus.QR_VERIFIED:
        return 'bg-purple-500/15 text-purple-400 border-purple-500/30';
      case BookingStatus.ASSIGNED:
        return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
      case BookingStatus.CANCELLED:
        return 'bg-rose-500/15 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-800 text-slate-300 border-slate-700';
    }
  };

  const displayText = children || (status ? status.replace(/_/g, ' ') : '');

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold border backdrop-blur-md uppercase tracking-wider ${getBadgeStyle()} ${className}`}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      {displayText}
    </span>
  );
};
