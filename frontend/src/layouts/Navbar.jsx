import { useState, useEffect } from "react";
import { SunIcon, MoonIcon, MagnifyingGlassIcon, UserCircleIcon } from "@heroicons/react/24/outline";

function Navbar() {
  const [darkMode, setDarkMode] = useState(false);

  // Load from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("darkMode") === "true";
    setDarkMode(saved);
    document.documentElement.classList.toggle("dark", saved);
  }, []);

  // Toggle handler
  const toggleDarkMode = () => {
    const newValue = !darkMode;
    setDarkMode(newValue);
    localStorage.setItem("darkMode", newValue);
    document.documentElement.classList.toggle("dark", newValue);
  };

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-900 shadow">
      {/* Left: Search */}
      <div className="flex items-center w-1/3">
        <div className="relative w-full">
          <MagnifyingGlassIcon className="absolute left-2 top-2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Search (services, accounts, AI queries...)"
            className="w-full pl-8 pr-3 py-1 border rounded text-sm dark:bg-gray-800 dark:text-white"
          />
        </div>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-4">
        {/* Dark mode toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-2 rounded hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          {darkMode ? (
            <SunIcon className="h-5 w-5 text-yellow-400" />
          ) : (
            <MoonIcon className="h-5 w-5 text-gray-600 dark:text-gray-300" />
          )}
        </button>

        {/* User menu */}
        <div className="flex items-center gap-2 cursor-pointer hover:opacity-80">
          <UserCircleIcon className="h-7 w-7 text-gray-600 dark:text-gray-300" />
          <span className="text-sm font-medium dark:text-white">Gurpreet</span>
        </div>
      </div>
    </div>
  );
}

export default Navbar;
