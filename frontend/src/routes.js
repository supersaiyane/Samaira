import Overview from "./pages/Overview";
import CostExplorer from "./pages/CostExplorer";
import Recommendations from "./pages/Recommendations";
import Savings from "./pages/Savings";
import Anomalies from "./pages/Anomalies";
import Forecasts from "./pages/Forecasts";
import Budgets from "./pages/Budgets";
import Clusters from "./pages/Clusters";
import EC2 from "./pages/EC2";
import Ops from "./pages/Ops";
import AIInsights from "./pages/AIInsights";

export default [
  { path: "/", component: Overview },
  { path: "/cost-explorer", component: CostExplorer },
  { path: "/recommendations", component: Recommendations },
  { path: "/savings", component: Savings },
  { path: "/anomalies", component: Anomalies },
  { path: "/forecasts", component: Forecasts },
  { path: "/budgets", component: Budgets },
  { path: "/clusters", component: Clusters },
  { path: "/ec2", component: EC2 },
  { path: "/ops", component: Ops },
  { path: "/ai-insights", component: AIInsights },
];
