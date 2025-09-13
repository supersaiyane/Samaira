import { useEffect, useState } from "react";
import axiosClient from "../api/axiosClient";

function Ops() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    axiosClient.get("/logs?limit=20").then((res) => setLogs(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">⚙️ Ops Dashboard</h2>
      {logs.length === 0 ? (
        <p>No recent logs.</p>
      ) : (
        <ul className="list-disc ml-6">
          {logs.map((log) => (
            <li key={log.log_id}>
              [{log.level}] {log.component} → {log.message}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default Ops;
