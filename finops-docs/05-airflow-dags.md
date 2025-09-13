📘 Airflow DAGs
===============

1\. Overview
------------

Airflow orchestrates the FinOps workflows:

*   Cost anomaly detection
    
*   Cost forecasting
    
*   Rightsizing & idle detection
    
*   Savings validation
    
*   Auto-remediation
    
*   Instance catalog sync
    

Each DAG follows **ETL principles**: extract from DB/AWS → analyze → load insights → notify (Slack/Teams).

2\. DAGs Implemented
--------------------

### **1\. Anomaly Detection DAG**

*   **File**: airflow/dags/anomaly\_detection.py
    
*   **Schedule**: Daily at 07:00 UTC
    
*   **Inputs**: Billing, usage, budgets, forecasts
    
*   **Logic**:
    
    *   Detects cost spikes (yesterday vs historical avg + stddev).
        
    *   Flags high CPU/memory usage, idle Lambdas, orphaned resources.
        
    *   Validates budget breaches & forecast drifts.
        
    *   Classifies severity: low, medium, high.
        
*   **Outputs**:
    
    *   Records anomalies in anomalies table.
        
    *   Sends alerts (Slack/Teams).
        
*   **Downstream**:
    
    *   Feeds Auto-remediation DAG.
        
    *   Powers dashboards.
        

### **2\. Cost Forecasting DAG**

*   **File**: airflow/dags/cost\_forecasting.py
    
*   **Schedule**: Daily at 10:00 UTC
    
*   **Inputs**: Billing (last 24 months)
    
*   **Logic**:
    
    *   Trains multiple models: Prophet, ARIMA, SMA.
        
    *   Selects best model per account/service (lowest MAPE/RMSE).
        
    *   Generates forecasts for 30/90/180 days.
        
    *   Stores confidence intervals.
        
*   **Outputs**:
    
    *   Writes forecasts → forecasts table.
        
    *   Notifies Slack/Teams with summary.
        
*   **Downstream**:
    
    *   Drives **Forecast dashboards**.
        
    *   Triggers anomalies when drift > tolerance.
        

### **3\. Rightsizing & Idle Detection DAG**

*   **File**: airflow/dags/rightsizing.py
    
*   **Schedule**: Daily at 04:00 UTC
    
*   **Inputs**: Usage (CPU, Memory, Invocations), InstanceCatalog, AWS Pricing API
    
*   **Logic**:
    
    *   EC2: Compares CPU < 20% → suggest smaller instance.
        
    *   ECS/EKS: Detects underutilized tasks/nodes.
        
    *   Lambda: Detects inactivity or oversizing.
        
    *   Enriches with AWS Pricing → estimated savings.
        
*   **Outputs**:
    
    *   Inserts recommendations into recommendations.
        
*   **Downstream**:
    
    *   Tracked by **Savings Tracker**.
        
    *   Used in **Insights dashboards**.
        

### **4\. Savings Tracker DAG**

*   **File**: airflow/dags/savings\_tracker.py
    
*   **Schedule**: Daily at 09:00 UTC
    
*   **Inputs**: Recommendations (status = applied), Billing (before/after 30d)
    
*   **Logic**:
    
    *   Compares costs before vs after recommendation applied.
        
    *   Marks recommendation as validated or no\_savings.
        
    *   Updates savings table with actual savings.
        
*   **Outputs**:
    
    *   Insights for realized savings.
        
    *   Slack/Teams updates: “💰 $X validated”.
        
*   **Downstream**:
    
    *   Drives **Savings dashboard**.
        

### **5\. Auto-Remediation DAG**

*   **File**: airflow/dags/auto\_remediation.py
    
*   **Schedule**: Daily at 08:00 UTC (after anomalies)
    
*   **Inputs**: anomalies table, playbooks (airflow/playbooks/\*.yaml)
    
*   **Logic**:
    
    *   Loads playbooks for each issue/service combo.
        
    *   Executes remediation (EC2 stop, Lambda delete, notify-only).
        
    *   Updates anomaly status → remediated or ignored.
        
*   **Outputs**:
    
    *   Audit trail in DB.
        
    *   Slack/Teams notifications (“✅ Stopped idle EC2 i-123…”).
        
*   **Downstream**:
    
    *   Logs → logs table.
        
    *   Insights for remediation success rate.
        

### **6\. Instance Catalog Updater DAG**

*   **File**: airflow/dags/instance\_catalog\_updater.py
    
*   **Schedule**: Weekly (Sunday 03:00 UTC)
    
*   **Inputs**: AWS Pricing API
    
*   **Logic**:
    
    *   Fetches latest EC2 families, sizes, vCPU, memory, pricing.
        
    *   Updates instance\_catalog.
        
*   **Outputs**:
    
    *   Keeps rightsizing recommendations accurate.
        
*   **Downstream**:
    
    *   Used by **Rightsizing DAG**.
        

3\. Notifications
-----------------

All DAGs integrate with:

*   **Slack** (block messages, summaries).
    
*   **Teams** (cards).
    
*   Alerts are contextual (e.g., “No anomalies today ✅” vs “🚨 5 budget breaches”).
    

4\. Orchestration Order
-----------------------

1.  **04:00** → Rightsizing (generate recommendations).
    
2.  **07:00** → Anomaly Detection.
    
3.  **08:00** → Auto-Remediation (respond to anomalies).
    
4.  **09:00** → Savings Tracker (validate recommendations).
    
5.  **10:00** → Cost Forecasting.
    
6.  **Weekly Sunday 03:00** → Instance Catalog Update.
    

5\. Knowledge Check
-------------------

1.  Which DAG is responsible for **validating savings**?
    
2.  How does the **forecasting DAG** choose the best model?
    
3.  Why does **Auto-remediation DAG** load playbooks from YAML?
    
4.  Which DAG depends on instance\_catalog?
    
5.  What’s the order of DAG execution in a single day