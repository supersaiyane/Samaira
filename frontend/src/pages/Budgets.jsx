import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

function Budgets() {
  const [budgets, setBudgets] = useState([]);

  useEffect(() => {
    axiosClient.get("/budgets").then((res) => setBudgets(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">📊 Budgets</h2>
      {budgets.length === 0 ? (
        <p>No budgets defined.</p>
      ) : (
        <ul className="list-disc ml-6">
          {budgets.map((b) => (
            <li key={b.budget_id}>
              {b.budget_name}: ${b.budget_limit} ({b.period})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Budgets;
