import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Sidebar from "./layouts/Sidebar";
import Navbar from "./layouts/Navbar";
import routes from "./routes";

function App() {
  return (
    <Router>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex flex-col flex-1">
          <Navbar />
          <main className="p-6 overflow-auto">
            <Routes>
              {routes.map((route, idx) => (
                <Route key={idx} path={route.path} element={<route.component />} />
              ))}
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
