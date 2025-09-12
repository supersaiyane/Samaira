import { useEffect, useState } from "react";
import { getRecommendations } from "../api/finopsApi";

function Recommendations() {
  const [recs, setRecs] = useState([]);

  useEffect(() => {
    getRecommendations().then((res) => setRecs(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">🛠️ Recommendations</h2>
      {recs.length === 0 ? (
        <p>No recommendations available.</p>
      ) : (
        <ul className="list-disc ml-6">
          {recs.map((r) => (
            <li key={r.rec_id}>
              {r.rec_type} → {r.status} (savings: ${r.estimated_savings})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Recommendations;
