import React from 'react';

export interface HomiQLogoProps {
  variant?: 'full' | 'horizontal' | 'stacked' | 'mark' | 'icon';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  theme?: 'dark' | 'light';
  showTagline?: boolean;
  className?: string;
}

export const HomiQLogo: React.FC<HomiQLogoProps> = ({
  variant = 'horizontal',
  size = 'md',
  theme = 'dark',
  showTagline = false,
  className = '',
}) => {
  const sizeMap = {
    xs: { mark: 22, text: 'text-sm', tag: 'text-[8px]', gap: 'gap-2' },
    sm: { mark: 28, text: 'text-base', tag: 'text-[9px]', gap: 'gap-2.5' },
    md: { mark: 36, text: 'text-xl', tag: 'text-[10px]', gap: 'gap-3' },
    lg: { mark: 48, text: 'text-2xl', tag: 'text-xs', gap: 'gap-3.5' },
    xl: { mark: 60, text: 'text-4xl', tag: 'text-sm', gap: 'gap-4' },
  }[size];

  const markSize = sizeMap.mark;

  // High-Precision Industrial Chevron / Hex Emblem in Ekvator Flame Orange
  const HomiQMark = () => (
    <svg
      width={markSize}
      height={markSize}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0 select-none transition-transform duration-300 group-hover:scale-105"
      style={{ filter: 'drop-shadow(0 0 12px rgba(217, 56, 30, 0.4))' }}
    >
      <defs>
        {/* Primary Industrial Orange Gradient */}
        <linearGradient id="homiqOrangeGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FF6B4A" />
          <stop offset="50%" stopColor="#E74320" />
          <stop offset="100%" stopColor="#C02C15" />
        </linearGradient>

        {/* Secondary Deep Ember Gradient */}
        <linearGradient id="homiqEmberGrad" x1="20" y1="0" x2="80" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#E74320" />
          <stop offset="100%" stopColor="#871A0B" />
        </linearGradient>

        {/* Dark Metallic Bevel */}
        <linearGradient id="homiqBevel" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#2A2A2A" />
          <stop offset="100%" stopColor="#141414" />
        </linearGradient>
      </defs>

      {/* Dark Chamfered Base Badge */}
      <rect x="4" y="4" width="92" height="92" rx="20" fill="url(#homiqBevel)" stroke="rgba(255,255,255,0.08)" strokeWidth="2" />

      {/* First Architectural Angular Chevron (Back Blade) */}
      <path
        d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
        fill="url(#homiqEmberGrad)"
        opacity="0.85"
      />

      {/* Second Architectural Angular Chevron (Forward Thrust Blade) */}
      <path
        d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
        fill="url(#homiqOrangeGrad)"
      />

      {/* Precision Core Indicator Dot */}
      <circle cx="76" cy="50" r="3.5" fill="#FFFFFF" opacity="0.9" />
    </svg>
  );

  // Clean, Bold Editorial Wordmark
  const Wordmark = () => (
    <div className="flex items-baseline">
      <span className={`font-extrabold tracking-tight select-none ${sizeMap.text} leading-none font-sans text-white`}>
        Homi
      </span>
      <span className={`font-black tracking-tight select-none ${sizeMap.text} leading-none font-sans text-sage-500 ml-0.5 relative`}>
        Q
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-sage-500 ml-0.5 shadow-[0_0_8px_rgba(217,56,30,0.8)]" />
      </span>
    </div>
  );

  // Official Tagline
  const Tagline = () => (
    <span
      className={`font-mono uppercase tracking-[0.25em] font-semibold text-slate-400 select-none ${sizeMap.tag} mt-0.5`}
    >
      SMART HOME ENGINEERING
    </span>
  );

  // Variant Rendering
  if (variant === 'mark' || variant === 'icon') {
    return (
      <div className={`inline-flex items-center justify-center ${className}`}>
        <HomiQMark />
      </div>
    );
  }

  if (variant === 'stacked') {
    return (
      <div className={`inline-flex flex-col items-center text-center ${sizeMap.gap} ${className}`}>
        <HomiQMark />
        <div className="flex flex-col items-center">
          <Wordmark />
          {(showTagline || variant === 'stacked') && <Tagline />}
        </div>
      </div>
    );
  }

  // Horizontal / Full Variant
  return (
    <div className={`inline-flex items-center ${sizeMap.gap} ${className}`}>
      <HomiQMark />
      <div className="flex flex-col justify-center">
        <Wordmark />
        {showTagline && <Tagline />}
      </div>
    </div>
  );
};

export default HomiQLogo;
