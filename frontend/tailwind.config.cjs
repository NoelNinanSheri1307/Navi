/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      '320': '320px',
      '375': '375px',
      '425': '425px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1440px',
    },
    extend: {
      fontFamily: {
        sans: ['Footlight MT Light', 'serif'],
        serif: ['Footlight MT Light', 'serif'],
        mono: ['Footlight MT Light', 'serif'],
      },
      colors: {
        background: '#09090b',
        surface: '#121215',
        subtle: '#18181b',
        border: 'rgba(255, 255, 255, 0.08)',
        accent: '#10b981',
      },
    },
  },
  plugins: [],
}
