/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./auto_resume/**/*.html.j2",
    './auto_resume/script/**/*.{vue,js}'
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/container-queries'),
  ],
}

