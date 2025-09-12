import { useEffect, useState } from "react";
import { getForecasts } from "../api/finopsApi";

function Forecasts() {
  const [forecasts, setForecasts] = useState([]);

  useEffect(() => {
    getForecasts().then((res) => setForecasts(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">📈 Forecasts</h2>
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
