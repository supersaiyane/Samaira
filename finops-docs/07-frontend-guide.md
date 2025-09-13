🎨 Frontend Guide (React + Tailwind + Heroicons)
================================================

1\. Overview
------------

The **frontend** is a React application styled with **TailwindCSS** and icons from **Heroicons**.

It provides:

*   Navbar (dark mode, search, profile).
    
*   Dashboard pages (Insights, Savings, Anomalies, Forecasts, Recommendations).
    
*   Integration with backend APIs (/api/v1/\*).
    
*   AI-powered query bar (wired to /api/v1/ai/query).
    

2\. Project Structure
---------------------

```
frontend/
├── public/              # Static files
├── src/
│   ├── components/      # Reusable UI components
│   │   ├── Navbar.js
│   │   ├── Sidebar.js
│   │   └── Cards/
│   ├── pages/           # Screens (Insights, Savings, etc.)
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API clients (axios/fetch wrappers)
│   ├── App.js           # Root app
│   └── index.js         # Entry point
├── tailwind.config.js   # Tailwind setup
└── package.json

```

3\. Navbar (Current Features)
-----------------------------

*   **Dark mode toggle**
    
    *   Persists in localStorage.
        
    *   Applies dark class to .
        
*   **Search bar**
    
    *   Connected to /api/v1/ai/query.
        
    *   Displays AI query results inline.
        
*   **User profile**
    
    *   Placeholder → UserCircleIcon.
        

4\. Pages
---------

### 🔹 Insights

*   Shows aggregated insights summary:
    
    *   By severity
        
    *   Top services
        
    *   Top accounts
        
    *   Cost MTD, Savings MTD, Forecast (30d).
        

API: /api/v1/insights/summary

### 🔹 Savings

*   List of savings and summary.
    
*   Shows “Validated” vs “No Savings”.
    

API: /api/v1/savings/

### 🔹 Anomalies

*   List anomalies (with filters).
    
*   Color-coded severity (info, warning, critical).
    

API: /api/v1/anomalies/

### 🔹 Forecasts

*   Charts for cost projections (30, 90, 180d).
    
*   Compare forecast vs actual.
    

API: /api/v1/forecasts/summary

### 🔹 Recommendations

*   Shows rightsizing & idle opportunities.
    
*   Button to mark recommendation as **applied**.
    

API: /api/v1/recommendations/

5\. Tailwind Setup
------------------

*   Config in tailwind.config.js
    
*   Supports **dark mode via class**.
    
*   Example usage:
    

```
<div className="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100">
   Hello World
</div>

```

6\. AI Query Bar
----------------

*   Component: integrated in Navbar.js.
    
*   Flow:
    
    1.  User enters natural language → "Show top 5 services by cost".
        
    2.  Request sent to /api/v1/ai/query.
        
    3.  Backend translates → SQL → executes → returns results.
        
    4.  Results displayed under the search bar.
        

7\. Example API Client
----------------------

frontend/src/services/api.js

```
import axios from "axios";


const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";


export const getInsightsSummary = async () => {
  const res = await axios.get(`${API_URL}/insights/summary`);
  return res.data;
};


export const askAI = async (query) => {
  const res = await axios.post(`${API_URL}/ai/query`, { query });
  return res.data;
};


```

8\. Knowledge Check
-------------------

1.  Which frontend component integrates with /api/v1/ai/query?
    
2.  How is dark mode persisted across reloads?
    
3.  Which API powers the **Forecasts** page?
    
4.  Where would you add a new page (e.g., Budgets)?
    
5.  What does tailwind.config.js control?