import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: "#3B82F6",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        savings: "#047857",
        landing: {
          deep: "#09090B",
          elevated: "#18181B",
          subtle: "#27272A",
          cyan: "#22D3EE",
          violet: "#A78BFA",
          emerald: "#34D399",
        },
      },
      fontFamily: {
        sans: ["Instrument Sans", "Inter", "sans-serif"],
        mono: ["JetBrains Mono", "monospace"],
      },
      fontSize: {
        "display": ["clamp(3rem, 8vw, 7rem)", { lineHeight: "1.05", letterSpacing: "-0.02em" }],
        "display-sm": ["clamp(2rem, 5vw, 4rem)", { lineHeight: "1.1", letterSpacing: "-0.02em" }],
      },
      keyframes: {
        "mesh-move": {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "25%": { transform: "translate(10px, -10px) scale(1.02)" },
          "50%": { transform: "translate(-5px, 15px) scale(0.98)" },
          "75%": { transform: "translate(-15px, -5px) scale(1.01)" },
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.4" },
          "50%": { opacity: "0.8" },
        },
        "fade-in-up": {
          "0%": { opacity: "0", transform: "translateY(20px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        "scale-in-center": {
          "0%": { opacity: "0", transform: "scale(0.9)" },
          "100%": { opacity: "1", transform: "scale(1)" },
        },
        "counter-roll": {
          "0%": { transform: "translateY(100%)", opacity: "0" },
          "100%": { transform: "translateY(0)", opacity: "1" },
        },
        "line-draw": {
          "0%": { strokeDashoffset: "100%" },
          "100%": { strokeDashoffset: "0%" },
        },
        "blur-in": {
          "0%": { filter: "blur(10px)", opacity: "0" },
          "100%": { filter: "blur(0)", opacity: "1" },
        },
      },
      animation: {
        "mesh-move": "mesh-move 20s ease-in-out infinite",
        "glow-pulse": "glow-pulse 3s ease-in-out infinite",
        "fade-in-up": "fade-in-up 0.6s ease-out forwards",
        "scale-in-center": "scale-in-center 0.5s ease-out forwards",
        "counter-roll": "counter-roll 0.8s ease-out forwards",
        "line-draw": "line-draw 1s ease-out forwards",
        "blur-in": "blur-in 0.5s ease-out forwards",
      },
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "mesh-gradient": "radial-gradient(at 40% 20%, hsla(180, 80%, 50%, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, hsla(260, 80%, 60%, 0.15) 0px, transparent 50%), radial-gradient(at 0% 50%, hsla(180, 80%, 50%, 0.1) 0px, transparent 50%), radial-gradient(at 80% 50%, hsla(260, 80%, 60%, 0.1) 0px, transparent 50%), radial-gradient(at 0% 100%, hsla(180, 80%, 50%, 0.15) 0px, transparent 50%), radial-gradient(at 80% 100%, hsla(260, 80%, 60%, 0.15) 0px, transparent 50%)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
