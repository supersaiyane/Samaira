import { Link } from "react-router-dom";

const links = [
  { path: "/", label: "Overview" },
  { path: "/cost-explorer", label: "Cost Explorer" },
  { path: "/recommendations", label: "Recommendations" },
  { path: "/savings", label: "Savings" },
  { path: "/anomalies", label: "Anomalies" },
  { path: "/forecasts", label: "Forecasts" },
  { path: "/budgets", label: "Budgets" },
  { path: "/clusters", label: "Clusters" },
  { path: "/ec2", label: "EC2" },
  { path: "/ops", label: "Ops" },
  { path: "/ai-insights", label: "AI Insights" },
];

function Sidebar() {
  return (
    <aside className="w-64 bg-gray-800 text-gray-200 flex flex-col">
      <div className="p-6 text-2xl font-bold">FinOps</div>
      <nav className="flex-1 px-4">
        {links.map((link) => (
          <Link
            key={link.path}
            to={link.path}
            className="block px-4 py-2 rounded hover:bg-gray-700"
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}

export default Sidebar;
