import { useEffect, useState } from "react";
import { getForecasts } from "../api/finopsApi";
import { Line } from "react-chartjs-2";
import "chart.js/auto";

function Forecasts() {
  const [forecasts, setForecasts] = useState([]);

  useEffect(() => {
    getForecasts()
      .then((res) => setForecasts(res.data))
      .catch((err) => console.error("Error fetching forecasts:", err));
  }, []);

  // ===== Chart Data (grouped by model) =====
  const chartData = {
    labels: forecasts.map((f) => f.forecast_period_end),
    datasets: [
      {
        label: "Prophet",
        data: forecasts
          .filter((f) => f.model_used === "Prophet")
          .map((f) => f.forecast_amount),
        borderColor: "blue",
        tension: 0.3,
      },
      {
        label: "ARIMA",
        data: forecasts
          .filter((f) => f.model_used === "ARIMA")
          .map((f) => f.forecast_amount),
        borderColor: "green",
        tension: 0.3,
      },
      {
        label: "SMA",
        data: forecasts
          .filter((f) => f.model_used === "SMA")
          .map((f) => f.forecast_amount),
        borderColor: "orange",
        tension: 0.3,
      },
      {
        label: "LSTM",
        data: forecasts
          .filter((f) => f.model_used === "LSTM")
          .map((f) => f.forecast_amount),
        borderColor: "red",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="p-6">
      <h2 className="text-xl font-bold mb-4">📈 Forecasts</h2>

      {/* Chart View */}
      {forecasts.length > 0 && (
        <div className="mb-8">
          <Line data={chartData} />
        </div>
      )}

      {/* Old Fallback List View */}
      {forecasts.length === 0 ? (
        <p>No forecasts available.</p>
      ) : (
        <ul className="list-disc ml-6">
          {forecasts.map((f) => (
            <li key={f.forecast_id}>
              Service {f.service_id} → ${f.forecast_amount} ({f.model_used})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Forecasts;
