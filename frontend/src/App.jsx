import { Navigate } from "react-router-dom";
import Insights from "./pages/Insights";
import Forecasts from "./pages/Forecasts";
import Savings from "./pages/Savings";
import IdleResources from "./pages/IdleResources";
import Anomalies from "./pages/Anomalies";
import Drift from "./pages/Drift"; // ✅ NEW

const routes = [
  // Default redirect: when user hits `/`, go to `/insights`
  { path: "/", component: () => <Navigate to="/insights" replace /> },

  { path: "/insights", component: Insights },
  { path: "/forecast", component: Forecasts },
  { path: "/savings", component: Savings },
  { path: "/idle", component: IdleResources },
  { path: "/anomalies", component: Anomalies },
  { path: "/drift", component: Drift }, // ✅ NEW ROUTE
];

export default routes;
