import { NavLink } from "react-router-dom";
import {
  HomeIcon,
  CurrencyDollarIcon,
  LightBulbIcon,
  ChartBarIcon,
  ExclamationTriangleIcon,
  ChartPieIcon,
  ClipboardDocumentIcon,
  ServerStackIcon,
  ComputerDesktopIcon,
  Cog6ToothIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";

const menuItems = [
  { path: "/", label: "Overview", icon: HomeIcon },
  { path: "/cost-explorer", label: "Cost Explorer", icon: CurrencyDollarIcon },
  { path: "/recommendations", label: "Recommendations", icon: LightBulbIcon },
  { path: "/savings", label: "Savings", icon: ChartBarIcon },
  { path: "/anomalies", label: "Anomalies", icon: ExclamationTriangleIcon },
  { path: "/forecasts", label: "Forecasts", icon: ChartPieIcon },
  { path: "/budgets", label: "Budgets", icon: ClipboardDocumentIcon },
  { path: "/clusters", label: "Clusters", icon: ServerStackIcon },
  { path: "/ec2", label: "EC2 Utilization", icon: ComputerDesktopIcon },
  { path: "/ops", label: "Ops Dashboard", icon: Cog6ToothIcon },
  { path: "/ai-insights", label: "AI Insights", icon: SparklesIcon },
];

function Sidebar() {
  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="text-2xl font-bold p-6 border-b border-gray-800">
        FinOps Toolkit
      </div>
      <nav className="flex-1 p-4">
        {menuItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              `flex items-center gap-3 p-2 rounded hover:bg-gray-700 ${
                isActive ? "bg-gray-800 font-semibold" : ""
              }`
            }
          >
            <item.icon className="h-5 w-5" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </div>
  );
}

export default Sidebar;
