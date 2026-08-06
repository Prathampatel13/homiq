import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, className = '', id, ...props }, ref) => {
    const inputId = id || props.name;

    return (
      <div className="w-full flex flex-col gap-1.5">
        {label && (
          <label htmlFor={inputId} className="text-xs font-medium text-slate-300">
            {label}
          </label>
        )}

        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3.5 text-slate-400 pointer-events-none">
              {leftIcon}
            </div>
          )}

          <input
            id={inputId}
            ref={ref}
            className={`w-full px-4 py-2.5 bg-slate-900/80 border ${
              error ? 'border-red-500/80 focus:ring-red-500' : 'border-slate-800 focus:border-brand-500 focus:ring-brand-500'
            } rounded-xl text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-opacity-50 transition-all duration-200 ${
              leftIcon ? 'pl-10' : ''
            } ${rightIcon ? 'pr-10' : ''} ${className}`}
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3.5 text-slate-400">
              {rightIcon}
            </div>
          )}
        </div>

        {error && <span className="text-xs text-red-400 font-medium">{error}</span>}
        {helperText && !error && <span className="text-xs text-slate-500">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = 'Input';
