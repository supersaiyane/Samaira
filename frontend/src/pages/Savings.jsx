import { useEffect, useState } from "react";
import { getSavings } from "../api/finopsApi";
import { Pie } from "react-chartjs-2";
import "chart.js/auto";

function Savings() {
  const [savings, setSavings] = useState([]);
  const [filteredSavings, setFilteredSavings] = useState([]);
  const [serviceFilter, setServiceFilter] = useState("All");
  const [accountFilter, setAccountFilter] = useState("All");

  // Load savings
  useEffect(() => {
    getSavings()
      .then((res) => {
        setSavings(res.data);
        setFilteredSavings(res.data);
      })
      .catch((err) => console.error("Error fetching savings:", err));
  }, []);

  // Apply filters
  useEffect(() => {
    let filtered = [...savings];
    if (serviceFilter !== "All") {
      filtered = filtered.filter((s) => s.service_name === serviceFilter);
    }
    if (accountFilter !== "All") {
      filtered = filtered.filter((s) => s.account_name === accountFilter);
    }
    setFilteredSavings(filtered);
  }, [serviceFilter, accountFilter, savings]);

  // Unique filter options
  const services = ["All", ...new Set(savings.map((s) => s.service_name || "Unknown"))];
  const accounts = ["All", ...new Set(savings.map((s) => s.account_name || "Unknown"))];

  // Chart data
  const colors = [
    "#4caf50",
    "#2196f3",
    "#ff9800",
    "#e91e63",
    "#9c27b0",
    "#00bcd4",
    "#8bc34a",
    "#ffc107",
    "#795548",
    "#607d8b",
  ];

  const chartData = {
    labels: filteredSavings.map(
      (s) => s.service_name || `Resource ${s.resource_id}`
    ),
    datasets: [
      {
        data: filteredSavings.map((s) => s.actual_savings),
        backgroundColor: filteredSavings.map((_, idx) => colors[idx % colors.length]),
      },
    ],
  };

  // Total
  const totalSavings = filteredSavings.reduce(
    (sum, s) => sum + (s.actual_savings || 0),
    0
  );

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">💰 Savings</h2>

      {/* Filters */}
      <div className="flex gap-4 mb-6">
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
      </div>

      {/* Summary */}
      <p className="text-lg font-semibold mb-6">
        Total Savings:{" "}
        <span className="text-green-600">${totalSavings.toFixed(2)}</span>
      </p>

      {/* Chart */}
      {filteredSavings.length > 0 && (
        <div className="mb-8 w-full md:w-1/2">
          <Pie data={chartData} />
        </div>
      )}

      {/* Table */}
      {filteredSavings.length === 0 ? (
        <p>No savings data available.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full border text-sm text-left dark:text-gray-200">
            <thead className="bg-gray-100 dark:bg-gray-700">
              <tr>
                <th className="px-3 py-2 border">Service</th>
                <th className="px-3 py-2 border">Account</th>
                <th className="px-3 py-2 border">Resource</th>
                <th className="px-3 py-2 border">Savings ($)</th>
                <th className="px-3 py-2 border">Implemented At</th>
              </tr>
            </thead>
            <tbody>
              {filteredSavings.map((s) => (
                <tr key={s.saving_id} className="border-b">
                  <td className="px-3 py-2 border">{s.service_name || "Unknown"}</td>
                  <td className="px-3 py-2 border">{s.account_name || "Unknown"}</td>
                  <td className="px-3 py-2 border">{s.resource_id || "-"}</td>
                  <td className="px-3 py-2 border text-green-600 font-medium">
                    ${s.actual_savings}
                  </td>
                  <td className="px-3 py-2 border">
                    {s.implemented_at
                      ? new Date(s.implemented_at).toLocaleDateString()
                      : "-"}
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

export default Savings;
