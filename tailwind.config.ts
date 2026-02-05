import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f4f7ff",
          500: "#3056d3",
          700: "#1a3fa8"
        }
      }
    }
  },
  plugins: []
};

export default config;
