/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        bolt: {
          light: '#fbbf24', // Amber 400
          DEFAULT: '#f59e0b', // Amber 500
          dark: '#b45309', // Amber 700
        },
        palette: {
          primary: '#6366f1', // Indigo 500
          secondary: '#ec4899', // Pink 500
          accent: '#10b981', // Emerald 500
          dark: '#1f2937', // Gray 800
          light: '#f9fafb', // Gray 50
        }
      },
      animation: {
        'pulse-fast': 'pulse 1s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
