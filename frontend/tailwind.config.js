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
          50: '#FDF3F1',
          100: '#FCE5DE',
          200: '#F7C6B8',
          300: '#F2A18C',
          400: '#E7603B', 
          500: '#D9381E', // The Ekvator orange
          600: '#C02C15',
          700: '#A0220F',
          800: '#831F10',
          900: '#6D1E11',
          950: '#3B0C06',
        },
        brand: {
          50: '#FDF3F1',
          100: '#FCE5DE',
          200: '#F7C6B8',
          300: '#F2A18C',
          400: '#E7603B', 
          500: '#D9381E',
          600: '#C02C15',
          700: '#A0220F',
          800: '#831F10',
          900: '#6D1E11',
          950: '#3B0C06',
        },
        dark: {
          950: '#111111', // Very dark charcoal
          900: '#1A1A1A', // Slightly lighter charcoal
          850: '#222222', 
          800: '#2A2A2A', 
          750: '#333333', 
          700: '#404040', 
          600: '#555555',
        },
        light: {
          primary: '#F5F5F2',
          secondary: '#E8E9E7',
          pure: '#FFFFFF',
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
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.4)',
        'card': '0 4px 24px -2px rgba(0, 0, 0, 0.5)',
        'modal': '0 24px 48px -12px rgba(0, 0, 0, 0.8)',
        'accent': '0 0 20px -5px rgba(143, 168, 160, 0.25)',
        'metallic': '0 0 25px -5px rgba(232, 233, 231, 0.15)',
      },
    },
  },
  plugins: [],
};
