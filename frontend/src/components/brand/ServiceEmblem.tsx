import React from 'react';

export type ServiceCategoryKey = 'ac' | 'electrical' | 'plumbing' | 'security' | 'cleaning' | 'carpentry' | string;

export interface ServiceEmblemProps {
  category: ServiceCategoryKey;
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'hero';
  className?: string;
}

export const ServiceEmblem: React.FC<ServiceEmblemProps> = ({
  category,
  size = 'md',
  className = '',
}) => {
  const catKey = (category || '').toLowerCase();

  const dimensions = {
    xs: { box: 28, radius: 8 },
    sm: { box: 42, radius: 11 },
    md: { box: 56, radius: 14 },
    lg: { box: 76, radius: 18 },
    hero: { box: 280, radius: 48 },
  }[size];

  // Pick trade palette and vector paths
  const getEmblemConfig = () => {
    switch (true) {
      case catKey.includes('ac') || catKey.includes('climate') || catKey.includes('cool'):
        return {
          id: 'ac',
          gradStart: '#4ADE80',
          gradEnd: '#16A34A',
          accentGradStart: '#38BDF8',
          accentGradEnd: '#0284C7',
          dotColor: '#F7F6D3',
          renderArt: () => (
            <>
              {/* Dual Aerodynamic Climate Blades */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#acAccentGrad)"
                opacity="0.85"
              />
              <path
                d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
                fill="url(#acSageGrad)"
              />
              {/* Center Frost Crystal Dot */}
              <circle cx="76" cy="50" r="4" fill="#F7F6D3" />
              {/* Modern Airflow Indicators */}
              <path
                d="M 28 36 Q 48 32 68 36"
                stroke="#FFFFFF"
                strokeWidth="2.5"
                strokeLinecap="round"
                opacity="0.6"
              />
              <path
                d="M 28 64 Q 48 68 68 64"
                stroke="#FFFFFF"
                strokeWidth="2.5"
                strokeLinecap="round"
                opacity="0.6"
              />
            </>
          ),
        };

      case catKey.includes('elec') || catKey.includes('wire') || catKey.includes('circuit'):
        return {
          id: 'electrical',
          gradStart: '#FBBF24',
          gradEnd: '#D97706',
          accentGradStart: '#4ADE80',
          accentGradEnd: '#16A34A',
          dotColor: '#FFFFFF',
          renderArt: () => (
            <>
              {/* High-Voltage Circuit Chevron */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#elecAccentGrad)"
                opacity="0.85"
              />
              {/* Precision Lightning Energy Core */}
              <path
                d="M 54 24 L 38 48 L 50 48 L 44 76 L 66 48 L 52 48 Z"
                fill="url(#elecGoldGrad)"
              />
              <circle cx="76" cy="50" r="4" fill="#FFFFFF" />
            </>
          ),
        };

      case catKey.includes('plumb') || catKey.includes('pipe') || catKey.includes('water') || catKey.includes('hydraul'):
        return {
          id: 'plumbing',
          gradStart: '#38BDF8',
          gradEnd: '#0284C7',
          accentGradStart: '#4ADE80',
          accentGradEnd: '#16A34A',
          dotColor: '#F7F6D3',
          renderArt: () => (
            <>
              {/* Hydraulic Pressure Chevron */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#plumbAccentGrad)"
                opacity="0.85"
              />
              <path
                d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
                fill="url(#plumbBlueGrad)"
              />
              {/* Teardrop Hydro Seal */}
              <path
                d="M 50 32 C 50 32 62 48 62 55 C 62 62 56 67 50 67 C 44 67 38 62 38 55 C 38 48 50 32 50 32 Z"
                fill="#FFFFFF"
                opacity="0.9"
              />
              <circle cx="76" cy="50" r="4" fill="#F7F6D3" />
            </>
          ),
        };

      case catKey.includes('sec') || catKey.includes('smart') || catKey.includes('lock'):
        return {
          id: 'security',
          gradStart: '#FB7185',
          gradEnd: '#E11D48',
          accentGradStart: '#4ADE80',
          accentGradEnd: '#16A34A',
          dotColor: '#FFFFFF',
          renderArt: () => (
            <>
              {/* Cyber Defense Shield Base Chevron */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#secAccentGrad)"
                opacity="0.85"
              />
              <path
                d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
                fill="url(#secRoseGrad)"
              />
              {/* Biometric Center Lock Shield */}
              <path
                d="M 40 40 Q 50 35 60 40 V 52 Q 50 65 40 52 Z"
                fill="#FFFFFF"
                opacity="0.95"
              />
              <circle cx="50" cy="46" r="2.5" fill="#E11D48" />
              <circle cx="76" cy="50" r="4" fill="#FFFFFF" />
            </>
          ),
        };

      case catKey.includes('clean') || catKey.includes('sanit') || catKey.includes('wash'):
        return {
          id: 'cleaning',
          gradStart: '#34D399',
          gradEnd: '#059669',
          accentGradStart: '#FB7185',
          accentGradEnd: '#E11D48',
          dotColor: '#F7F6D3',
          renderArt: () => (
            <>
              {/* Sparkle Blade Chevron */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#cleanAccentGrad)"
                opacity="0.85"
              />
              <path
                d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
                fill="url(#cleanMintGrad)"
              />
              {/* Radiant Sanitization Starburst */}
              <path
                d="M 50 30 Q 50 45 65 45 Q 50 45 50 60 Q 50 45 35 45 Q 50 45 50 30 Z"
                fill="#FFFFFF"
                opacity="0.95"
              />
              <circle cx="76" cy="50" r="4" fill="#F7F6D3" />
            </>
          ),
        };

      case catKey.includes('carp') || catKey.includes('repair') || catKey.includes('wood'):
      default:
        return {
          id: 'carpentry',
          gradStart: '#FB923C',
          gradEnd: '#C2410C',
          accentGradStart: '#4ADE80',
          accentGradEnd: '#16A34A',
          dotColor: '#FFFFFF',
          renderArt: () => (
            <>
              {/* Craftsman Structural Chevron */}
              <path
                d="M 24 50 L 44 26 L 56 26 L 36 50 L 56 74 L 44 74 Z"
                fill="url(#carpAccentGrad)"
                opacity="0.85"
              />
              <path
                d="M 44 50 L 64 26 L 76 26 L 56 50 L 76 74 L 64 74 Z"
                fill="url(#carpOrangeGrad)"
              />
              {/* Precision Square / Tool Indicator */}
              <path
                d="M 42 34 L 58 50 L 50 58 L 34 42 Z"
                fill="#FFFFFF"
                opacity="0.9"
              />
              <circle cx="76" cy="50" r="4" fill="#FFFFFF" />
            </>
          ),
        };
    }
  };

  const config = getEmblemConfig();

  return (
    <div className={`inline-flex items-center justify-center shrink-0 ${className}`}>
      <svg
        width={dimensions.box}
        height={dimensions.box}
        viewBox="0 0 100 100"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="shrink-0 select-none transition-transform duration-300 hover:scale-105"
        style={{
          filter: size === 'hero' 
            ? 'drop-shadow(0 20px 35px rgba(15, 23, 42, 0.14))' 
            : 'drop-shadow(0 2px 6px rgba(15, 23, 42, 0.08))'
        }}
      >
        <defs>
          {/* Beveled Dark Slate Foundation Matching Brand Emblem */}
          <linearGradient id={`${config.id}Bevel`} x1="0" y1="0" x2="100" y2="100" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#1E293B" />
            <stop offset="100%" stopColor="#0F172A" />
          </linearGradient>

          {/* Primary Trade Gradient */}
          <linearGradient id={`${config.id}SageGrad`} x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#4ADE80" />
            <stop offset="100%" stopColor="#16A34A" />
          </linearGradient>

          <linearGradient id={`${config.id}AccentGrad`} x1="20" y1="0" x2="80" y2="100" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor={config.accentGradStart} />
            <stop offset="100%" stopColor={config.accentGradEnd} />
          </linearGradient>

          {/* Dedicated service gradients */}
          <linearGradient id="elecGoldGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FDE047" />
            <stop offset="100%" stopColor="#D97706" />
          </linearGradient>

          <linearGradient id="plumbBlueGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="100%" stopColor="#0284C7" />
          </linearGradient>

          <linearGradient id="secRoseGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FB7185" />
            <stop offset="100%" stopColor="#E11D48" />
          </linearGradient>

          <linearGradient id="cleanMintGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#34D399" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>

          <linearGradient id="carpOrangeGrad" x1="10" y1="10" x2="90" y2="90" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#FB923C" />
            <stop offset="100%" stopColor="#C2410C" />
          </linearGradient>
        </defs>

        {/* Outer Chamfered Base Badge */}
        <rect
          x="4"
          y="4"
          width="92"
          height="92"
          rx="22"
          fill={`url(#${config.id}Bevel)`}
          stroke="rgba(255, 255, 255, 0.12)"
          strokeWidth="1.5"
        />

        {/* Vector Art */}
        {config.renderArt()}
      </svg>
    </div>
  );
};
