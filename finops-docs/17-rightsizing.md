📌 Overview
-----------

Rightsizing is the practice of analyzing resource utilization (CPU, memory, network, etc.) and comparing it against actual costs to **recommend optimal configurations**. The goal is to reduce waste by:

*   **Downsizing** over-provisioned instances or tasks.
    
*   **Terminating** idle resources.
    
*   **Resizing** to more cost-efficient types while maintaining performance.
    

This FinOps system integrates **metrics ingestion, AWS Pricing API, and recommendations logic** into a single automated DAG in Airflow.

🏗️ Workflow
------------

### 1\. Input Data

*   **Usage metrics** from CloudWatch (CPUUtilization, Memory, Lambda Duration, etc.) → stored in usage table.
    
*   **Billing data** from Cost Explorer → stored in billing table.
    
*   **Instance catalog** from AWS Pricing API → stored in instance\_catalog table (kept updated weekly).
    

### 2\. Analysis Process

The DAG (rightsizing) evaluates utilization trends for the last **14–30 days**:

*   **EC2** → CPU-based thresholds (<5% = idle, <20% = over-provisioned).
    
*   **ECS/EKS** → CPU & memory-based thresholds.
    
*   **Lambda** → duration and invocation count.
    
*   **Billing overlay** → potential savings computed with actual prices.
    

### 3\. Recommendations

*   **Idle Resource** → stop/terminate or scale to zero.
    
*   **Rightsizing** → suggest next smaller instance/task size, along with estimated monthly savings.
    
*   **Keep** → if utilization is within healthy range.
    

Recommendations are written to the recommendations table with:

*   rec\_type: idle / rightsize
    
*   current\_config: JSON snapshot of current state (e.g., avg\_cpu, instance\_type)
    
*   recommended\_config: JSON with target (e.g., new instance type, action)
    
*   estimated\_savings: numeric cost delta
    
*   status: pending → applied → validated/no\_savings
    

⚙️ DAG Structure
----------------

*   **Task: Analyze Rightsizing**
    
    *   Query usage metrics for EC2/ECS/EKS/Lambda.
        
    *   Join with resources to identify service & region.
        
    *   Query AWS Pricing API (EC2) or fallback to static rules (ECS/EKS/Lambda).
        
    *   Insert recommendation into DB.
        
*   **Schedule**: Daily at **04:00 UTC**Ensures recommendations are refreshed with latest metrics & pricing.
    

🧠 Technical Details
--------------------

### EC2 Rightsizing

1.  Query usage table for CPUUtilization (last 14 days).
    
2.  If <5% → recommend stop.
    
3.  If <20% → recommend smaller instance:
    
    *   Look up **next smaller size** from instance\_catalog.
        
    *   Fetch **price delta** using Pricing API.
        
    *   Store estimated savings as (old\_price - new\_price) \* 730.
        

### ECS/EKS Rightsizing

*   CPU & memory averages <30% → suggest smaller task size or node group scaling.
    
*   Idle (<5% both) → scale to zero.
    

### Lambda Rightsizing

*   Zero invocations → recommend deletion.
    
*   Duration >5 seconds avg → recommend memory increase (may improve efficiency).
    

🛠️ Database Tables
-------------------

### recommendations

| Column             | Type          | Description                   |
|--------------------|---------------|-------------------------------|
| rec_id             | SERIAL PK     | Recommendation ID             |
| resource_id        | FK(resources) | Target resource               |
| rec_type           | VARCHAR       | idle / rightsize              |
| current_config     | JSON          | Current metrics & config      |
| recommended_config | JSON          | Suggested action/size         |
| estimated_savings  | NUMERIC       | Monthly savings in USD        |
| currency           | VARCHAR       | Default: USD                  |
| status             | VARCHAR       | pending / applied / validated |
| created_at         | TIMESTAMP     | When detected                 |


📊 Example Recommendation
-------------------------

```
{
  "rec_id": 101,
  "resource_id": 55,
  "rec_type": "Rightsize",
  "current_config": {
    "avg_cpu": 14.2,
    "instance_type": "m5.xlarge",
    "service": "EC2"
  },
  "recommended_config": {
    "recommend": "m5.large"
  },
  "estimated_savings": 58.40,
  "currency": "USD",
  "status": "pending",
  "created_at": "2025-09-13T04:00:00Z"
}
```

🔔 Notifications
----------------

When new recommendations are generated:

*   **Slack & Teams** alerts are triggered via Webhooks.
    
*   Messages summarize idle/rightsizing opportunities and potential savings.
    

✅ Key Benefits
--------------

*   Continuous optimization of cloud footprint.
    
*   Uses **live AWS pricing** for accurate savings estimates.
    
*   Integrates with anomaly detection and savings tracker for closed-loop validation.
    
*   Reduces manual FinOps toil by automating rightsizing.
    

❓ Review Questions
------------------

1.  What three services are analyzed in the rightsizing DAG?
    
2.  How does the system determine the next smaller EC2 instance size?
    
3.  What role does the instance\_catalog table play?
    
4.  How are savings validated after recommendations are applied?
    
5.  Why is daily scheduling important for rightsizing tasks?