📌 Overview
-----------

The **Savings Tracker** validates whether **applied recommendations** (e.g., rightsizing, idle shutdowns) actually led to **realized savings**.It closes the loop between:

1.  **Recommendation** → Suggested by rightsizing/idle detection.
    
2.  **Implementation** → Applied by engineers/automation.
    
3.  **Validation** → Savings measured in **billing data**.
    

This ensures FinOps teams don’t just generate recommendations but also measure **ROI**.

🏗️ Workflow
------------

### 1\. Input Data

*   **recommendations table** → Recommendations with status = applied.
    
*   **billing table** → Historical cost (before/after change).
    
*   **resources table** → Maps recommendation to account/service.
    

### 2\. Processing Steps

1.  Identify **applied recommendations**.
    
2.  For each recommendation:
    
    *   Get **30 days cost before** applied.
        
    *   Get **30 days cost after** applied.
        
    *   Calculate savings = before – after.
        
3.  Write into **savings table**.
    
4.  Update recommendation status:
    
    *   ✅ validated if savings > 0.
        
    *   ❌ no\_savings if not.
        

### 3\. Output

*   Historical savings records → savings table.
    
*   Notifications → Slack + Teams.
    
*   Insights → Total monthly savings.
    

⚙️ DAG Structure
----------------

*   **Task: track\_savings**
    
    *   Runs daily at **09:00 UTC**.
        
    *   Steps:
        
        1.  Query applied recommendations.
            
        2.  Compute before/after costs.
            
        3.  Insert into savings.
            
        4.  Update recommendation status.
            
        5.  Send notifications.
            

🛠️ Database Tables
-------------------

### recommendations

| Column             | Type      | Description                             |
|--------------------|-----------|-----------------------------------------|
| rec_id             | SERIAL PK | Recommendation ID                       |
| resource_id        | INT FK    | Target resource                         |
| rec_type           | VARCHAR   | Rightsize, Idle, etc.                   |
| recommended_config | JSONB     | Suggested change                        |
| status             | VARCHAR   | pending, applied, validated, no_savings |

### savings

| Column         | Type      | Description                 |
|----------------|-----------|-----------------------------|
| saving_id      | SERIAL PK | Unique savings record       |
| account_id     | INT FK    | Linked account              |
| resource_id    | INT FK    | Linked resource             |
| rec_id         | INT FK    | Linked recommendation       |
| implemented_at | TIMESTAMP | Date recommendation applied |
| actual_savings | NUMERIC   | Calculated savings          |
| currency       | VARCHAR   | USD (default)               |

🔍 Savings Calculation Logic
----------------------------

1.  **Before Applied**
    

```
SELECT SUM(cost_amount) 
FROM billing
WHERE resource_id = {rid}
  AND usage_date BETWEEN (applied_date - 30) AND applied_date;
```

1.  **After Applied**
    

```
SELECT SUM(cost_amount) 
FROM billing
WHERE resource_id = {rid}
  AND usage_date BETWEEN applied_date AND (applied_date + 30);
```

1.  **Savings**
    

```
savings = before - after (if > 0)
```

🔔 Notifications
----------------

### Slack

```
💰 Savings Tracker Results:
- Rec 45 on Resource i-12345: $120.00 → validated
- Rec 47 on Resource rds-789: $0.00 → no_savings
📊 Total Savings This Month: $120.00
```

### Teams

```
💰 Savings Tracker Results:
- Rec 45 (EC2): $120 validated
- Rec 47 (RDS): $0 no_savings
Total Savings: $120
```

📊 Example Scenarios
--------------------

### Case 1: EC2 Rightsizing

*   Before: $200/month
    
*   After: $100/month
    
*   Savings: $100
    
*   Status: validated
    

### Case 2: Lambda Inactivity

*   Before: $5/month
    
*   After: $5/month
    
*   Savings: $0
    
*   Status: no\_savings
    

✅ Key Benefits
--------------

*   Links **recommendations → real savings**.
    
*   Builds trust in automation.
    
*   Gives management **hard dollar value** of optimizations.
    
*   Drives **continuous improvement** in FinOps.
    

❓ Review Questions
------------------

1.  How does the tracker calculate **actual savings**?
    
2.  What happens if the recommendation doesn’t save money?
    
3.  Which table logs realized savings?
    
4.  How often does the DAG run?
    
5.  What type of notification is sent when savings are validated?