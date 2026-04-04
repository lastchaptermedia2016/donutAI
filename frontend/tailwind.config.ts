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
        // Billionaire Warm Gold Palette with Deep Blue Accents
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
          // Deep Blue Accents
          deep: {
            blue: "#0A1628",
            navy: "#0D1B3E",
            ocean: "#1A2744",
            sapphire: "#1E3A5F",
          },
        },
        // Sophisticated Dark Theme Palette
        sophisticated: {
          midnight: "#1C2333", // 220 24% 15%
          slate: "#272D3D", // 220 16% 20%
          platinum: "#EDEDF5", // 220 16% 95%
          champagne: "#F5F5F9", // 220 20% 98%
          burgundy: "#4A3636", // 0 30% 30% - lighter for visibility
          emerald: "#3D4A3D", // 120 25% 25% - lighter for visibility
          gold: "#D4AF37", // 50 80% 60%
          silver: "#CCCCCC", // 0 0% 80%
          taupe: "#D9D9E6", // 220 12% 85% - light text
          charcoal: "#40404D", // 220 12% 30% - lighter for visibility
          ivory: "#F5F0E8", // 50 20% 95% - bright text
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
        "blue-glow": "0 0 20px rgba(30, 58, 95, 0.4)",
        "holographic": "0 0 30px rgba(201, 169, 110, 0.2), 0 0 60px rgba(30, 58, 95, 0.15), 0 0 90px rgba(224, 194, 108, 0.1)",
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
        "shimmer": "shimmer 2s linear infinite",
        "gradient-shift": "gradientShift 15s ease infinite",
        "holographic-shimmer": "holographicShimmer 3s ease-in-out infinite",
        "particle-float": "particleFloat 20s linear infinite",
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
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        gradientShift: {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        holographicShimmer: {
          "0%, 100%": { 
            backgroundPosition: "0% 0%",
            opacity: "0.6"
          },
          "25%": { 
            backgroundPosition: "100% 0%",
            opacity: "0.8"
          },
          "50%": { 
            backgroundPosition: "100% 100%",
            opacity: "1"
          },
          "75%": { 
            backgroundPosition: "0% 100%",
            opacity: "0.8"
          },
        },
        particleFloat: {
          "0%": { transform: "translateY(0) translateX(0)", opacity: "0" },
          "10%": { opacity: "0.6" },
          "90%": { opacity: "0.6" },
          "100%": { transform: "translateY(-100vh) translateX(50px)", opacity: "0" },
        },
      },
    },
  },
  plugins: [],
};

export default config;
