/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    screens: {
      'xs': '320px',
      'sm': '375px',
      'msm': '425px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1440px',
    },
    extend: {
      fontFamily: {
        sans: ['Footlight MT Light', 'serif'],
        mono: ['Footlight MT Light', 'serif'],
        serif: ['Footlight MT Light', 'serif'],
      },
      colors: {
        background: '#050506',
        card: '#0a0a0b',
        ga: '#10b981',
        pso: '#3b82f6',
        gwo: '#94a3b8',
        de: '#8b5cf6',
        aco: '#f59e0b',
        sa: '#f43f5e',
        hybrid: '#22d3ee',
      },
    },
  },
  plugins: [],
}
