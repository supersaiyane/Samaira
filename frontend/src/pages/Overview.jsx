import { useEffect, useState } from "react";
import StatCard from "../components/StatCard";
import ChartCard from "../components/ChartCard";
import { getInsightsSummary } from "../api/finopsApi";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from "recharts";

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

  // Map anomaly severity counts for PieChart
  const severityData = summary.by_severity.map((s) => ({
    name: s.severity,
    value: s.count,
  }));

  const COLORS = ["#EF4444", "#F59E0B", "#3B82F6"]; // red, yellow, blue

  return (
    <div className="space-y-6">
      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <StatCard title="Total Cost (MTD)" value={`$${summary.total_cost_mtd.toFixed(2)}`} />
        <StatCard title="Total Savings" value={`$${summary.total_savings.toFixed(2)}`} />
        <StatCard title="Active Anomalies" value={summary.active_anomalies} />
        <StatCard title="Forecasted Spend (30d)" value={`$${summary.forecast_30d.toFixed(2)}`} />
      </div>

      {/* Charts grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Daily Spend Trend */}
        <ChartCard
          title="Daily Spend (Last 30 Days)"
          data={summary.daily_trend}
          dataKey="cost"
        />

        {/* Anomaly Severity Breakdown */}
        <div className="bg-white shadow rounded p-6">
          <h3 className="text-gray-700 mb-4">Anomalies by Severity</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={severityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                outerRadius={90}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {severityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Top 5 Services */}
      <div className="bg-white shadow rounded p-6">
        <h3 className="text-gray-700 mb-4">Top 5 Services (by anomalies)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={topServicesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="service" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3B82F6" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>

  );
}

export default Overview;
