/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: '#09090b',
        foreground: '#fafafa',
        primary: {
          DEFAULT: '#ffffff',
          foreground: '#000000',
        },
        card: {
          DEFAULT: '#18181b',
          foreground: '#fafafa',
        },
        border: '#27272a',
        muted: '#52525b',
        accent: '#2563eb'
      }
    },
  },
  plugins: [],
}
