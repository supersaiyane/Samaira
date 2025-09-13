📘 FastAPI APIs
===============

1\. Overview
------------

The **backend** exposes REST APIs via FastAPI (app/main.py) under the prefix:

```
/api/v1/*
```

It is modularized into routers grouped by feature:

*   **Accounts**
    
*   **Services**
    
*   **Resources**
    
*   **Billing & Usage**
    
*   **Recommendations**
    
*   **Savings**
    
*   **Anomalies**
    
*   **Forecasts**
    
*   **Insights**
    
*   **AI Assistant**
    

2\. API Routers
---------------

### 🔹 Accounts

*   **File**: app/api/v1/accounts.py
    
*   **Endpoints**:
    
    *   GET /accounts/ → List accounts.
        
    *   GET /accounts/{id} → Fetch account details.
        
    *   POST /accounts/ → Add account (from onboarding).
        
*   **DB Tables**: accounts
    

### 🔹 Services

*   **File**: app/api/v1/services.py
    
*   **Endpoints**:
    
    *   GET /services/ → List cloud services.
        
    *   GET /services/{id} → Fetch service metadata.
        
*   **DB Tables**: services, service\_categories, unmapped\_services
    

### 🔹 Resources

*   **File**: app/api/v1/resources.py
    
*   **Endpoints**:
    
    *   GET /resources/ → List resources (filter by account/service).
        
    *   GET /resources/{id} → Fetch details (tags, region, type).
        
*   **DB Tables**: resources, clusters, cluster\_resources
    

### 🔹 Billing & Usage

*   **File**: app/api/v1/billing.py
    
*   **Endpoints**:
    
    *   GET /billing/ → Cost data per account/service.
        
    *   GET /billing/summary → MTD spend, daily trend.
        
*   **DB Tables**: billing, usage
    

### 🔹 Recommendations

*   **File**: app/api/v1/recommendations.py
    
*   **Endpoints**:
    
    *   GET /recommendations/ → List active recommendations.
        
    *   POST /recommendations/apply/{id} → Mark as applied.
        
*   **DB Tables**: recommendations
    

### 🔹 Savings

*   **File**: app/api/v1/savings.py
    
*   **Endpoints**:
    
    *   GET /savings/ → List validated savings.
        
    *   GET /savings/summary → Total validated savings.
        
*   **DB Tables**: savings
    

### 🔹 Anomalies

*   **File**: app/api/v1/anomalies.py
    
*   **Endpoints**:
    
    *   GET /anomalies/ → List anomalies (with filters).
        
    *   GET /anomalies/summary → Count by severity.
        
*   **DB Tables**: anomalies
    

### 🔹 Forecasts

*   **File**: app/api/v1/forecasts.py
    
*   **Endpoints**:
    
    *   GET /forecasts/ → Forecast records.
        
    *   GET /forecasts/summary → Next 30/90/180d spend.
        
*   **DB Tables**: forecasts
    

### 🔹 Insights

*   **File**: app/api/v1/insights.py
    
*   **Endpoints**:
    
    *   GET /insights/ → List insights (combined anomalies, savings, recs).
        
    *   GET /insights/summary → Aggregated metrics:
        
        *   by severity
            
        *   top services
            
        *   daily trend
            
        *   top accounts
            
        *   cost MTD
            
        *   savings validated
            
        *   forecast (30d)
            
*   **DB Tables**: insights
    

### 🔹 AI Assistant

*   **File**: app/api/v1/ai.py
    
*   **Endpoints**:
    
    *   POST /ai/query
        
        *   Input: { "query": "Show me top 5 services with rising costs" }
            
        *   Output: JSON with results from SQL query.
            
        *   Logs query into ai\_queries\_log.
            
*   **DB Tables**: ai\_queries\_log
    

3\. Authentication (Future)
---------------------------

*   Currently open endpoints (local dev).
    
*   Extendable with:
    
    *   OAuth2 (JWT tokens).
        
    *   SSO integration.
        
    *   Role-based access control (RBAC).
        

4\. API Usage Example
---------------------

**Example: Fetch insights summary**

```
curl http://localhost:8000/api/v1/insights/summary?days=30

```

Response:

```
{
  "by_severity": [
    {"severity": "critical", "count": 3},
    {"severity": "warning", "count": 7}
  ],
  "top_services": [
    {"service_name": "EC2", "count": 5}
  ],
  "trend": [
    {"day": "2025-09-01", "count": 4}
  ],
  "top_accounts": [
    {"account_name": "prod-aws", "count": 6}
  ],
  "total_cost_mtd": 12345.67,
  "total_savings": 456.78,
  "active_anomalies": 2,
  "forecast_30d": 56789.01,
  "daily_trend": []
}


```

5\. Knowledge Check
-------------------

1.  Which API endpoint provides **validated savings summary**?
    
2.  How are **insights** different from anomalies?
    
3.  What happens when an AI query is unsupported?
    
4.  Which table powers /api/v1/forecasts/summary?
    
5.  How would you extend the APIs with **RBAC**?