/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sage: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          300: '#4ADE80',
          400: '#16A34A', // High-contrast vibrant Sage / Emerald Green
          500: '#15803D',
          600: '#166534',
          700: '#14532D',
          800: '#14532D',
          900: '#052E16',
          950: '#022C22',
        },
        brand: {
          50: '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          300: '#4ADE80',
          400: '#16A34A',
          500: '#15803D',
          600: '#166534',
          700: '#14532D',
          800: '#14532D',
          900: '#052E16',
          950: '#022C22',
        },
        cream: {
          50: '#FFFEFA',
          100: '#FCFBEF',
          200: '#F7F6D3', // Warm Butter / Cream
          300: '#EDEBC0',
          400: '#DDD99F',
          500: '#C7C27D',
        },
        blush: {
          50: '#FFF8FB',
          100: '#FFE4EF', // Soft Blush Pink
          200: '#FFD1E3',
          300: '#FFBAD3',
        },
        rose: {
          50: '#FFF5F8',
          100: '#FFE4EF',
          200: '#FFCCD9',
          300: '#FBB4CA',
          400: '#F39EB6', // Warm Rose / Coral Pink (Secondary Accent)
          500: '#E27D9A',
          600: '#C55B79',
          700: '#9F3E5A',
          800: '#7B2E45',
          900: '#551F30',
          950: '#2E0F19',
        },
        dark: {
          950: '#F8FAFC', // Canvas background (crisp slate-50)
          900: '#FFFFFF', // Card background (pure white)
          850: '#F1F5F9', // Elevated surface / sub-panel (slate-100)
          800: '#E2E8F0', // Hover / pills (slate-200)
          750: '#E2E8F0', // Subtle card borders
          700: '#CBD5E1', // Input & focus borders (slate-300)
          600: '#94A3B8', // Active border
        },
        slate: {
          50: '#F8FAFC',
          100: '#F1F5F9',
          200: '#E2E8F0',
          300: '#334155', // Slate-700 for high-contrast readable body text
          400: '#475569', // Slate-600 for clear secondary descriptions
          500: '#64748B', // Slate-500 for captions and metadata
          600: '#475569',
          700: '#334155',
          800: '#1E293B',
          900: '#0F172A',
        },
        light: {
          primary: '#0F172A',
          secondary: '#334155',
          pure: '#FFFFFF',
          cream: '#F7F6D3',
          blush: '#FFE4EF',
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '22px',
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
        'card': '0 4px 20px -2px rgba(15, 23, 42, 0.06), 0 2px 6px -1px rgba(15, 23, 42, 0.04)',
        'modal': '0 20px 45px -10px rgba(15, 23, 42, 0.15), 0 10px 20px -5px rgba(15, 23, 42, 0.08)',
        'accent': '0 0 25px -5px rgba(22, 163, 74, 0.25)',
        'rose': '0 0 25px -5px rgba(225, 29, 72, 0.25)',
        'cream': '0 0 25px -5px rgba(247, 246, 211, 0.35)',
        'metallic': '0 2px 8px 0 rgba(15, 23, 42, 0.08)',
      },
    },
  },
  plugins: [],
};
