import { useState, useEffect } from "react";
import {
  SunIcon,
  MoonIcon,
  MagnifyingGlassIcon,
  UserCircleIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { queryAI } from "../api/finopsApi";

function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

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

  // Submit AI query
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    try {
      const res = await queryAI(query);
      setResult(res.data);
    } catch (err) {
      setResult({ error: "Query failed" });
    }
  };

  // Render AI results smartly
  const renderResult = () => {
    if (!result) return null;

    // If response has rows & columns → render table
    if (result.columns && result.rows) {
      return (
        <table className="min-w-full border text-sm text-left dark:text-gray-200">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              {result.columns.map((col, idx) => (
                <th key={idx} className="px-3 py-2 border">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {result.rows.map((row, rIdx) => (
              <tr key={rIdx} className="border-b">
                {row.map((cell, cIdx) => (
                  <td key={cIdx} className="px-3 py-2 border">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      );
    }

    // Fallback → pretty JSON
    return (
      <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 text-sm">
        {JSON.stringify(result, null, 2)}
      </pre>
    );
  };

  return (
    <div className="flex items-center justify-between px-6 py-3 bg-white dark:bg-gray-900 shadow relative">
      {/* Left: Search */}
      <form onSubmit={handleSearch} className="flex items-center w-1/3">
        <div className="relative w-full">
          <MagnifyingGlassIcon className="absolute left-2 top-2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask FinOps AI (e.g., Top 5 costly services last 60 days)"
            className="w-full pl-8 pr-3 py-1 border rounded text-sm dark:bg-gray-800 dark:text-white"
          />
        </div>
      </form>

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

      {/* AI Search Result Dropdown */}
      {result && (
        <div className="absolute top-14 left-6 w-1/2 bg-white dark:bg-gray-800 shadow-lg rounded p-4 max-h-80 overflow-y-auto z-50">
          {/* Close Button */}
          <button
            onClick={() => setResult(null)}
            className="absolute top-2 right-2 text-gray-500 hover:text-gray-800 dark:hover:text-gray-200"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
          {renderResult()}
        </div>
      )}
    </div>
  );
}

export default Navbar;
