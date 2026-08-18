import React from 'react';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';
import { Card } from './Card';

export interface StatsCardProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  change?: string | number;
  changeType?: 'increase' | 'decrease' | 'neutral';
  subtext?: string;
  className?: string;
}

export const StatsCard: React.FC<StatsCardProps> = ({
  label,
  value,
  icon: Icon,
  change,
  changeType = 'neutral',
  subtext,
  className = '',
}) => {
  return (
    <Card className={`p-5 relative overflow-hidden ${className}`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider">{label}</p>
          <h3 className="text-2xl font-bold text-white mt-1.5 font-mono tracking-tight">{value}</h3>
        </div>
        <div className="w-10 h-10 rounded-xl bg-dark-850 border border-dark-750 flex items-center justify-center text-slate-300 shadow-subtle">
          <Icon className="w-5 h-5 text-brand-400" />
        </div>
      </div>

      {(change !== undefined || subtext) && (
        <div className="flex items-center gap-2 mt-4 pt-3 border-t border-dark-800/80 text-xs">
          {change !== undefined && (
            <span
              className={`inline-flex items-center gap-1 font-semibold ${
                changeType === 'increase'
                  ? 'text-emerald-400'
                  : changeType === 'decrease'
                  ? 'text-rose-400'
                  : 'text-slate-400'
              }`}
            >
              {changeType === 'increase' ? (
                <TrendingUp className="w-3.5 h-3.5" />
              ) : changeType === 'decrease' ? (
                <TrendingDown className="w-3.5 h-3.5" />
              ) : null}
              {typeof change === 'number' ? `${change > 0 ? '+' : ''}${change}%` : change}
            </span>
          )}
          {subtext && <span className="text-slate-500">{subtext}</span>}
        </div>
      )}
    </Card>
  );
};
