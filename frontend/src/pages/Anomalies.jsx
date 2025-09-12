import { useEffect, useState } from "react";
import { getAnomalies } from "../api/finopsApi";

function Anomalies() {
  const [anomalies, setAnomalies] = useState([]);

  useEffect(() => {
    getAnomalies().then((res) => setAnomalies(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">🚨 Anomalies</h2>
      {anomalies.length === 0 ? (
        <p>No anomalies detected.</p>
      ) : (
        <ul className="list-disc ml-6">
          {anomalies.map((a) => (
            <li key={a.anomaly_id}>
              {a.metric} deviation {a.deviation_percent}% (Observed: {a.observed_value})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Anomalies;
