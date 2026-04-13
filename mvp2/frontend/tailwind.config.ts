import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2563eb",
        "primary-dark": "#1d4ed8",
        accent: "#06b6d4",
        "nav-bg": "#1e293b",
        dark: "#0f172a",
        sym: {
          bg: "#f8fafc",
          border: "#e2e8f0",
          text: "#334155",
          "text-light": "#64748b",
        },
      },
      fontFamily: {
        sans: ["'Apple SD Gothic Neo'", "'Noto Sans KR'", "sans-serif"],
      },
    },
  },
  plugins: [],
};

export default config;
