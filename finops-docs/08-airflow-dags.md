🚀 Airflow DAGs Guide
=====================

1\. Overview
------------

Airflow orchestrates **data ingestion, cost optimization, anomaly detection, forecasting, and savings tracking**.All DAGs are placed in:

```
airflow/dags/
```

2\. DAG List
------------

 **#** | **DAG Name**             | **Purpose**                                                    | **** | **** | **** | **** | **** | **** | **** | **** 
-------|--------------------------|----------------------------------------------------------------|------|------|------|------|------|------|------|------
 1     | billing_ingest           | Collect AWS Cost Explorer billing data     
 2     | usage_ingest             | Collect CloudWatch metrics for EC2, ECS, EKS, Lambda
 3     | rightsizing              | Detect idle/underutilized resources, generate recommendations
 4     | anomaly_detection_v2     | Detect cost/usage/budget/forecast anomalies    
 5     | auto_remediation         | Apply fixes via playbooks (stop EC2, delete idle Lambda, etc.)
 6     | cost_forecasting_v2      | Generate forecasts with Prophet/ARIMA/SMA    
 7     | savings_tracker          | Measure realized savings from applied recommendations     
 8     | instance_catalog_updater | Weekly sync of AWS EC2 instance families & pricing 
  

3\. Billing Ingest DAG
----------------------

**File:** billing\_ingest.py

*   Uses **Cost Explorer API**.
    
*   Multi-account ingestion via AWS Organizations.
    
*   Normalizes accounts table.
    
*   Inserts into billing table.
    

Schedule: every **6 hours** (0 \*/6 \* \* \*).

4\. Usage Ingest DAG
--------------------

**File:** usage\_ingest.py

*   Uses **CloudWatch Metrics API**.
    
*   Services:
    
    *   EC2 (CPU, NetworkIn/Out).
        
    *   ECS (CPU/Memory).
        
    *   EKS (Container Insights).
        
    *   Lambda (Invocations, Duration).
        
*   Maps resources → resources table.
    
*   Inserts into usage table.
    

Schedule: every **6 hours**.

5\. Rightsizing DAG
-------------------

**File:** rightsizing.py

*   Pulls from usage.
    
*   Logic:
    
    *   **Idle**: CPU < 5% (EC2/ECS/EKS) or Invocations = 0 (Lambda).
        
    *   **Rightsize**: CPU < 20% → recommend smaller instance/task/node.
        
*   **Dynamic pricing** via AWS Pricing API.
    
*   Inserts into recommendations table.
    

Schedule: daily 4 AM.

6\. Anomaly Detection DAG
-------------------------

**File:** anomaly\_detection\_v2.py

*   Types:
    
    1.  Cost spikes (day vs history).
        
    2.  Usage anomalies (CPU > 90%, Memory > 85%).
        
    3.  Idle/orphan resources (cost > 10$, usage < 1%).
        
    4.  Budget breaches (budgets table).
        
    5.  Forecast drift (forecast vs actual).
        
*   Notifications: **Slack + Teams**.
    
*   Inserts into anomalies table.
    

Schedule: daily 7 AM.

7\. Auto-Remediation DAG
------------------------

**File:** auto\_remediation.py

*   Reads unresolved anomalies.
    
*   Executes playbooks (YAML in airflow/playbooks/).
    
*   Examples:
    
    *   Stop EC2 instance.
        
    *   Delete idle Lambda.
        
    *   Notify for Budget/Forecast drift.
        
*   Updates anomalies.status.
    
*   Notifies Slack/Teams.
    

Schedule: daily 8 AM.

8\. Forecasting DAG
-------------------

**File:** cost\_forecasting\_v2.py

*   Models: **Prophet, ARIMA, SMA baseline**.
    
*   Selects best model based on **MAPE + RMSE**.
    
*   Generates **30, 90, 180d forecasts**.
    
*   Stores in forecasts table.
    
*   Notifies summary via Slack/Teams.
    

Schedule: daily 10 AM.

9\. Savings Tracker DAG
-----------------------

**File:** savings\_tracker.py

*   Tracks recommendations with status='applied'.
    
*   Compares billing **30d before vs after**.
    
*   Inserts into savings table.
    
*   Updates recommendation status → validated or no\_savings.
    

Schedule: daily 9 AM.

10\. Instance Catalog Updater DAG
---------------------------------

**File:** instance\_catalog\_updater.py

*   Syncs **EC2 instance families & pricing** weekly.
    
*   Populates instance\_catalog table.
    
*   Used by Rightsizing DAG for accurate downsizing.
    

Schedule: weekly (Sunday at 3 AM).

11\. DAG Dependencies
---------------------

```
instance_catalog_updater ─▶ rightsizing
billing_ingest ───────────▶ anomaly_detection, forecasting
usage_ingest ─────────────▶ rightsizing, anomaly_detection
rightsizing ──────────────▶ savings_tracker
anomaly_detection ────────▶ auto_remediation

```

12\. Knowledge Check
--------------------

1.  Which DAG uses **AWS Pricing API**?
    
2.  What DAG is scheduled after anomaly detection?
    
3.  How does the savings tracker validate recommendations?
    
4.  Which DAG feeds the **instance\_catalog** table?
    
5.  How do anomaly detection results trigger auto-remediation?