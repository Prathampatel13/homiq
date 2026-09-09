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
          50: '#F5F9EE',
          100: '#EAF4DC',
          200: '#D8EBB8',
          300: '#C6E294',
          400: '#B8DB80', // Soft Matcha / Sage Green (Primary Accent)
          500: '#9FC964',
          600: '#83AA48',
          700: '#658636',
          800: '#4D6729',
          900: '#374B1D',
          950: '#1D280E',
        },
        brand: {
          50: '#F5F9EE',
          100: '#EAF4DC',
          200: '#D8EBB8',
          300: '#C6E294',
          400: '#B8DB80',
          500: '#9FC964',
          600: '#83AA48',
          700: '#658636',
          800: '#4D6729',
          900: '#374B1D',
          950: '#1D280E',
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
          950: '#0B0D11', // Refined deep slate charcoal
          900: '#12151B',
          850: '#181C24', 
          800: '#202530', 
          750: '#2A303E', 
          700: '#373F50', 
          600: '#4B5569',
        },
        light: {
          primary: '#F8F9FA',
          secondary: '#E5E7EB',
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
        'subtle': '0 1px 3px 0 rgba(0, 0, 0, 0.25)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.35)',
        'modal': '0 20px 45px -10px rgba(0, 0, 0, 0.65)',
        'accent': '0 0 25px -5px rgba(184, 219, 128, 0.35)',
        'rose': '0 0 25px -5px rgba(243, 158, 182, 0.35)',
        'cream': '0 0 25px -5px rgba(247, 246, 211, 0.35)',
        'metallic': '0 0 20px -5px rgba(232, 233, 231, 0.1)',
      },
    },
  },
  plugins: [],
};
