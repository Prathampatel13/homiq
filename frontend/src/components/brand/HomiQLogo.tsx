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
    xl: { mark: 64, text: 'text-4xl', tag: 'text-sm', gap: 'gap-4' },
  }[size];

  const markSize = sizeMap.mark;

  // Official HomiQ Architectural Mark SVG: House Silhouette + Integrated Chrome Q + Sage Mint Accent
  const HomiQMark = () => (
    <svg
      width={markSize}
      height={markSize}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className="shrink-0 drop-shadow-sm select-none"
    >
      <defs>
        {/* Metallic / Chrome Brushed Gradient for Architectural House Mark */}
        <linearGradient id="homiqChrome" x1="15" y1="10" x2="85" y2="90" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="25%" stopColor="#E4E7EB" />
          <stop offset="50%" stopColor="#A8B0BA" />
          <stop offset="75%" stopColor="#D4D9DE" />
          <stop offset="100%" stopColor="#8FA8A0" />
        </linearGradient>

        {/* Restrained Sage Mint Accent Gradient */}
        <linearGradient id="homiqSage" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#A6C2B9" />
          <stop offset="60%" stopColor="#8FA8A0" />
          <stop offset="100%" stopColor="#678078" />
        </linearGradient>

        <linearGradient id="homiqDarkSurface" x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
          <stop offset="0%" stopColor="#181C22" />
          <stop offset="100%" stopColor="#08090B" />
        </linearGradient>
      </defs>

      {/* Outer Housing Container */}
      <rect width="100" height="100" rx="22" fill="url(#homiqDarkSurface)" />

      {/* Architectural Pitched Roof Structure */}
      <path
        d="M 50 14 L 84 41 L 84 56 L 75 49 L 50 29 L 25 49 L 16 56 L 16 41 Z"
        fill="url(#homiqChrome)"
      />

      {/* Subtle Chimney Element with Sage Accent */}
      <path
        d="M 68 22 L 77 29 L 77 18 L 68 18 Z"
        fill="url(#homiqSage)"
        opacity="0.9"
      />

      {/* Integrated Circular 'Q' Body */}
      <path
        d="M 50 36 C 65.46 36 78 48.54 78 64 C 78 70.8 75.56 77.03 71.49 81.88 L 84 94.39 L 74.39 104 L 62.15 91.76 C 58.46 93.83 54.36 95 50 95 C 34.54 95 22 82.46 22 67 C 22 51.54 34.54 39 50 39 Z"
        transform="scale(0.88) translate(6.8, 4)"
        fill="url(#homiqChrome)"
        fillRule="evenodd"
      />

      {/* Inner Q Aperture */}
      <circle cx="50" cy="63" r="16" fill="#08090B" />
      
      {/* Central Intelligent Core / Keyhole Indicator */}
      <circle cx="50" cy="63" r="6.5" fill="url(#homiqSage)" />
      <rect x="47.5" y="42" width="5" height="7" rx="1.5" fill="url(#homiqSage)" />
    </svg>
  );

  // Wordmark: 'Homi' in clean geometric sans + 'Q' with metallic chrome / sage accent
  const Wordmark = () => (
    <span className={`font-extrabold tracking-tight select-none ${sizeMap.text} leading-none font-sans`}>
      <span className={theme === 'dark' ? 'text-white' : 'text-dark-950'}>Homi</span>
      <span className="bg-gradient-to-tr from-sage-400 via-light-pure to-sage-300 bg-clip-text text-transparent ml-0.5">
        Q
      </span>
    </span>
  );

  // Official Tagline
  const Tagline = () => (
    <span
      className={`font-mono uppercase tracking-[0.25em] font-medium text-slate-400 select-none ${sizeMap.tag}`}
    >
      SMARTER HOMES. SIMPLER LIVING.
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
        <div className="flex flex-col items-center gap-1">
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
