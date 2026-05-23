/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        warm: {
          50: "#fdf8f0",
          100: "#f9edd9",
          200: "#f3d9b0",
          300: "#ebc07d",
          400: "#e2a34e",
          500: "#d98b2b",
          600: "#c47020",
          700: "#a3561d",
          800: "#83451f",
          900: "#6c3a1d",
        },
        sage: {
          50: "#f4f7f4",
          100: "#e3eae3",
          200: "#c7d5c7",
          300: "#a1b8a1",
          400: "#7a9a7a",
          500: "#5a7d5a",
          600: "#466446",
          700: "#3a5139",
          800: "#31422f",
          900: "#293728",
        },
      },
      fontFamily: {
        serif: ["Georgia", "Cambria", "Times New Roman", "serif"],
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
