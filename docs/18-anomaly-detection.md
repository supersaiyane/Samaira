📌 Overview
-----------

Anomaly detection identifies unusual patterns in **cost, usage, or forecasts** that could indicate:

*   Unexpected cost spikes (e.g., misconfigured resources, runaway jobs).
    
*   Performance anomalies (e.g., high CPU/Memory).
    
*   Idle/orphaned resources still incurring cost.
    
*   Forecast drifts (actuals diverging from predictions).
    
*   Budget breaches.
    

The goal is to **alert FinOps teams early** to investigate, take corrective action, or trigger auto-remediation.

🏗️ Workflow
------------

### 1\. Input Data

*   **Billing Data** (billing table): Cost and usage quantities by account/service/date.
    
*   **Usage Metrics** (usage table): CPU, memory, Lambda invocations, etc.
    
*   **Budgets** (budgets table): Predefined monthly limits.
    
*   **Forecasts** (forecasts table): Model-generated predictions (Prophet, ARIMA, SMA).
    

### 2\. Detection Process

The anomaly DAG (anomaly\_detection\_v3) evaluates across multiple dimensions:

1.  **Cost anomalies** – Compare daily costs against historical averages (last 30 days).
    
2.  **Usage anomalies** – Detect unusually high CPU/memory or Lambda inactivity.
    
3.  **Idle/orphan resources** – High cost with negligible usage.
    
4.  **Budget breaches** – Monthly-to-date spend exceeds allocated budget.
    
5.  **Forecast drift** – Actuals fall outside forecast confidence intervals.
    

### 3\. Classification

Each anomaly is tagged with:

*   severity: low / medium / high (based on deviation magnitude & criticality).
    
*   issue: cost spike, budget breach, idle resource, forecast drift, etc.
    
*   status: unresolved → remediated/ignored.
    

⚙️ DAG Structure
----------------

*   **Task: detect\_anomalies**
    
    *   Pulls last 30–60 days of billing + usage.
        
    *   Runs cost anomaly detection using statistical thresholds (deviation > 50% + beyond 2× stddev).
        
    *   Checks budget, usage, idle, and forecast drifts.
        
    *   Inserts anomalies into anomalies table.
        
    *   Notifies via Slack & Teams.
        
*   **Schedule**: Daily at **07:00 UTC**(gives fresh data from previous day before business hours).
    

🧠 Technical Details
--------------------

### Cost Anomalies

*   deviation = (observed - mean) / mean × 100
    
*   If |deviation| > threshold (default: 50%) **AND** difference > 2×stddev → anomaly.
    

### Usage Anomalies

*   **CPUUtilization** > 90% (sustained) → performance anomaly.
    
*   **MemoryUtilization** > 85% → performance anomaly.
    
*   **Lambda Invocations** = 0 (over 7 days) → inactive.
    

### Idle Resources

*   Query billing per resource vs. avg usage.
    
*   If cost > $10 but avg usage < 1% → idle.
    

### Budget Breaches

*   Compare MTD cost vs. budget\_limit.
    
*   Severity = high if exceeded.
    

### Forecast Drift

*   Compare actual cost vs. forecast confidence intervals.
    
*   If outside range → anomaly.
    

🛠️ Database Tables
-------------------

### anomalies

| Column            | Type         | Description                               |
|-------------------|--------------|-------------------------------------------|
| anomaly_id        | SERIAL PK    | Unique anomaly                            |
| account_id        | FK(accounts) | Related account                           |
| service_id        | FK(services) | Related service                           |
| detected_at       | TIMESTAMP    | When detected                             |
| metric            | VARCHAR      | Metric (cost, cpu, memory, etc.)          |
| observed_value    | NUMERIC      | Actual observed                           |
| expected_value    | NUMERIC      | Historical mean / forecast                |
| deviation_percent | NUMERIC      | % deviation                               |
| severity          | VARCHAR      | low/medium/high                           |
| details           | JSON         | Extra metadata (issue, resource_id, etc.) |
| status            | VARCHAR      | unresolved/remediated                     |

📊 Example Anomaly
------------------

```
{
  "anomaly_id": 402,
  "account_id": 10,
  "service_id": 2,
  "detected_at": "2025-09-13T07:00:00Z",
  "metric": "cost",
  "observed_value": 1240.50,
  "expected_value": 680.00,
  "deviation_percent": 82.35,
  "severity": "high",
  "details": {
    "issue": "Cost Spike",
    "window": "last_24h",
    "threshold": 50
  },
  "status": "unresolved"
}

```

🔔 Notifications
----------------

*   **Slack** → Block Kit with top 10 anomalies (account, service, issue, observed vs expected).
    
*   **Teams** → Simple card summary of anomalies.
    
*   **No anomalies** → “✅ No anomalies detected” message.
    

✅ Key Benefits
--------------

*   Detects waste early (idle/orphan resources).
    
*   Protects against unexpected spend (cost spikes).
    
*   Guards governance policies (budget enforcement).
    
*   Improves trust in forecasts by flagging drift.
    
*   Integrates with **auto-remediation DAG**.
    

❓ Review Questions
------------------

1.  What five types of anomalies does the system detect?
    
2.  How does the DAG decide if a cost deviation is anomalous?
    
3.  What’s the difference between a **budget breach** and a **forecast drift**?
    
4.  How are anomalies stored in the database for further remediation?
    
5.  Why is scheduling anomaly detection at **07:00 UTC** beneficial?