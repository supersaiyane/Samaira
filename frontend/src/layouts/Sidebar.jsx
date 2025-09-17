import { useState, useEffect } from "react";
import { NavLink, useLocation } from "react-router-dom";
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
  ArrowTrendingDownIcon,
  ChevronDownIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";
import {
  getAnomaliesCount,
  getSavingsTotal,
  getBudgetBreaches,
  getClustersCount,      // ✅ NEW
  getIdleEC2Count,       // ✅ NEW
} from "../api/finopsApi";

const sections = [
  {
    key: "overview",
    title: "🏠 Overview",
    items: [{ path: "/", label: "Overview", icon: HomeIcon }],
  },
  {
    key: "analysis",
    title: "📊 Analysis & Insights",
    items: [
      { path: "/cost-explorer", label: "Cost Explorer", icon: CurrencyDollarIcon },
      { path: "/recommendations", label: "Recommendations", icon: LightBulbIcon },
      { path: "/insights", label: "Insights", icon: SparklesIcon },
    ],
  },
  {
    key: "forecasting",
    title: "📉 Forecasting & Anomalies",
    items: [
      { path: "/forecasts", label: "Forecasts", icon: ChartPieIcon },
      { path: "/drift", label: "Drift Detection", icon: ArrowTrendingDownIcon },
      { path: "/anomalies", label: "Anomalies", icon: ExclamationTriangleIcon, badge: "anomalies" },
      { path: "/savings", label: "Savings", icon: ChartBarIcon, badge: "savings" },
    ],
  },
  {
    key: "ops",
    title: "⚙️ Ops & Resources",
    items: [
      { path: "/budgets", label: "Budgets", icon: ClipboardDocumentIcon, badge: "budgets" },
      { path: "/clusters", label: "Clusters", icon: ServerStackIcon, badge: "clusters" }, // ✅ NEW
      { path: "/ec2", label: "EC2 Utilization", icon: ComputerDesktopIcon, badge: "ec2" }, // ✅ NEW
      { path: "/ops", label: "Ops Dashboard", icon: Cog6ToothIcon },
    ],
  },
  {
    key: "ai",
    title: "🤖 AI",
    items: [{ path: "/ai-insights", label: "AI Insights", icon: SparklesIcon }],
  },
];

function Sidebar() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState({});
  const [counts, setCounts] = useState({
    anomalies: 0,
    savings: 0,
    budgets: 0,
    clusters: 0,   // ✅ NEW
    ec2: 0,        // ✅ NEW
  });

  // Fetch counts for badges
  useEffect(() => {
    async function fetchCounts() {
      try {
        const anomaliesRes = await getAnomaliesCount();
        const savingsRes = await getSavingsTotal();
        const budgetsRes = await getBudgetBreaches();
        const clustersRes = await getClustersCount();
        const ec2Res = await getIdleEC2Count();

        setCounts({
          anomalies: anomaliesRes.data?.count || 0,
          savings: savingsRes.data?.total || 0,
          budgets: budgetsRes.data?.breaches || 0,
          clusters: clustersRes.data?.count || 0,
          ec2: ec2Res.data?.idle || 0,
        });
      } catch (err) {
        console.error("Error fetching sidebar counts:", err);
      }
    }
    fetchCounts();
  }, []);

  // Toggle collapse
  const toggleSection = (key) => {
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="w-64 bg-gray-900 text-white flex flex-col">
      <div className="text-2xl font-bold p-6 border-b border-gray-800">
        FinOps Toolkit
      </div>
      <nav className="flex-1 p-4 space-y-6">
        {sections.map((section) => {
          const isActive = section.items.some((item) =>
            location.pathname.startsWith(item.path)
          );
          const isCollapsed = collapsed[section.key];

          return (
            <div key={section.key}>
              {/* Section Header */}
              <div
                className={`flex items-center justify-between text-xs uppercase tracking-wider cursor-pointer mb-2 ${
                  isActive ? "text-yellow-400 font-semibold" : "text-gray-400"
                }`}
                onClick={() => toggleSection(section.key)}
              >
                <span>{section.title}</span>
                {isCollapsed ? (
                  <ChevronRightIcon className="h-4 w-4" />
                ) : (
                  <ChevronDownIcon className="h-4 w-4" />
                )}
              </div>

              {/* Section Items */}
              {!isCollapsed &&
                section.items.map((item) => (
                  <NavLink
                    key={item.path}
                    to={item.path}
                    className={({ isActive }) =>
                      `flex items-center justify-between gap-3 p-2 rounded hover:bg-gray-700 ${
                        isActive ? "bg-gray-800 font-semibold" : ""
                      }`
                    }
                  >
                    <div className="flex items-center gap-3">
                      <item.icon className="h-5 w-5" />
                      {item.label}
                    </div>
                    {/* Badge Support */}
                    {item.badge && counts[item.badge] > 0 && (
                      <span className="bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">
                        {item.badge === "savings"
                          ? `$${counts[item.badge]}`
                          : counts[item.badge]}
                      </span>
                    )}
                  </NavLink>
                ))}
            </div>
          );
        })}
      </nav>
    </div>
  );
}

export default Sidebar;
