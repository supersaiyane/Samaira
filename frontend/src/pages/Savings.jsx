import { useEffect, useState } from "react";
import { getSavingsSummary } from "../api/finopsApi";

function Savings() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    getSavingsSummary().then((res) => setSummary(res.data));
  }, []);

  if (!summary) return <p>Loading...</p>;

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">💰 Savings</h2>
      <p>Total Savings: ${summary.total_savings} {summary.currency}</p>
    </div>
  );
}

export default Savings;
