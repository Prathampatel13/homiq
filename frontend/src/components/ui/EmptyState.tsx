import React from 'react';
import { LucideIcon, FolderOpen } from 'lucide-react';

export interface EmptyStateProps {
  title: string;
  description: string;
  icon?: LucideIcon;
  actionLabel?: string;
  onAction?: () => void;
  actionIcon?: LucideIcon;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  title,
  description,
  icon: Icon = FolderOpen,
  actionLabel,
  onAction,
  actionIcon: ActionIcon,
  className = '',
}) => {
  return (
    <div className={`p-8 sm:p-12 rounded-3xl bg-dark-900/60 border border-dark-750 flex flex-col items-center justify-center text-center ${className}`}>
      <div className="w-14 h-14 rounded-2xl bg-dark-850 border border-dark-750 flex items-center justify-center text-sage-400 mb-4 shadow-subtle">
        <Icon className="w-7 h-7 stroke-[1.5]" />
      </div>
      <h3 className="text-base font-bold text-white tracking-tight mb-1.5">{title}</h3>
      <p className="text-xs text-slate-400 max-w-md leading-relaxed mb-6">{description}</p>
      
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="btn-primary text-xs px-4 py-2 flex items-center gap-1.5 shadow-subtle hover:shadow-accent"
        >
          {ActionIcon && <ActionIcon className="w-3.5 h-3.5" />}
          <span>{actionLabel}</span>
        </button>
      )}
    </div>
  );
};
