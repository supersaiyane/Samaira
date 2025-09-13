import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

function Clusters() {
  const [clusters, setClusters] = useState([]);

  useEffect(() => {
    axiosClient.get("/clusters").then((res) => setClusters(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">🖥️ Clusters</h2>
      {clusters.length === 0 ? (
        <p>No clusters found.</p>
      ) : (
        <ul className="list-disc ml-6">
          {clusters.map((c) => (
            <li key={c.cluster_id}>
              {c.cluster_name} ({c.cluster_type}, {c.region})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Clusters;
