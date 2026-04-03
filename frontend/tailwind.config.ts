import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Billionaire Warm Gold Palette
        billionaire: {
          black: "#0A0A0A",
          charcoal: "#121212",
          slate: "#1A1A1A",
          titanium: "#2D2D2D",
          platinum: "#D1D1D1",
          silver: "#E5E4E2",
          gold: {
            50: "#FDF6E3",
            100: "#F7E9C1",
            200: "#EFD89C",
            300: "#E5C777",
            400: "#DAB65B",
            500: "#C9A96E", // Primary gold
            600: "#B89857",
            700: "#A68743",
            800: "#947632",
            900: "#826524",
          },
          burgundy: "#722F37",
          amber: "#C89B3C",
          bronze: "#A67C52",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        display: ["Playfair Display", "serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      boxShadow: {
        "billionaire-sm": "0 1px 2px rgba(201, 169, 110, 0.05)",
        "billionaire": "0 4px 12px rgba(201, 169, 110, 0.1)",
        "billionaire-lg": "0 8px 24px rgba(201, 169, 110, 0.15)",
        "billionaire-xl": "0 16px 48px rgba(201, 169, 110, 0.2)",
        "gold-glow": "0 0 20px rgba(201, 169, 110, 0.3)",
      },
      backdropBlur: {
        xs: "2px",
        "4xl": "40px",
      },
      animation: {
        "pulse-slow": "pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        "fade-in": "fadeIn 0.5s ease-in-out",
        "slide-up": "slideUp 0.4s ease-out",
        "scale-in": "scaleIn 0.3s ease-out",
        "float": "float 6s ease-in-out infinite",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        slideUp: {
          "0%": { transform: "translateY(20px)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        scaleIn: {
          "0%": { transform: "scale(0.9)", opacity: "0" },
          "100%": { transform: "scale(1)", opacity: "1" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-10px)" },
        },
      },
    },
  },
  plugins: [],
};

export default config;