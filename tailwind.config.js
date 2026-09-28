/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./templates/**/*.html', './garden/**/*.py', './src/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        soil: {
          50: '#f7f3ee',
          100: '#ebe0d4',
          200: '#d4bfa8',
          300: '#b89674',
          400: '#9a7350',
          500: '#7d5a3c',
          600: '#5c4033',
          700: '#3d2914',
          800: '#2a1c0e',
          900: '#1a1108',
        },
        leaf: {
          50: '#f0f7ed',
          100: '#dcefd4',
          200: '#bbdfab',
          300: '#8fc87a',
          400: '#6aaf52',
          500: '#4a7c3f',
          600: '#2d5a27',
          700: '#244820',
          800: '#1e3a1b',
          900: '#193117',
        },
        sand: {
          50: '#faf8f4',
          100: '#f3efe6',
          200: '#e8dfd0',
        },
      },
      fontFamily: {
        display: ['Georgia', 'Cambria', 'Times New Roman', 'serif'],
        sans: ['system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
