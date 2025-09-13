import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

function EC2() {
  const [instances, setInstances] = useState([]);

  useEffect(() => {
    axiosClient.get("/resources?service=EC2").then((res) => setInstances(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">💻 EC2 Utilization</h2>
      {instances.length === 0 ? (
        <p>No EC2 instances found.</p>
      ) : (
        <ul className="list-disc ml-6">
          {instances.map((i) => (
            <li key={i.resource_id}>
              {i.resource_name} ({i.region}) → {i.resource_type}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default EC2;
