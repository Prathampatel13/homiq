import React from 'react';
import { clsx } from 'clsx';

export interface TabItem {
  id: string;
  label: string;
  count?: number;
  icon?: React.ComponentType<{ className?: string }>;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (tabId: string) => void;
  variant?: 'pills' | 'underline';
  className?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  variant = 'pills',
  className,
}) => {
  if (variant === 'underline') {
    return (
      <div className={clsx('flex items-center gap-6 border-b border-slate-200', className)}>
        {tabs.map((tab) => {
          const isActive = tab.id === activeTab;
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => onChange(tab.id)}
              className={clsx(
                'flex items-center gap-2 pb-3 text-sm font-medium transition-all relative',
                isActive ? 'text-sage-600 font-bold' : 'text-slate-600 hover:text-slate-900'
              )}
            >
              {Icon && <Icon className="w-4 h-4" />}
              <span>{tab.label}</span>
              {typeof tab.count === 'number' && (
                <span
                  className={clsx(
                    'px-2 py-0.5 text-xs rounded-full font-mono',
                    isActive ? 'bg-sage-100 text-sage-800' : 'bg-slate-100 text-slate-600'
                  )}
                >
                  {tab.count}
                </span>
              )}
              {isActive && (
                <span className="absolute bottom-0 inset-x-0 h-0.5 bg-sage-600 rounded-full" />
              )}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className={clsx('inline-flex items-center p-1 bg-slate-100 border border-slate-200 rounded-xl gap-1', className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        const Icon = tab.icon;
        return (
          <button
            key={tab.id}
            onClick={() => onChange(tab.id)}
            className={clsx(
              'flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all',
              isActive
                ? 'bg-white text-slate-900 shadow-subtle border border-slate-200'
                : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
            )}
          >
            {Icon && <Icon className="w-3.5 h-3.5" />}
            <span>{tab.label}</span>
            {typeof tab.count === 'number' && (
              <span
                className={clsx(
                  'px-1.5 py-0.5 rounded text-[10px] font-mono',
                  isActive ? 'bg-sage-100 text-sage-800' : 'bg-slate-200 text-slate-700'
                )}
              >
                {tab.count}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
};
