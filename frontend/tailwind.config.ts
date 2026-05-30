import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17202a",
        canvas: "#f7f8f5",
        mint: "#72d6b1",
        coral: "#f26d5b",
        berry: "#8b3f63",
        steel: "#566b7b"
      },
      boxShadow: {
        soft: "0 12px 30px rgba(23, 32, 42, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;
