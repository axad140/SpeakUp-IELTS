/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        gold: "#f0a500",
        dark: "#0f0c29",
        surface: "#1a1a2e",
        card: "#16213e",
        accent: "#0f3460",
        success: "#00b894",
        danger: "#e17055",
        info: "#74b9ff",
        muted: "#8892a4",
      },
      animation: {
        'pulse-slow': 'pulse 3s ease-in-out infinite',
        'float': 'float 3s ease-in-out infinite',
        'wave': 'wave 1.2s ease-in-out infinite',
        'glow': 'glow 2s ease-in-out infinite alternate',
        'slide-up': 'slideUp 0.4s ease-out',
        'fade-in': 'fadeIn 0.3s ease-out',
      },
      keyframes: {
        float: { '0%,100%': {transform:'translateY(0)'}, '50%': {transform:'translateY(-8px)'} },
        wave: { '0%,100%': {height:'6px'}, '50%': {height:'22px'} },
        glow: { from:{boxShadow:'0 0 5px #f0a500'}, to:{boxShadow:'0 0 20px #f0a500,0 0 40px #f0a50055'} },
        slideUp: { from:{opacity:0,transform:'translateY(16px)'}, to:{opacity:1,transform:'translateY(0)'} },
        fadeIn: { from:{opacity:0}, to:{opacity:1} },
      }
    }
  },
  plugins: []
}
