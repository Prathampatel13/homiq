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
        brand: {
          50: '#F5F9FF',
          100: '#EBF3FE',
          200: '#CEE2FD',
          300: '#A1CBFC',
          400: '#68ACFA',
          500: '#0071E3', // Apple/Linear refined royal electric accent
          600: '#0062C4',
          700: '#0050A3',
          800: '#003F82',
          900: '#002B59',
          950: '#001937',
        },
        dark: {
          950: '#08090C', // Root deep canvas
          900: '#0D0F14', // Primary card/surface
          850: '#12151D', // Elevated surface
          800: '#181C26', // Interactive element
          750: '#222836', // Hover border / active
          700: '#2B3244', // Static subtle border
        }
      },
      fontFamily: {
        sans: ['Inter', 'Plus Jakarta Sans', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      borderRadius: {
        'xl': '12px',
        '2xl': '16px',
        '3xl': '22px',
      },
      boxShadow: {
        'subtle': '0 1px 2px 0 rgba(0, 0, 0, 0.25)',
        'card': '0 4px 20px -2px rgba(0, 0, 0, 0.4)',
        'modal': '0 20px 40px -15px rgba(0, 0, 0, 0.7)',
        'accent': '0 0 15px -3px rgba(0, 113, 227, 0.25)',
      },
    },
  },
  plugins: [],
};
