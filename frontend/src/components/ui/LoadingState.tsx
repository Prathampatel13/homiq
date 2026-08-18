import React from 'react';

export const LoadingState: React.FC<{ message?: string; className?: string }> = ({
  message = 'Loading data...',
  className = 'py-16',
}) => {
  return (
    <div className={`flex flex-col items-center justify-center text-center ${className}`}>
      <div className="relative w-10 h-10 mb-4">
        <div className="absolute inset-0 rounded-full border-2 border-dark-700"></div>
        <div className="absolute inset-0 rounded-full border-2 border-brand-500 border-t-transparent animate-spin"></div>
      </div>
      <p className="text-xs text-slate-400 font-medium tracking-wide">{message}</p>
    </div>
  );
};

export const CardSkeleton: React.FC<{ count?: number }> = ({ count = 3 }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {Array.from({ length: count }).map((_, idx) => (
        <div key={idx} className="bg-dark-900/90 border border-dark-700/60 rounded-2xl p-5 animate-pulse space-y-4">
          <div className="flex items-center justify-between">
            <div className="w-24 h-4 bg-dark-750 rounded"></div>
            <div className="w-16 h-4 bg-dark-750 rounded-full"></div>
          </div>
          <div className="w-3/4 h-5 bg-dark-700 rounded"></div>
          <div className="space-y-2">
            <div className="w-full h-3.5 bg-dark-800 rounded"></div>
            <div className="w-4/5 h-3.5 bg-dark-800 rounded"></div>
          </div>
          <div className="pt-3 border-t border-dark-800 flex items-center justify-between">
            <div className="w-20 h-5 bg-dark-700 rounded"></div>
            <div className="w-24 h-8 bg-dark-750 rounded-xl"></div>
          </div>
        </div>
      ))}
    </div>
  );
};
