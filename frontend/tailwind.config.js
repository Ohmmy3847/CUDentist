/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        'cu-pink': '#E5007D',
        'cu-gold': '#FFD700',
        'cu-gray': '#F5F5F5',
        'cu-blue': '#0099CC',
        'cu-dark': '#222',
      },
      fontFamily: {
        'cu': ['Kanit', 'Sarabun', 'Prompt', 'sans-serif'],
      },
      boxShadow: {
        'cu': '0 4px 24px rgba(229,0,125,0.08)',
      },
      borderRadius: {
        'cu': '1.5rem',
      },
    },
  },
  plugins: [],
}
