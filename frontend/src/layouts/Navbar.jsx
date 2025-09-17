import { useState, useEffect, useRef } from "react";
import {
  SunIcon,
  MoonIcon,
  MagnifyingGlassIcon,
  UserCircleIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";
import { Link } from "react-router-dom";
import { queryAI } from "../api/finopsApi";
import { Link } from "react-router-dom";

function Navbar() {
  const [darkMode, setDarkMode] = useState(false);
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);
  const [searchFocused, setSearchFocused] = useState(false);
  const [history, setHistory] = useState([]); // ✅ search history
  const searchInputRef = useRef(null);

  // Load dark mode + history from localStorage
  useEffect(() => {
    const saved = localStorage.getItem("darkMode") === "true";
    setDarkMode(saved);
    document.documentElement.classList.toggle("dark", saved);

    const savedHistory = JSON.parse(localStorage.getItem("searchHistory") || "[]");
    setHistory(savedHistory);
  }, []);

  // Keyboard shortcut (Cmd+K / Ctrl+K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") {
        e.preventDefault();
        searchInputRef.current?.focus();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
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

      // ✅ update history (last 5)
      const newHistory = [query, ...history.filter((q) => q !== query)].slice(0, 5);
      setHistory(newHistory);
      localStorage.setItem("searchHistory", JSON.stringify(newHistory));
    } catch (err) {
      setResult({ error: "Query failed" });
    }
  };

  // Render AI results smartly
  const renderResult = () => {
    if (!result) return null;

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

    return (
      <pre className="whitespace-pre-wrap text-gray-800 dark:text-gray-200 text-sm">
        {JSON.stringify(result, null, 2)}
      </pre>
    );
  };

  return (
    <div
      className={`flex items-center justify-between px-6 py-3 shadow relative transition-colors duration-300 ${
        searchFocused
          ? "bg-white/70 dark:bg-gray-900/70 backdrop-blur-md"
          : "bg-white dark:bg-gray-900"
      }`}
    >
      {/* Left: Navigation + Search */}
      <div className="flex items-center gap-6 w-2/3">
        {/* Navigation Links */}
        <div className="flex items-center gap-4 text-sm font-medium dark:text-white">
          <Link to="/insights" className="hover:underline">📊 Insights</Link>
          <Link to="/forecast" className="hover:underline">📈 Forecasts</Link>
          <Link to="/savings" className="hover:underline">💰 Savings</Link>
          <Link to="/idle" className="hover:underline">🛑 Idle</Link>
          <Link to="/anomalies" className="hover:underline">⚠️ Anomalies</Link>
          <Link to="/drift" className="hover:underline">📉 Drift</Link>
        </div>

        {/* AI Search */}
        <form onSubmit={handleSearch} className="flex items-center flex-1 relative">
          <div className="relative w-full transition-all duration-300 ease-in-out focus-within:w-[140%] focus-within:shadow-lg">
            <MagnifyingGlassIcon className="absolute left-2 top-2 h-5 w-5 text-gray-400" />
            <input
              ref={searchInputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onFocus={() => setSearchFocused(true)}
              onBlur={() => setTimeout(() => setSearchFocused(false), 150)} // delay so clicks work
              placeholder="Ask FinOps AI (⌘K / Ctrl+K to focus)"
              className="w-full pl-8 pr-3 py-1 border rounded text-sm dark:bg-gray-800 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* ✅ Search History Suggestions */}
          {searchFocused && history.length > 0 && (
            <div className="absolute top-10 left-0 w-full bg-white dark:bg-gray-800 shadow-lg rounded p-2 text-sm z-50">
              {history.map((h, idx) => (
                <div
                  key={idx}
                  onClick={() => setQuery(h)}
                  className="px-3 py-1 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {h}
                </div>
              ))}
            </div>
          )}
        </form>
      </div>

      {/* Right: Controls */}
      <div className="flex items-center gap-4">
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
