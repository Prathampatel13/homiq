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
          50: '#f0f7ff',
          100: '#e0effe',
          200: '#bae0fd',
          300: '#7cc5fd',
          400: '#36a6f9',
          500: '#0c87e8',
          600: '#006bc6',
          700: '#0256a3',
          800: '#064986',
          900: '#0b3d6f',
          950: '#072749',
        },
        dark: {
          bg: '#0b0f17',
          card: '#111827',
          border: '#1f2937',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
      boxShadow: {
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
        'glow': '0 0 20px rgba(59, 130, 246, 0.4)',
      },
    },
  },
  plugins: [],
};
