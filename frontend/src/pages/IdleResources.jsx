import { useEffect, useState } from "react";
import { getIdleResources } from "../api/finopsApi";
import { Bar } from "react-chartjs-2";
import "chart.js/auto";

function IdleResources() {
  const [resources, setResources] = useState([]);
  const [filteredResources, setFilteredResources] = useState([]);
  const [serviceFilter, setServiceFilter] = useState("All");
  const [accountFilter, setAccountFilter] = useState("All");
  const [regionFilter, setRegionFilter] = useState("All");

  // Load data
  useEffect(() => {
    getIdleResources()
      .then((res) => {
        setResources(res.data);
        setFilteredResources(res.data);
      })
      .catch((err) => console.error("Error fetching idle resources:", err));
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...resources];
    if (serviceFilter !== "All") {
      filtered = filtered.filter((r) => r.service_name === serviceFilter);
    }
    if (accountFilter !== "All") {
      filtered = filtered.filter((r) => r.account_name === accountFilter);
    }
    if (regionFilter !== "All") {
      filtered = filtered.filter((r) => r.region === regionFilter);
    }
    setFilteredResources(filtered);
  }, [serviceFilter, accountFilter, regionFilter, resources]);

  // Unique options
  const services = ["All", ...new Set(resources.map((r) => r.service_name || "Unknown"))];
  const accounts = ["All", ...new Set(resources.map((r) => r.account_name || "Unknown"))];
  const regions = ["All", ...new Set(resources.map((r) => r.region || "Unknown"))];

  // Chart data
  const colors = [
    "#f44336",
    "#ff9800",
    "#9c27b0",
    "#2196f3",
    "#4caf50",
    "#00bcd4",
    "#607d8b",
  ];

  const chartData = {
    labels: filteredResources.map((r) => r.resource_name),
    datasets: [
      {
        label: "Idle Cost ($)",
        data: filteredResources.map((r) => r.total_cost),
        backgroundColor: filteredResources.map((_, idx) => colors[idx % colors.length]),
      },
    ],
  };

  // Total Idle Cost
  const totalIdleCost = filteredResources.reduce(
    (sum, r) => sum + (r.total_cost || 0),
    0
  );

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">🛑 Idle Resources</h2>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 mb-6">
        <div>
          <label className="block text-sm font-medium">Filter by Service</label>
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
          <label className="block text-sm font-medium">Filter by Account</label>
          <select
            value={accountFilter}
            onChange={(e) => setAccountFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
          >
            {accounts.map((acct, idx) => (
              <option key={idx} value={acct}>
                {acct}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium">Filter by Region</label>
          <select
            value={regionFilter}
            onChange={(e) => setRegionFilter(e.target.value)}
            className="border rounded px-2 py-1 text-sm dark:bg-gray-800 dark:text-white"
          >
            {regions.map((reg, idx) => (
              <option key={idx} value={reg}>
                {reg}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Summary */}
      <p className="text-lg font-semibold mb-6">
        Total Idle Cost:{" "}
        <span className="text-red-600">${totalIdleCost.toFixed(2)}</span>
      </p>

      {/* Chart */}
      {filteredResources.length > 0 && (
        <div className="mb-8 w-full md:w-2/3">
          <Bar
            data={chartData}
            options={{
              responsive: true,
              plugins: { legend: { display: false } },
              scales: {
                y: {
                  beginAtZero: true,
                  ticks: { callback: (v) => `$${v}` },
                },
              },
            }}
          />
        </div>
      )}

      {/* Table */}
      {filteredResources.length === 0 ? (
        <p>No idle resources found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border text-sm text-left dark:text-gray-200">
            <thead className="bg-gray-100 dark:bg-gray-700">
              <tr>
                <th className="px-3 py-2 border">Resource</th>
                <th className="px-3 py-2 border">Service</th>
                <th className="px-3 py-2 border">Account</th>
                <th className="px-3 py-2 border">Region</th>
                <th className="px-3 py-2 border">Idle Cost ($)</th>
              </tr>
            </thead>
            <tbody>
              {filteredResources.map((r, i) => (
                <tr key={i} className="border-b">
                  <td className="px-3 py-2 border">{r.resource_name}</td>
                  <td className="px-3 py-2 border">{r.service_name || "-"}</td>
                  <td className="px-3 py-2 border">{r.account_name || "-"}</td>
                  <td className="px-3 py-2 border">{r.region || "-"}</td>
                  <td className="px-3 py-2 border text-red-600 font-medium">
                    ${r.total_cost}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default IdleResources;
