import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { getInsightsSummary } from "../api/finopsApi";

function Overview() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getInsightsSummary()
      .then((res) => setSummary(res.data))
      .catch((err) => console.error("Failed to load summary:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p>Loading...</p>;
  if (!summary) return <p>Error loading data.</p>;

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total Cost (MTD)" value={`$${summary.total_cost_mtd.toFixed(2)}`} />
        <StatCard title="Total Savings" value={`$${summary.total_savings.toFixed(2)}`} />
        <StatCard title="Active Anomalies" value={summary.active_anomalies} />
        <StatCard title="Forecasted Spend (30d)" value={`$${summary.forecast_30d.toFixed(2)}`} />
      </div>

      {/* Trend chart */}
      <ChartCard
        title="Daily Spend (Last 30 Days)"
        data={summary.daily_trend}
        dataKey="cost"
      />
    </div>
  );
}

export default Overview;
