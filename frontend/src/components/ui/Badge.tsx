import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'neutral' | 'brand' | 'success' | 'warning' | 'danger' | 'outline';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'neutral',
  size = 'md',
  className,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center gap-1.5 font-medium rounded-full transition-colors';

  const sizeStyles = {
    sm: 'px-2 py-0.5 text-[10px] tracking-wide',
    md: 'px-2.5 py-0.5 text-xs',
  };

  const variantStyles = {
    neutral: 'bg-slate-100 text-slate-700 border border-slate-200 font-semibold',
    brand: 'bg-sage-50 text-sage-700 border border-sage-200 font-semibold',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200 font-semibold',
    warning: 'bg-amber-50 text-amber-800 border border-amber-200 font-semibold',
    danger: 'bg-rose-50 text-rose-700 border border-rose-200 font-semibold',
    outline: 'bg-transparent text-slate-700 border border-slate-300 font-semibold',
  };

  return (
    <span className={twMerge(clsx(baseStyles, sizeStyles[size], variantStyles[variant], className))} {...props}>
      {children}
    </span>
  );
};
