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
          'bg-dark-900/90 border border-dark-700/60 rounded-2xl p-5 shadow-card transition-all duration-200',
          interactive && 'hover:bg-dark-850 hover:border-dark-750 cursor-pointer hover:shadow-subtle',
          className
        )
      )}
      {...props}
    >
      {children}
    </div>
  );
};
