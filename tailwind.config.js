/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        friends: {
          sofa: '#5D4037',
          coffee: '#8D6E63',
          cream: '#FFF8E1',
          perk: '#2E7D32',
          accent: '#FFB74D',
          paper: '#FFF3E0',
        }
      },
      fontFamily: {
        hand: ['"Caveat"', 'cursive'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'card': '0 10px 30px -10px rgba(93, 64, 55, 0.25)',
      }
    },
  },
  plugins: [],
}
