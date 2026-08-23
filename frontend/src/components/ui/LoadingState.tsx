import React from 'react';
import { HomiQLogo } from '../brand/HomiQLogo';

export interface LoadingStateProps {
  message?: string;
  fullScreen?: boolean;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Loading HomiQ Ecosystem...',
  fullScreen = false,
}) => {
  const content = (
    <div className="flex flex-col items-center justify-center p-8 text-center space-y-4 animate-in fade-in duration-300">
      <div className="relative">
        <div className="w-12 h-12 rounded-2xl bg-dark-850 border border-dark-750 flex items-center justify-center shadow-card">
          <HomiQLogo variant="mark" size="sm" />
        </div>
        <div className="absolute -inset-1 rounded-2xl border border-sage-400/30 animate-ping opacity-30 pointer-events-none" />
      </div>
      <p className="text-xs font-mono text-slate-400 tracking-wide">{message}</p>
    </div>
  );

  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-dark-950/95 backdrop-blur-md flex items-center justify-center z-50">
        {content}
      </div>
    );
  }

  return content;
};
