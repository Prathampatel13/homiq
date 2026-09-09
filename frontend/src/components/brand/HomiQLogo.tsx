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

  // Refined Minimal Geometric Emblem in Sage & Rose Palette
  const HomiQMark = () => (
    <svg
      width={markSize}
      height={markSize}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0 select-none transition-transform duration-300 group-hover:scale-105"
      style={{ filter: 'drop-shadow(0 0 10px rgba(184, 219, 128, 0.25))' }}
    >
      <defs>
        {/* Primary Sage Gradient */}
        <linearGradient id="homiqSageGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#C6E294" />
          <stop offset="50%" stopColor="#B8DB80" />
          <stop offset="100%" stopColor="#9FC964" />
        </linearGradient>

        {/* Secondary Rose Accent Gradient */}
        <linearGradient id="homiqRoseGrad" x1="20" y1="0" x2="80" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#F39EB6" />
          <stop offset="100%" stopColor="#C55B79" />
        </linearGradient>

        {/* Dark Slate Bevel */}
        <linearGradient id="homiqBevel" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#252C38" />
          <stop offset="100%" stopColor="#12161E" />
        </linearGradient>
      </defs>

      {/* Dark Chamfered Base Badge */}
      <rect x="4" y="4" width="92" height="92" rx="22" fill="url(#homiqBevel)" stroke="rgba(255,255,255,0.08)" strokeWidth="1.5" />

      {/* First Architectural Angular Chevron (Back Blade in Rose Accent) */}
      <path
        d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
        fill="url(#homiqRoseGrad)"
        opacity="0.8"
      />

      {/* Second Architectural Angular Chevron (Forward Thrust Blade in Sage) */}
      <path
        d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
        fill="url(#homiqSageGrad)"
      />

      {/* Precision Core Indicator Dot (Warm Cream) */}
      <circle cx="76" cy="50" r="3.5" fill="#F7F6D3" opacity="0.95" />
    </svg>
  );

  // Clean, Minimal Editorial Wordmark
  const Wordmark = () => (
    <div className="flex items-baseline">
      <span className={`font-bold tracking-tight select-none ${sizeMap.text} leading-none font-sans text-white`}>
        Homi
      </span>
      <span className={`font-black tracking-tight select-none ${sizeMap.text} leading-none font-sans text-sage-400 ml-0.5 relative`}>
        Q
        <span className="inline-block w-1.5 h-1.5 rounded-full bg-sage-400 ml-0.5 shadow-[0_0_8px_rgba(184,219,128,0.7)]" />
      </span>
    </div>
  );

  // Minimal Tagline
  const Tagline = () => (
    <span
      className={`font-mono uppercase tracking-[0.22em] font-medium text-slate-400 select-none ${sizeMap.tag} mt-0.5`}
    >
      PREMIUM HOME SERVICES
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
