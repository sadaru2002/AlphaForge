/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Background Colors
        'bg-main': '#0A0E1A',           // Deep Navy Black
        'bg-card': '#131825',            // Slightly lighter navy
        'bg-elevated': '#1A1F2E',        // Medium dark blue-gray
        'bg-hover': '#1F2433',           // Subtle lighter on hover
        
        // Accent Colors
        'accent-primary': '#7FFF00',     // Electric Lime Green (Chartreuse)
        'accent-success': '#00FF87',     // Spring Green
        'accent-warning': '#FFB800',     // Vibrant Amber
        'accent-danger': '#FF3366',      // Hot Pink Red
        'accent-info': '#00D9FF',        // Cyan Blue
        
        // Text Colors
        'text-primary': '#FFFFFF',       // Pure White
        'text-secondary': '#A0AEC0',     // Cool Gray
        'text-muted': '#718096',         // Darker Gray
        'text-disabled': '#4A5568',      // Very Dark Gray
        
        // Border Colors
        'border-subtle': '#1E293B',      // Dark slate
        'border-elevated': '#334155',    // Medium slate
        'border-active': '#7FFF00',      // Electric Lime
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'monospace'],
      },
      fontSize: {
        'h1': ['36px', { lineHeight: '42px', fontWeight: '700' }],
        'h2': ['28px', { lineHeight: '34px', fontWeight: '700' }],
        'h3': ['22px', { lineHeight: '28px', fontWeight: '600' }],
        'h4': ['18px', { lineHeight: '24px', fontWeight: '600' }],
        'body-lg': ['16px', { lineHeight: '24px' }],
        'body': ['14px', { lineHeight: '21px' }],
        'small': ['12px', { lineHeight: '18px' }],
        'tiny': ['10px', { lineHeight: '14px', fontWeight: '500' }],
      },
      boxShadow: {
        'card': '0 4px 20px rgba(0, 0, 0, 0.3)',
        'card-hover': '0 8px 30px rgba(127, 255, 0, 0.15)',
        'button': '0 4px 12px rgba(127, 255, 0, 0.3)',
        'button-hover': '0 6px 16px rgba(127, 255, 0, 0.4)',
        'focus': '0 0 0 3px rgba(127, 255, 0, 0.1)',
      },
      borderRadius: {
        'card': '16px',
        'button': '8px',
        'input': '6px',
        'badge': '12px',
      },
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      animation: {
        'pulse-green': 'pulse-green 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'shimmer': 'shimmer 1.5s ease-in-out infinite',
      },
      keyframes: {
        'pulse-green': {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        shimmer: {
          '0%': { transform: 'translateX(-100%)' },
          '100%': { transform: 'translateX(100%)' },
        },
      },
    },
  },
  plugins: [],
}

