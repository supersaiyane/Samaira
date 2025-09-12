import { useEffect, useState } from "react";
import { getAccounts, getServices } from "../api/finopsApi";

function CostExplorer() {
  const [accounts, setAccounts] = useState([]);
  const [services, setServices] = useState([]);

  useEffect(() => {
    getAccounts().then((res) => setAccounts(res.data));
    getServices().then((res) => setServices(res.data));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-bold mb-4">💵 Cost Explorer</h2>
      <p className="text-gray-600">Explore costs by account and service.</p>
      <div className="mt-4">
        <h3 className="font-semibold">Accounts:</h3>
        <ul className="list-disc ml-6">
          {accounts.map((a) => (
            <li key={a.account_id}>{a.account_name}</li>
          ))}
        </ul>
      </div>
      <div className="mt-4">
        <h3 className="font-semibold">Services:</h3>
        <ul className="list-disc ml-6">
          {services.map((s) => (
            <li key={s.service_id}>{s.service_name}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default CostExplorer;
