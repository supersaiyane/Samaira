import { useEffect, useState } from "react";
import { getAnomalies } from "../api/finopsApi";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [serviceFilter, setServiceFilter] = useState("All");
  const [severityFilter, setSeverityFilter] = useState("All");
  const [timeWindow, setTimeWindow] = useState("All");

  // Load anomalies
  useEffect(() => {
    getAnomalies()
      .then((res) => {
        setAnomalies(res.data);
        setFiltered(res.data);
      })
      .catch((err) => console.error("Error fetching anomalies:", err));
  }, []);

  // Apply filters
  useEffect(() => {
    let data = [...anomalies];

    if (serviceFilter !== "All") {
      data = data.filter((a) => a.service_name === serviceFilter);
    }
    if (severityFilter !== "All") {
      data = data.filter((a) => a.severity === severityFilter);
    }
    if (timeWindow !== "All") {
      const now = new Date();
      const cutoff =
        timeWindow === "7d"
          ? new Date(now.setDate(now.getDate() - 7))
          : new Date(now.setMonth(now.getMonth() - 1));
      data = data.filter((a) => new Date(a.detected_at) >= cutoff);
    }

    setFiltered(data);
  }, [serviceFilter, severityFilter, timeWindow, anomalies]);

  // Dropdown options
  const services = ["All", ...new Set(anomalies.map((a) => a.service_name || "Unknown"))];
  const severities = ["All", "Low", "Medium", "High", "Critical"];
  const windows = [
    { value: "All", label: "All Time" },
    { value: "7d", label: "Last 7 Days" },
    { value: "30d", label: "Last 30 Days" },
  ];

  // Chart Data
  const chartData = {
    labels: filtered.map((a) => a.detected_at),
    datasets: [
      {
        label: "Deviation %",
        data: filtered.map((a) => a.deviation_percent),
        borderColor: "#ff9800",
        tension: 0.3,
      },
    ],
  };

  // Summary
  const total = filtered.length;
  const criticalCount = filtered.filter((a) => a.severity === "Critical").length;

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">⚠️ Anomalies</h2>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium">Service</label>
          <select
            value={serviceFilter}
            onChange={(e) => setServiceFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
          >
            {services.map((svc, idx) => (
              <option key={idx} value={svc}>
                {svc}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">Severity</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
          >
            {severities.map((sev, idx) => (
              <option key={idx} value={sev}>
                {sev}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">Time Window</label>
          <select
            value={timeWindow}
            onChange={(e) => setTimeWindow(e.target.value)}
            className="border rounded px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
          >
            {windows.map((w) => (
              <option key={w.value} value={w.value}>
                {w.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary */}
      <p className="mb-4 text-lg font-semibold">
        Total: {total} | Critical:{" "}
        <span className="text-red-600">{criticalCount}</span>
      </p>

      {/* Chart */}
      {filtered.length > 0 && (
        <div className="mb-8">
          <Line
            data={chartData}
            options={{
              responsive: true,
              plugins: { legend: { display: true } },
              scales: { y: { beginAtZero: true } },
            }}
          />
        </div>
      )}

      {/* Table */}
      {filtered.length === 0 ? (
        <p>No anomalies detected.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border text-sm text-left dark:text-gray-200">
            <thead className="bg-gray-100 dark:bg-gray-700">
              <tr>
                <th className="px-3 py-2 border">Service</th>
                <th className="px-3 py-2 border">Severity</th>
                <th className="px-3 py-2 border">Deviation %</th>
                <th className="px-3 py-2 border">Detected At</th>
                <th className="px-3 py-2 border">Description</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((a) => (
                <tr key={a.anomaly_id} className="border-b">
                  <td className="px-3 py-2 border">{a.service_name || "-"}</td>
                  <td className="px-3 py-2 border">{a.severity || "N/A"}</td>
                  <td className="px-3 py-2 border">{a.deviation_percent}%</td>
                  <td className="px-3 py-2 border">{a.detected_at}</td>
                  <td className="px-3 py-2 border">{a.description || "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Anomalies;
