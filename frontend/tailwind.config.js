/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        "bg-global": "var(--color-bg-global)",
        "bg-card": "var(--color-bg-card)",
        "text-primary": "var(--color-text-primary)",
        "border-wireframe": "var(--color-border-wireframe)",
        "ml-win": "var(--color-ml-win)",
        "ml-loss": "var(--color-ml-loss)",
        "ml-draw": "var(--color-ml-draw)",
        "accent-primary": "var(--color-accent-primary)",
        "accent-secondary": "var(--color-accent-secondary)",
      },
      fontFamily: {
        sans: [
          "Inter",
          "ui-sans-serif",
          "system-ui",
          "-apple-system",
          "Segoe UI",
          "Roboto",
          "sans-serif",
        ],
        mono: [
          "IBM Plex Mono",
          "ui-monospace",
          "SFMono-Regular",
          "Menlo",
          "monospace",
        ],
      },
      borderRadius: {
        none: "0px",
        wireframe: "2px",
      },
      boxShadow: {
        none: "none",
      },
    },
  },
  plugins: [],
};
