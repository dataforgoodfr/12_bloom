const { fontFamily } = require("tailwindcss/defaultTheme")

/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: ["app/**/*.{ts,tsx}", "components/**/*.{ts,tsx}"],
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
        "vessel-color-1": "#FF5A81",
        "vessel-color-2": "#E0B51E",
        "vessel-color-3": "#AEFF00",
        "vessel-color-4": "#7DFFBC",
        "vessel-color-5": "#5090FF",
        "vessel-color-6": "#D01EE0",
        "vessel-color-7": "#FF7D53",
        "vessel-color-8": "#FFB972",
        "vessel-color-9": "#61FF31",
        "vessel-color-10": "#00E0AC",
        "vessel-color-11": "#31CCFF",
        "vessel-color-12": "#927FFF",

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
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
