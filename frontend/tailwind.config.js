/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: "class",
  theme: { 
    extend: { 
      colors: { "on-primary-fixed-variant": "#314863", "secondary-container": "#cce2fc", "primary-fixed": "#d1e4ff", "on-secondary-container": "#50657b", "on-background": "#191c1e", "on-primary-container": "#7a92b0", "on-secondary-fixed-variant": "#34495d", "tertiary": "#001626", "on-primary": "#ffffff", "surface-tint": "#49607c", "outline": "#74777e", "tertiary-fixed": "#cce5ff", "on-error": "#ffffff", "primary-fixed-dim": "#b0c9e8", "secondary-fixed": "#cfe5ff", "surface-container-low": "#f2f4f6", "on-tertiary": "#ffffff", "outline-variant": "#c3c6ce", "surface-container-highest": "#e0e3e5", "on-tertiary-fixed": "#001d31", "secondary-fixed-dim": "#b3c9e2", "error": "#ba1a1a", "inverse-surface": "#2d3133", "surface-container-high": "#e6e8ea", "background": "#f7f9fb", "surface-dim": "#d8dadc", "on-tertiary-container": "#2f96db", "on-surface-variant": "#43474d", "secondary": "#4b6076", "primary-container": "#102a43", "surface-container-lowest": "#ffffff", "on-secondary": "#ffffff", "on-secondary-fixed": "#051d30", "on-tertiary-fixed-variant": "#004b73", "on-surface": "#191c1e", "tertiary-container": "#002b45", "primary": "#00152a", "on-error-container": "#93000a", "error-container": "#ffdad6", "surface-variant": "#e0e3e5", "surface-bright": "#f7f9fb", "tertiary-fixed-dim": "#93ccff", "surface-container": "#eceef0", "surface": "#f7f9fb", "inverse-on-surface": "#eff1f3", "on-primary-fixed": "#011d35", "inverse-primary": "#b0c9e8" }, 
      borderRadius: { "DEFAULT": "0.125rem", "lg": "0.25rem", "xl": "0.5rem", "full": "0.75rem" }, 
      spacing: { "space-xl": "1.5rem", "space-sm": "0.5rem", "space-lg": "1rem", "gutter": "0.75rem", "space-xs": "0.25rem", "space-md": "0.75rem", "margin": "1rem" }, 
      fontFamily: { "headline-sm": ["Inter"], "headline-xl": ["Inter"], "body-md": ["Inter"], "label-caps": ["Inter"], "body-lg": ["Inter"], "body-sm": ["Inter"], "telemetry-lg": ["JetBrains Mono"], "telemetry-xs": ["JetBrains Mono"], "headline-md": ["Inter"], "telemetry-sm": ["JetBrains Mono"], "headline-lg": ["Inter"], "telemetry-md": ["JetBrains Mono"] }, 
      fontSize: { "headline-sm": ["1rem", { lineHeight: "1.5rem", letterSpacing: "0", fontWeight: "600" }], "headline-xl": ["2rem", { lineHeight: "2.5rem", letterSpacing: "-0.02em", fontWeight: "600" }], "body-md": ["0.875rem", { lineHeight: "1.375rem", letterSpacing: "0", fontWeight: "400" }], "label-caps": ["0.6875rem", { lineHeight: "0.875rem", letterSpacing: "0.08em", fontWeight: "600" }], "body-lg": ["1rem", { lineHeight: "1.5rem", letterSpacing: "0", fontWeight: "400" }], "body-sm": ["0.75rem", { lineHeight: "1.125rem", letterSpacing: "0.01em", fontWeight: "400" }], "telemetry-lg": ["1.5rem", { lineHeight: "1.75rem", letterSpacing: "-0.025em", fontWeight: "600" }], "telemetry-xs": ["0.6875rem", { lineHeight: "0.875rem", letterSpacing: "0.02em", fontWeight: "400" }], "headline-md": ["1.25rem", { lineHeight: "1.75rem", letterSpacing: "-0.01em", fontWeight: "600" }], "telemetry-sm": ["0.8125rem", { lineHeight: "1rem", letterSpacing: "0", fontWeight: "500" }], "headline-lg": ["1.5rem", { lineHeight: "2rem", letterSpacing: "-0.015em", fontWeight: "600" }], "telemetry-md": ["1rem", { lineHeight: "1.25rem", letterSpacing: "-0.01em", fontWeight: "500" }] } 
    } 
  },
  plugins: [],
}
