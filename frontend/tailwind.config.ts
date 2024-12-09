const { fontFamily } = require("tailwindcss/defaultTheme")

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["app/**/*.{ts,tsx}", "components/**/*.{ts,tsx}", "libs/**/*.{ts,tsx}"],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      fontSize: {
        xxs: "0.58rem",
        xxxs: "0.54rem",
      },
      borderWidth: {
        1: "1px",
      },
      height: {
        "1/6": "13%",
        "5/6": "87%",
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        "color-1": "#2CE2B0",
        "color-2": "#4F5B7B",
        "color-3": "#26314C",
        "color-4": "#A7ADBD",
        "color-5": "#374056",

        // Vessel colors
        "vessel-color-0": "rgb(255, 90, 129)",
        "vessel-color-1": "rgb(224, 181, 30)",
        "vessel-color-2": "rgb(174, 255, 0)",
        "vessel-color-3": "rgb(125, 255, 188)",
        "vessel-color-4": "rgb(80, 144, 255)",
        "vessel-color-5": "rgb(208, 30, 224)",
        "vessel-color-6": "rgb(255, 125, 83)",
        "vessel-color-7": "rgb(255, 185, 114)",
        "vessel-color-8": "rgb(97, 255, 49)",
        "vessel-color-9": "rgb(0, 224, 172)",
        "vessel-color-10": "rgb(49, 204, 255)",
        "vessel-color-11": "rgb(146, 127, 255)",

        // Progress Colors
        "progress-color-1": "#6E83B7",
      },
      borderRadius: {
        lg: `var(--radius)`,
        md: `calc(var(--radius) - 2px)`,
        sm: "calc(var(--radius) - 4px)",
      },
      fontFamily: {
        sans: ["var(--font-sans)", ...fontFamily.sans],
        unito: ["Nunito Sans", "sans-serif"],
      },
      keyframes: {
        "accordion-down": {
          from: { height: 0 },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: 0 },
        },
        "grow-shrink": {
          "0%": {
            scale: "1",
          },
          "50%": {
            scale: "1.2",
          },
          "100%": {
            scale: "1",
          },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        "grow-shrink": "grow-shrink 0.3s ease-in-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
