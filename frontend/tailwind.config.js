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
          50: '#F4F7F6',
          100: '#E5EBE9',
          200: '#CAD7D3',
          300: '#AEC3BC',
          400: '#8FA8A0', // Official HomiQ Sage Accent
          500: '#759088',
          600: '#5C746D',
          700: '#465954',
          800: '#32403C',
          900: '#202A27',
          950: '#101715',
        },
        brand: {
          50: '#F4F7F6',
          100: '#E5EBE9',
          200: '#CAD7D3',
          300: '#AEC3BC',
          400: '#8FA8A0', // Muted sage accent
          500: '#8FA8A0', // Primary accent
          600: '#7B948D',
          700: '#647A73',
          800: '#4E5F5A',
          900: '#36433F',
          950: '#1F2825',
        },
        dark: {
          950: '#08090B', // Primary root canvas
          900: '#0D0F12', // Panel / card surface
          850: '#12151A', // Elevated surface
          800: '#181C22', // Interactive / input surface
          750: '#22272F', // Active / border
          700: '#2A303A', // Static border
          600: '#3D4653',
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
