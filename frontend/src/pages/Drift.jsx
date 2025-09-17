import { useEffect, useState } from "react";
import { getDrift } from "../api/finopsApi";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

function Drift() {
  const [driftData, setDriftData] = useState([]);

  useEffect(() => {
    getDrift()
      .then((res) => setDriftData(res.data))
      .catch((err) => console.error("Error fetching drift data:", err));
  }, []);

  // ===== Line Chart: Actual vs Forecast =====
  const chartData = {
    labels: driftData.map((d) => d.date),
    datasets: [
      {
        label: "Actual Cost",
        data: driftData.map((d) => d.actual_cost),
        borderColor: "#4caf50",
        fill: false,
      },
      {
        label: "Forecast Cost",
        data: driftData.map((d) => d.forecast_cost),
        borderColor: "#2196f3",
        borderDash: [5, 5],
        fill: false,
      },
    ],
  };

  // ===== Drift Metrics =====
  const driftMetrics = driftData.reduce(
    (acc, d) => {
      acc.total += 1;
      if (d.drift_percent > 20) acc.alerts += 1; // threshold = 20%
      return acc;
    },
    { total: 0, alerts: 0 }
  );

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">📉 Forecast Drift Detection</h2>

      {/* Chart View */}
      {driftData.length > 0 && (
        <div className="mb-8">
          <Line data={chartData} />
        </div>
      )}

      {/* Summary */}
      <div className="mb-6 text-sm">
        <p>
          Total Data Points: <b>{driftMetrics.total}</b>
        </p>
        <p className="text-red-500">
          Drift Alerts (>{">"}20% deviation): <b>{driftMetrics.alerts}</b>
        </p>
      </div>

      {/* Table View */}
      {driftData.length === 0 ? (
        <p>No drift data available.</p>
      ) : (
        <table className="min-w-full border text-sm text-left dark:text-gray-200">
          <thead className="bg-gray-100 dark:bg-gray-700">
            <tr>
              <th className="px-3 py-2 border">Date</th>
              <th className="px-3 py-2 border">Service</th>
              <th className="px-3 py-2 border">Actual Cost</th>
              <th className="px-3 py-2 border">Forecast Cost</th>
              <th className="px-3 py-2 border">Drift %</th>
            </tr>
          </thead>
          <tbody>
            {driftData.map((d, idx) => (
              <tr key={idx} className="border-b">
                <td className="px-3 py-2 border">{d.date}</td>
                <td className="px-3 py-2 border">{d.service_name}</td>
                <td className="px-3 py-2 border">${d.actual_cost}</td>
                <td className="px-3 py-2 border">${d.forecast_cost}</td>
                <td
                  className={`px-3 py-2 border ${
                    d.drift_percent > 20 ? "text-red-500 font-bold" : ""
                  }`}
                >
                  {d.drift_percent}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default Drift;
