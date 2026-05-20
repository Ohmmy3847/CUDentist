/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './lib/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#E5007D',
        'primary-dark': '#B8005E',
        'primary-light': '#FF66B2',
        'primary-bg': '#FFF0F7',
      },
      fontFamily: {
        sans: ['Kanit', 'Sarabun', 'Prompt', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
