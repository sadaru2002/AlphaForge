/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'bg-main': '#0f1117',
        'bg-card': '#16181f',
        'bg-elevated': '#1e2029',
        'bg-hover': '#262933',
        'text-primary': '#e4e7eb',
        'text-secondary': '#9ca3af',
        'text-muted': '#6b7280',
        'border-subtle': '#2a2e3e',
        'accent-primary': '#10b981',
        'accent-danger': '#ef4444',
      },
      fontSize: {
        'tiny': ['0.75rem', { lineHeight: '1rem' }],
        'small': ['0.875rem', { lineHeight: '1.25rem' }],
        'body': ['1rem', { lineHeight: '1.5rem' }],
        'h4': ['1.125rem', { lineHeight: '1.75rem' }],
        'h3': ['1.25rem', { lineHeight: '1.75rem' }],
        'h2': ['1.5rem', { lineHeight: '2rem' }],
        'h1': ['2rem', { lineHeight: '2.5rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '70': '17.5rem',
      },
    },
  },
  plugins: [],
}
