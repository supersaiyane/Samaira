import { useState } from "react";
import { queryAI } from "../api/finopsApi";

function AIInsights() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await queryAI(query);
    setResult(res.data);
  };

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">🤖 AI Assistant</h2>
      <form onSubmit={handleSubmit} className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask FinOps AI (e.g., Top 5 costly services last 60 days)"
          className="border p-2 flex-1 rounded"
        />
        <button type="submit" className="bg-blue-600 text-white px-4 rounded">
          Ask
        </button>
      </form>
      {result && (
        <pre className="bg-gray-100 p-4 rounded text-sm overflow-x-auto">
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default AIInsights;
