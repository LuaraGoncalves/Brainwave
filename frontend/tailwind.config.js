/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'brain-dark': '#090907',
        'brain-panel': '#10100d',
        'brain-soft': '#191812',
        'brain-line': 'rgba(202, 163, 92, 0.34)',
        'brain-muted': '#9a927f',
        'brain-ivory': '#fff7e6',
        'brain-gold': '#d4ad67',
        'brain-gold-soft': '#7b6336',
      },
      fontFamily: {
        display: ['Georgia', 'serif'],
        sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      backgroundImage: {
        'gradient-radial': 'radial-gradient(var(--tw-gradient-stops))',
        'gradient-glass': 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%)',
      },
      boxShadow: {
        'gold': '0 0 28px rgba(202, 163, 92, 0.2)',
      }
    },
  },
  plugins: [],
}
