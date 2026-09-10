import React from \"react\";
import { useTheme } from \"./ThemeContext\";

export const ThemeToggleButton = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <button 
      onClick={toggleTheme} 
      className=\"theme-toggle-btn\"
      aria-label={`Switch to ${theme === \"dark\" ? \"light\" : \"dark\"} mode`}
    >
      {theme === \"dark\" ? \"☀️ Light Mode\" : \"🌙 Dark Mode\"}
    </button>
  );
};
