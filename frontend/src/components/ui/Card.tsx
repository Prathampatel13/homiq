import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  interactive?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, interactive = false, className, ...props }) => {
  return (
    <div
      className={twMerge(
        clsx(
          'bg-white border border-slate-200 rounded-2xl p-5 shadow-card text-slate-900 transition-all duration-200',
          interactive && 'hover:bg-slate-50 hover:border-slate-300 cursor-pointer hover:shadow-subtle',
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};

